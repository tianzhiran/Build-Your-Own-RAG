import os
import numpy as np

from sentence_transformers import SentenceTransformer

from config import EMBEDDING_MODEL
from config import CACHE_FILE


# Load embedding model only once
model = SentenceTransformer(EMBEDDING_MODEL)


def create_embeddings(knowledge):
    """
    Generate sentence embeddings for the knowledge base.

    Args:
        knowledge (list[str]): List of knowledge documents.

    Returns:
        numpy.ndarray: Sentence embeddings.
    """

    print("[Embedding] Creating embeddings...")

    embeddings = model.encode(
        knowledge,
        convert_to_numpy=True
    )

    print(f"[Embedding] Shape: {embeddings.shape}")

    return embeddings


def save_embeddings(embeddings):
    """
    Save embeddings to local cache.
    """

    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)

    np.save(CACHE_FILE, embeddings)

    print("[Embedding] Cache saved.")


def load_embeddings():
    """
    Load cached embeddings.
    """

    print("[Embedding] Loading cached embeddings...")

    embeddings = np.load(CACHE_FILE)

    print(f"[Embedding] Shape: {embeddings.shape}")

    return embeddings


def load_or_create_embeddings(knowledge):
    """
    Load embeddings from cache.
    If cache does not exist (or is broken),
    create new embeddings.
    """

    if os.path.exists(CACHE_FILE):

        try:
            return load_embeddings()

        except Exception:
            print("[Embedding] Cache corrupted.")
            print("[Embedding] Rebuilding cache...")

    embeddings = create_embeddings(knowledge)

    save_embeddings(embeddings)

    return embeddings