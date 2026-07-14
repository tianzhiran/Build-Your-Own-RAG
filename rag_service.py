from embedding import load_or_create_embeddings
from retrieval import build_index
from retrieval import retrieve
from prompt_builder import build_prompt
from llm import generate_answer
from utils import load_knowledge
from schemas import RAGResponse


class RAGService:
    """
    Reusable RAG workflow service.
    """

    def __init__(self):
        self.knowledge = load_knowledge()
        self.embeddings = load_or_create_embeddings(self.knowledge)
        self.index = build_index(self.embeddings)

    def ask(self, question):
        """
        Answer a user question using the RAG pipeline.
        """

        contexts = retrieve(
            question,
            self.index,
            self.knowledge
        )

        prompt = build_prompt(
            contexts,
            question
        )

        answer = generate_answer(prompt)

        return RAGResponse(
            answer=answer,
            contexts=contexts
        )
