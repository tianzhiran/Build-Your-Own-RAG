from sentence_transformers import SentenceTransformer
import numpy as np
import os

from config import MODEL_NAME, CACHE_FILE


model = SentenceTransformer(MODEL_NAME)


def load_or_create_embeddings(knowledge):
    """
    Load cached embeddings if available,
    otherwise generate new embeddings.
    """

    pass