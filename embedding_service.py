from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL


# Load embedding model once and reuse it across document and query embedding.
model = SentenceTransformer(EMBEDDING_MODEL)


def embed_text(text):
    """
    Generate one embedding vector for a single text input.
    """

    return model.encode(
        text,
        convert_to_numpy=True
    )


def embed_texts(texts):
    """
    Generate embedding vectors for multiple text inputs.
    """

    return model.encode(
        texts,
        convert_to_numpy=True
    )
