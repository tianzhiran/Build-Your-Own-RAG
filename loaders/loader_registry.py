from loaders import markdown_loader


LOADERS = [
    markdown_loader
]


def get_loader(filename):
    for loader in LOADERS:
        if loader.supports(filename):
            return loader

    raise ValueError(
        "Unsupported file type. Supported file types: "
        f"{', '.join(get_supported_extensions())}."
    )


def get_supported_extensions():
    extensions = []

    for loader in LOADERS:
        extensions.extend(loader.SUPPORTED_EXTENSIONS)

    return sorted(extensions)


def get_file_type(filename):
    return get_loader(filename).FILE_TYPE


def is_supported_file(filename):
    try:
        get_loader(filename)
    except ValueError:
        return False

    return True


def load_document_text(file_path):
    loader = get_loader(file_path)

    return loader.load_text(file_path)
