# QAYBTA CUSUB: RAADINTA INTERNET-KA (Web Plagiarism Check)
import re
from urllib.parse import unquote
from concurrent.futures import ThreadPoolExecutor
import requests
from bs4 import BeautifulSoup
from preprocess import tokenize
from similarity import ngrams

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
N = 4              # weedh = 4 eray oo isku xigta
MAX_QUERIES = 5    # inta jeer internet-ka laga raadinayo
MAX_PAGES = 8      # inta bog ee la akhrinayo


def pick_queries(text):
    """Dooro weedho kala duwan oo qoraalka ka mid ah si loo raadiyo."""
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", text) if len(s.split()) >= 6]
    if not sentences:
        sentences = [text]
    step = max(1, len(sentences) // MAX_QUERIES)
    chosen = sentences[::step][:MAX_QUERIES]
    # 12-ka eray ee ugu horreeya, ku duub xaashiyo (exact phrase)
    return ['"' + " ".join(s.split()[:12]) + '"' for s in chosen]


def search_web(query, n=5):
    """Raadi internet-ka, soo celi liiska URL-ada."""
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
        return soup.get_text(" ")[:300000]
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
    urls = []
    for q in pick_queries(text):
        for u in search_web(q):
            if u not in urls:
                urls.append(u)
    urls = urls[:MAX_PAGES]
    with ThreadPoolExecutor(max_workers=4) as pool:  # bogagga si wada jir ah u akhri
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