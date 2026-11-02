# QAYBTA 1: NADIINTA QORAALKA (Text Preprocessing)
import re
from nltk.stem import PorterStemmer
# CHANGED [Bug 2]: stop words waxay hadda ka yimaadaan scikit-learn, download looma baahna
# (hore waxaa loo isticmaali jiray nltk.download, kaas oo app-ka ka joojin jiray inuu furmo).
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

# Erayada aan muhiimka ahayn: Ingiriis + Soomaali
SOMALI_STOP = {"iyo", "oo", "ee", "ku", "ka", "u", "la", "waa", "ayaa", "uu", "ay", "aan", "ah", "in", "ma", "si"}
STOP = set(ENGLISH_STOP_WORDS) | SOMALI_STOP

stemmer = PorterStemmer()  # "running" -> "run" (Ingiriis oo keliya)


def tokenize(text):
    """Qoraalka u beddel xarfo yaryar, kadibna u kala qaybi eray-eray."""
    return re.findall(r"\w+", text.lower())


def clean_words(text):
    """Tokenize + ka saar stop words + stemming."""
    return [stemmer.stem(w) for w in tokenize(text) if w not in STOP]
