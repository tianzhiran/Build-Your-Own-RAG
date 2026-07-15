from fastapi import FastAPI
from pydantic import BaseModel

from rag_service import RAGService


app = FastAPI(title="Mini RAG Backend")

rag_service = None


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    answer: str
    contexts: list[str]


def get_rag_service():
    global rag_service

    if rag_service is None:
        rag_service = RAGService()

    return rag_service


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    response = get_rag_service().ask(request.question)

    return AskResponse(
        answer=response.answer,
        contexts=response.contexts
    )
