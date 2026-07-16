from dataclasses import dataclass
from typing import List


@dataclass
class RAGSource:
    """
    Source chunk metadata used to explain a RAG answer.
    """

    document_id: str
    chunk_id: str
    filename: str
    distance: float


@dataclass
class RAGResponse:
    """
    Structured response returned by the RAG workflow.
    """

    answer: str
    contexts: List[str]
    sources: List[RAGSource]
