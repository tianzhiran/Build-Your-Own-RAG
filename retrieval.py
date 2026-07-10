import faiss

from config import VECTOR_DIM
from config import TOP_K

from embedding import model


def build_index(embeddings):
    """
    Build FAISS index.
    """

    index = faiss.IndexFlatL2(VECTOR_DIM)

    index.add(embeddings)

    print(f"[Retrieval] Indexed {index.ntotal} documents.")

    return index


def retrieve(question, index, knowledge):
    """
    Retrieve Top-K knowledge.
    """

    question_embedding = model.encode(
        [question],
        convert_to_numpy=True
    )

    distances, indices = index.search(
        question_embedding,
        TOP_K
    )

    results = [
        knowledge[idx]
        for idx in indices[0]
    ]

    return results