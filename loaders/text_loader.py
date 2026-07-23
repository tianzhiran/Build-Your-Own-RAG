from pathlib import Path


FILE_TYPE = "text"
SUPPORTED_EXTENSIONS = {".txt"}


def supports(filename):
    return Path(filename).suffix.lower() in SUPPORTED_EXTENSIONS


def load_text(file_path):
    if not supports(file_path):
        raise ValueError("Only TXT files are supported by text_loader.")

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()
