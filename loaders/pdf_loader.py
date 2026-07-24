from pathlib import Path


FILE_TYPE = "pdf"
SUPPORTED_EXTENSIONS = {".pdf"}


def supports(filename):
    return Path(filename).suffix.lower() in SUPPORTED_EXTENSIONS


def load_text(file_path):
    if not supports(file_path):
        raise ValueError("Only PDF files are supported by pdf_loader.")

    from pypdf import PdfReader

    reader = PdfReader(file_path)
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        page_text = page_text.strip()

        if page_text:
            pages.append(f"[Page {page_number}]\n{page_text}")

    if not pages:
        raise ValueError(
            "No extractable text found in PDF. "
            "Scanned PDFs need OCR and are not supported yet."
        )

    return "\n\n".join(pages)
