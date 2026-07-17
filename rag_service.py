from database import create_chat_history
from database import get_chunks_by_ids
from database import init_db
from embedding_service import embed_text
from llm import generate_answer
from prompt_builder import build_prompt
from schemas import RAGResponse
from schemas import RAGSource
from vector_store import search


UNKNOWN_KNOWLEDGE_ANSWER = "当前知识库没有找到相关信息."


class RAGService:
    """
    Reusable RAG workflow service backed by uploaded document chunks.
    """

    def __init__(self):
        init_db()

    def ask(self, question):
        """
        Answer a user question using SQLite chunks and FAISS retrieval.
        """

        question_embedding = embed_text(question)

        search_results = search(question_embedding)
        print(f"[Retrieval] Retrieved {len(search_results)} chunks")

        chunk_ids = [
            result["chunk_id"]
            for result in search_results
        ]
        chunks = get_chunks_by_ids(chunk_ids)

        if not chunks:
            create_chat_history(question, UNKNOWN_KNOWLEDGE_ANSWER)

            return RAGResponse(
                answer=UNKNOWN_KNOWLEDGE_ANSWER,
                contexts=[],
                sources=[]
            )

        contexts = [
            chunk["chunk_text"]
            for chunk in chunks
        ]
        distance_by_chunk_id = {
            result["chunk_id"]: result["distance"]
            for result in search_results
        }
        sources = [
            RAGSource(
                document_id=chunk["document_id"],
                chunk_id=chunk["chunk_id"],
                filename=chunk["filename"],
                distance=distance_by_chunk_id[chunk["chunk_id"]]
            )
            for chunk in chunks
        ]

        prompt = build_prompt(
            contexts,
            question
        )

        print("[LLM] Generating response")
        answer = generate_answer(prompt)

        create_chat_history(question, answer)

        return RAGResponse(
            answer=answer,
            contexts=contexts,
            sources=sources
        )
