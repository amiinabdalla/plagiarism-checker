# QAYBTA 1: NADIINTA QORAALKA (Text Preprocessing)
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Soo dejiso liiska stop words (mar keliya ayuu soo dejisanayaa)
try:
    stopwords.words("english")
except LookupError:
    nltk.download("stopwords")

# Erayada aan muhiimka ahayn: Ingiriis + Soomaali
SOMALI_STOP = {"iyo", "oo", "ee", "ku", "ka", "u", "la", "waa", "ayaa", "uu", "ay", "aan", "ah", "in", "ma", "si"}
STOP = set(stopwords.words("english")) | SOMALI_STOP

stemmer = PorterStemmer()  # "running" -> "run"


def tokenize(text):
    """Qoraalka u beddel xarfo yaryar, kadibna u kala qaybi eray-eray."""
    return re.findall(r"\w+", text.lower())


def clean_words(text):
    """Tokenize + ka saar stop words + stemming."""
    return [stemmer.stem(w) for w in tokenize(text) if w not in STOP]
