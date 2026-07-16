from pathlib import Path


SUPPORTED_MARKDOWN_EXTENSIONS = {".md", ".markdown"}


def is_markdown_file(filename):
    return Path(filename).suffix.lower() in SUPPORTED_MARKDOWN_EXTENSIONS


def load_markdown(file_path):
    if not is_markdown_file(file_path):
        raise ValueError("Only Markdown files are supported in this ingestion phase.")

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()
