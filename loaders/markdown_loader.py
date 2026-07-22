from pathlib import Path


FILE_TYPE = "markdown"
SUPPORTED_EXTENSIONS = {".md", ".markdown"}
SUPPORTED_MARKDOWN_EXTENSIONS = SUPPORTED_EXTENSIONS


def supports(filename):
    return Path(filename).suffix.lower() in SUPPORTED_EXTENSIONS


def load_text(file_path):
    if not supports(file_path):
        raise ValueError("Only Markdown files are supported by markdown_loader.")

    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


# Backward-compatible helpers used by older callers/tests.
def is_markdown_file(filename):
    return supports(filename)


def load_markdown(file_path):
    return load_text(file_path)
