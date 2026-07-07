"""Ingest a contract from .docx or .pdf into a list of paragraphs."""
import re
from pathlib import Path


def read_docx(path):
    from docx import Document
    doc = Document(str(path))
    return [p.text.strip() for p in doc.paragraphs if p.text.strip()]


def read_pdf(path):
    """Extract text from a PDF and re-segment into paragraphs.

    PDF extraction loses paragraph structure, so we re-split on numbered
    clause headings ("1. Heading." ...) which our contract population uses.
    """
    from pypdf import PdfReader
    reader = PdfReader(str(path))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    text = re.sub(r"\s+", " ", text).strip()
    # Split before "N. " clause markers and before the signature block.
    parts = re.split(r"(?=(?:\s|^)\d{1,2}\.\s+[A-Z])", text)
    paras = []
    for part in parts:
        part = part.strip()
        if not part:
            continue
        sig_split = re.split(r"(?=IN WITNESS WHEREOF)", part)
        paras.extend(s.strip() for s in sig_split if s.strip())
    return paras


def load_contract(path):
    path = Path(path)
    if path.suffix.lower() == ".docx":
        return read_docx(path), "docx"
    if path.suffix.lower() == ".pdf":
        return read_pdf(path), "pdf"
    raise ValueError(f"Unsupported file type: {path.suffix} (use .docx or .pdf)")
