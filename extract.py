# QAYBTA 2: QORAALKA KA SOO SAARIDDA FAYLASHA (Text Extraction)
from docx import Document
from pypdf import PdfReader


def extract_text(file):
    """Fayl (.pdf / .docx / .txt) u beddel qoraal caadi ah. Haddii uu fashilmo, wuxuu soo celiyaa ''."""
    name = file.filename.lower()
    try:  # CHANGED [Bug 7]: fayl jilicsan ama scan ah ma jabiyo app-ka; app.py ayaa fariin cad muujinaya
        if name.endswith(".pdf"):
            reader = PdfReader(file.stream)
            return "\n".join((page.extract_text() or "") for page in reader.pages)
        if name.endswith(".docx"):
            doc = Document(file.stream)
            return "\n".join(p.text for p in doc.paragraphs)
        return file.read().decode("utf-8", errors="ignore")  # .txt
    except Exception:
        return ""
