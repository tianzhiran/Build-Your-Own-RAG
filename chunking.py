
def split_long_text(text, chunk_size):
    return [
        text[index:index + chunk_size]
        for index in range(0, len(text), chunk_size)
    ]


def chunk_text(text, chunk_size=800):
    """
    Split extracted document text into simple paragraph-aware chunks.
    """

    paragraphs = [
        paragraph.strip()
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]

    chunks = []
    current_chunk = ""

    for paragraph in paragraphs:
        if len(paragraph) > chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = ""

            chunks.extend(split_long_text(paragraph, chunk_size))
            continue

        candidate = f"{current_chunk}\n\n{paragraph}" if current_chunk else paragraph

        if len(candidate) <= chunk_size:
            current_chunk = candidate
        else:
            chunks.append(current_chunk.strip())
            current_chunk = paragraph

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks
