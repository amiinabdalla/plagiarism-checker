# QAYBTA 3: XISAABINTA IS-EKAANSHAHA (Similarity Algorithms)
import re
from html import escape
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from preprocess import clean_words, tokenize


def cosine_score(a, b):
    """TF-IDF + Cosine Similarity. Natiijo: 0 ilaa 1."""
    wa, wb = " ".join(clean_words(a)), " ".join(clean_words(b))
    if not wa or not wb:
        return 0.0
    matrix = TfidfVectorizer().fit_transform([wa, wb])  # qoraal -> lambaro
    return float(cosine_similarity(matrix[0], matrix[1])[0][0])


def jaccard_score(a, b):
    """Erayada wadajirka ah / dhammaan erayada kala duwan."""
    sa, sb = set(clean_words(a)), set(clean_words(b))
    union = sa | sb
    return len(sa & sb) / len(union) if union else 0.0


def ngrams(words, n=3):
    """Kooxo ka kooban n eray oo isku xigta (tusaale n=3)."""
    return [" ".join(words[i:i + n]) for i in range(len(words) - n + 1)]


def shared_ngrams(a, b, n=3):
    """3-eray ee labada qoraal ku jira."""
    return set(ngrams(tokenize(a), n)) & set(ngrams(tokenize(b), n))


def overlap_score(a, b, n=3):
    """Boqolkiiba intee ka mid ah 3-erayda A ayaa ku jira B."""
    ga = ngrams(tokenize(a), n)
    return len([g for g in ga if g in set(ngrams(tokenize(b), n))]) / len(ga) if ga else 0.0


def highlight(text, shared, n=3):
    """Qoraalka ku celi isagoo weedhaha la koobiyeeyay ku duuban <mark>."""
    tokens = [(m.group().lower(), m.start(), m.end()) for m in re.finditer(r"\w+", text)]
    flags = [False] * len(tokens)
    for i in range(len(tokens) - n + 1):
        if " ".join(t[0] for t in tokens[i:i + n]) in shared:
            for k in range(n):
                flags[i + k] = True
    out, pos, i = "", 0, 0
    while i < len(tokens):
        if flags[i]:
            j = i
            while j + 1 < len(tokens) and flags[j + 1]:
                j += 1
            out += escape(text[pos:tokens[i][1]]) + "<mark>" + escape(text[tokens[i][1]:tokens[j][2]]) + "</mark>"
            pos = tokens[j][2]
            i = j + 1
        else:
            i += 1
    return out + escape(text[pos:])
