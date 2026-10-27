# QAYBTA CUSUB: RAADINTA INTERNET-KA (Web Plagiarism Check)
import re
from urllib.parse import unquote, quote
from concurrent.futures import ThreadPoolExecutor
from itertools import zip_longest
import requests
from bs4 import BeautifulSoup
from preprocess import tokenize
from similarity import ngrams

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
N = 4              # weedh = 4 eray oo isku xigta
MAX_QUERIES = 5    # inta jeer internet-ka laga raadinayo
MAX_PAGES = 10     # inta bog ee la akhrinayo
REF = re.compile(r"\[[^\]]{1,20}\]")  # calaamadaha tixraaca: [1], [A], [citation needed]


def strip_refs(text):
    """Ka saar calaamadaha tixraaca ee Wikipedia ([1], [A]) si 4-erayada isku xigta aysan u go'in."""
    return REF.sub(" ", text)


def pick_queries(text):
    """Dooro weedho qoraal dhab ah (ma aha shax/infobox) oo la raadiyo."""
    parts = [p.strip() for p in re.split(r"(?<=[.!?])\s+|\n+", text) if p.strip()]

    def is_prose(p):
        words = p.split()
        digits = sum(c.isdigit() for c in p)
        return len(words) >= 10 and "\t" not in p and digits / max(len(p), 1) < 0.15

    sentences = [p for p in parts if is_prose(p)]
    if not sentences:
        sentences = [p for p in parts if len(p.split()) >= 6] or [text]
    step = max(1, len(sentences) // MAX_QUERIES)
    chosen = sentences[::step][:MAX_QUERIES]
    return [" ".join(p.split()[:12]) for p in chosen]


def search_wikipedia(query, n=2):
    """Raadi Wikipedia si toos ah (API rasmi ah, deggan)."""
    try:
        r = requests.get("https://en.wikipedia.org/w/api.php", headers=HEADERS, timeout=8,
                         params={"action": "query", "list": "search", "srsearch": query,
                                 "srlimit": n, "format": "json"})
        return ["https://en.wikipedia.org/wiki/" + quote(it["title"].replace(" ", "_"))
                for it in r.json()["query"]["search"]]
    except Exception:
        return []


def search_web(query):
    """Wikipedia + DuckDuckGo."""
    return search_wikipedia(query) + search_ddg('"' + query + '"')


def search_ddg(query, n=5):
    """Raadi DuckDuckGo, soo celi liiska URL-ada."""
    try:  # Habka 1: maktabadda ddgs
        from ddgs import DDGS
        results = DDGS().text(query, max_results=n)
        urls = [r["href"] for r in results if r.get("href")]
        if urls:
            return urls
    except Exception:
        pass
    try:  # Habka 2: DuckDuckGo HTML (haddii ddgs shaqayn waayo)
        r = requests.post("https://html.duckduckgo.com/html/", data={"q": query}, headers=HEADERS, timeout=10)
        urls = []
        for a in BeautifulSoup(r.text, "html.parser").select("a.result__a"):
            href = a.get("href", "")
            m = re.search(r"uddg=([^&]+)", href)
            href = unquote(m.group(1)) if m else href
            if href.startswith("http"):
                urls.append(href)
        return urls[:n]
    except Exception:
        return []


def fetch_text(url):
    """Soo qaado qoraalka bogga web-ka."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=8)
        if "text/html" not in r.headers.get("Content-Type", ""):
            return ""
        soup = BeautifulSoup(r.text, "html.parser")
        for tag in soup(["script", "style", "nav", "footer"]):
            tag.decompose()
        return strip_refs(soup.get_text(" "))[:300000]
    except Exception:
        return ""


def matches(mine, other_text):
    """Kooxaha 4-eray ee qoraalkaaga ku jira qoraalka kale."""
    other = set(ngrams(tokenize(other_text), N))
    return {g for g in mine if g in other}


def check_text(text, local_docs):
    """Hubi qoraalka: database-ka hore + internet-ka."""
    mine = ngrams(tokenize(text), N)
    if not mine:
        return None
    sources, shared_all = [], set()

    def add(label, url, hit):
        score = sum(1 for g in mine if g in hit) / len(mine)
        if score > 0.02:  # ka dhaaf is-ekaansho aad u yar
            sources.append({"label": label, "url": url, "score": round(score * 100, 1)})
            shared_all.update(hit)

    # 1) Qoraalladii hore loo hubiyay (database)
    for title, created, doc in local_docs:
        add("Database: " + title + " (" + created + ")", "", matches(mine, doc))

    # 2) Internet
    queries = pick_queries(text)
    with ThreadPoolExecutor(max_workers=4) as pool:  # raadinta iyo akhrinta si wada jir ah
        found = list(pool.map(search_web, queries))
        urls = []
        for group in zip_longest(*found):  # weedh walba natiijo ka qaado (isku-beddel)
            for u in group:
                if u and u not in urls:
                    urls.append(u)
        urls = urls[:MAX_PAGES]
        pages = list(pool.map(fetch_text, urls))
    for u, page in zip(urls, pages):
        if page:
            add(u, u, matches(mine, page))

    pct = round(sum(1 for g in mine if g in shared_all) / len(mine) * 100, 1)
    sources.sort(key=lambda s: s["score"], reverse=True)
    return {"pct": pct, "sources": sources, "shared": shared_all, "n": N, "pages_checked": len(urls)}


def verdict(pct):
    if pct < 15:
        return "Original text: no copied content found"
    if pct < 40:
        return "Some parts may have been copied"
    return "Plagiarized: copied content found"
