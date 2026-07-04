"""
PDF -> raw text extraction. Kept isolated so the extraction library
can be swapped (pypdf -> pdfplumber -> OCR pipeline) without touching routers.
"""
from pypdf import PdfReader


def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    pages = [page.extract_text() or "" for page in reader.pages]
    text = "\n\n".join(pages).strip()
    if not text:
        raise ValueError("No extractable text found in PDF (it may be a scanned image).")
    return text
