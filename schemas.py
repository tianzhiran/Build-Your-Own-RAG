from dataclasses import dataclass
from typing import List


@dataclass
class RAGResponse:
    """
    Structured response returned by the RAG workflow.
    """

    answer: str
    contexts: List[str]
