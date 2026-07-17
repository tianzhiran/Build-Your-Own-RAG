from fastapi import FastAPI
from fastapi import File
from fastapi import HTTPException
from fastapi import UploadFile
from pydantic import BaseModel

from document_service import delete_document_by_id
from document_service import get_documents
from document_service import ingest_markdown_upload


app = FastAPI(title="Mini RAG Backend")

rag_service = None


class AskRequest(BaseModel):
    question: str


class SourceResponse(BaseModel):
    document_id: str
    chunk_id: str
    filename: str
    distance: float


class AskResponse(BaseModel):
    answer: str
    contexts: list[str]
    sources: list[SourceResponse]


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    file_type: str
    status: str
    chunk_count: int


class DocumentRecord(BaseModel):
    document_id: str
    filename: str
    file_type: str
    upload_time: str
    status: str


class DocumentDeleteResponse(BaseModel):
    document_id: str
    deleted: bool
    removed_vectors: int


def get_rag_service():
    global rag_service

    if rag_service is None:
        from rag_service import RAGService

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
        contexts=response.contexts,
        sources=[
            SourceResponse(
                document_id=source.document_id,
                chunk_id=source.chunk_id,
                filename=source.filename,
                distance=source.distance
            )
            for source in response.sources
        ]
    )


@app.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a filename.")

    content = await file.read()

    try:
        result = ingest_markdown_upload(file.filename, content)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error))

    return DocumentUploadResponse(**result)


@app.get("/documents", response_model=list[DocumentRecord])
def list_uploaded_documents():
    return [
        DocumentRecord(**document)
        for document in get_documents()
    ]


@app.delete("/documents/{document_id}", response_model=DocumentDeleteResponse)
def delete_uploaded_document(document_id: str):
    try:
        result = delete_document_by_id(document_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))

    return DocumentDeleteResponse(**result)
