from pathlib import Path

from pypdf import PdfReader

from app.core.config import settings


def decode_text_bytes(content: bytes) -> str:
    for encoding in ("utf-8", "latin-1"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError("Could not decode text file contents.")


def extract_text_from_pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    pages = [(page.extract_text() or "").strip() for page in reader.pages]
    text = "\n".join(page for page in pages if page)
    if not text.strip():
        raise ValueError("No readable text was found in the PDF.")
    return text


def extract_text_from_file(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".pdf":
        return extract_text_from_pdf(path)
    if suffix in {".txt", ".md"}:
        return decode_text_bytes(path.read_bytes()).strip()
    raise ValueError("Unsupported file type for text extraction.")


def validate_extracted_text(text: str) -> str:
    cleaned = text.strip()
    if not cleaned:
        raise ValueError("Extracted text is empty.")
    if len(cleaned.encode("utf-8")) > settings.MAX_UPLOAD_SIZE_BYTES * 2:
        raise ValueError("Extracted text is unexpectedly large.")
    return cleaned
