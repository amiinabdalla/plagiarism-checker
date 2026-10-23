# QAYBTA 2: QORAALKA KA SOO SAARIDDA FAYLASHA (Text Extraction)
from docx import Document
from pypdf import PdfReader


def extract_text(file):
    """Fayl (.pdf / .docx / .txt) u beddel qoraal caadi ah."""
    name = file.filename.lower()
    if name.endswith(".pdf"):
        reader = PdfReader(file.stream)
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    if name.endswith(".docx"):
        doc = Document(file.stream)
        return "\n".join(p.text for p in doc.paragraphs)
    return file.read().decode("utf-8", errors="ignore")  # .txt
