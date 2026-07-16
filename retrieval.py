import faiss

from config import VECTOR_DIM
from config import TOP_K

from embedding_service import embed_texts


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

    question_embedding = embed_texts([question])

    distances, indices = index.search(
        question_embedding,
        TOP_K
    )

    results = [
        knowledge[idx]
        for idx in indices[0]
    ]

    return results