import os
import uuid
from pathlib import Path

from chunking import chunk_text
from config import DATABASE_FILE
from config import UPLOAD_DIR
from database import DOCUMENT_STATUS_COMPLETED
from database import DOCUMENT_STATUS_FAILED
from database import DOCUMENT_STATUS_PROCESSING
from database import create_chunk
from database import create_document
from database import init_db
from database import list_documents
from database import update_chunk_embedding_ref
from database import update_document_processing_result
from loaders.markdown_loader import is_markdown_file
from loaders.markdown_loader import load_markdown


FILE_TYPE_MARKDOWN = "markdown"


def ensure_upload_dir(upload_dir=UPLOAD_DIR):
    os.makedirs(upload_dir, exist_ok=True)


def build_stored_filename(filename):
    safe_name = Path(filename).name
    return f"{uuid.uuid4()}_{safe_name}"


def save_uploaded_file(filename, content, upload_dir=UPLOAD_DIR):
    ensure_upload_dir(upload_dir)

    stored_filename = build_stored_filename(filename)
    file_path = os.path.join(upload_dir, stored_filename)

    with open(file_path, "wb") as file:
        file.write(content)

    return file_path


def ingest_markdown_file(
    file_path,
    original_filename=None,
    db_path=DATABASE_FILE,
    chunk_size=800
):
    if not is_markdown_file(file_path):
        raise ValueError("Only Markdown files are supported in this ingestion phase.")

    init_db(db_path)

    filename = original_filename or Path(file_path).name
    document_id = create_document(
        filename,
        FILE_TYPE_MARKDOWN,
        stored_filename=Path(file_path).name,
        file_path=file_path,
        status=DOCUMENT_STATUS_PROCESSING,
        db_path=db_path
    )

    try:
        text = load_markdown(file_path)
        print(f"[Document] Loaded {filename}")

        chunks = chunk_text(text, chunk_size=chunk_size)
        print(f"[Chunk] Created {len(chunks)} chunks")

        chunk_records = []

        for chunk_index, chunk in enumerate(chunks):
            chunk_id = create_chunk(
                document_id,
                chunk,
                chunk_index,
                embedding_ref=None,
                db_path=db_path
            )
            chunk_records.append(
                {
                    "chunk_id": chunk_id,
                    "document_id": document_id
                }
            )

        if chunks:
            from embedding_service import embed_texts
            from vector_store import add_vectors

            embeddings = embed_texts(chunks)
            print("[Embedding] Generated vectors")

            vector_metadata = add_vectors(embeddings, chunk_records)
            print("[VectorStore] Stored vectors")

            for item in vector_metadata:
                update_chunk_embedding_ref(
                    item["chunk_id"],
                    f"faiss:{item['vector_index']}",
                    db_path=db_path
                )

        update_document_processing_result(
            document_id,
            DOCUMENT_STATUS_COMPLETED,
            chunk_count=len(chunks),
            error_message=None,
            db_path=db_path
        )
        print(f"[Document] Completed {filename}")

        return {
            "document_id": document_id,
            "filename": filename,
            "stored_filename": Path(file_path).name,
            "file_type": FILE_TYPE_MARKDOWN,
            "file_path": file_path,
            "status": DOCUMENT_STATUS_COMPLETED,
            "chunk_count": len(chunks),
            "error_message": None
        }

    except Exception as error:
        print(f"[Document] Failed {filename}")
        update_document_processing_result(
            document_id,
            DOCUMENT_STATUS_FAILED,
            error_message=str(error),
            db_path=db_path
        )
        raise


def ingest_markdown_upload(
    filename,
    content,
    db_path=DATABASE_FILE,
    upload_dir=UPLOAD_DIR,
    chunk_size=800
):
    if not is_markdown_file(filename):
        raise ValueError("Only Markdown files are supported in this ingestion phase.")

    file_path = save_uploaded_file(filename, content, upload_dir=upload_dir)

    return ingest_markdown_file(
        file_path,
        original_filename=filename,
        db_path=db_path,
        chunk_size=chunk_size
    )


def get_documents(db_path=DATABASE_FILE):
    init_db(db_path)

    return list_documents(db_path=db_path)


def delete_document_by_id(document_id, db_path=DATABASE_FILE):
    from database import delete_document
    from database import get_document
    from vector_store import remove_document_vectors

    init_db(db_path)

    document = get_document(document_id, db_path=db_path)

    if not document:
        raise ValueError("Document not found.")

    removed_vectors = remove_document_vectors(document_id)
    deleted = delete_document(document_id, db_path=db_path)

    return {
        "document_id": document_id,
        "deleted": deleted,
        "removed_vectors": removed_vectors
    }
