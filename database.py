import os
import sqlite3
import uuid
from datetime import datetime
from datetime import timezone

from config import DATABASE_FILE


DOCUMENT_STATUS_PENDING = "pending"
DOCUMENT_STATUS_PROCESSING = "processing"
DOCUMENT_STATUS_COMPLETED = "completed"
DOCUMENT_STATUS_FAILED = "failed"


def current_timestamp():
    return datetime.now(timezone.utc).isoformat()


def get_connection(db_path=DATABASE_FILE):
    db_dir = os.path.dirname(db_path)

    if db_dir:
        os.makedirs(db_dir, exist_ok=True)

    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def init_db(db_path=DATABASE_FILE):
    with get_connection(db_path) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                document_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                file_type TEXT NOT NULL,
                upload_time TEXT NOT NULL,
                status TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS chunks (
                chunk_id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                chunk_index INTEGER NOT NULL,
                chunk_text TEXT NOT NULL,
                embedding_ref TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (document_id) REFERENCES documents (document_id)
            )
            """
        )

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_history (
                chat_id TEXT PRIMARY KEY,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                timestamp TEXT NOT NULL
            )
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_chunks_document_id
            ON chunks (document_id)
            """
        )

        connection.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_chat_history_timestamp
            ON chat_history (timestamp)
            """
        )


def row_to_dict(row):
    return dict(row) if row else None


def create_document(
    filename,
    file_type,
    status=DOCUMENT_STATUS_PENDING,
    db_path=DATABASE_FILE
):
    document_id = str(uuid.uuid4())
    upload_time = current_timestamp()

    with get_connection(db_path) as connection:
        connection.execute(
            """
            INSERT INTO documents (
                document_id,
                filename,
                file_type,
                upload_time,
                status
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                document_id,
                filename,
                file_type,
                upload_time,
                status
            )
        )

    return document_id


def update_document_status(document_id, status, db_path=DATABASE_FILE):
    with get_connection(db_path) as connection:
        connection.execute(
            """
            UPDATE documents
            SET status = ?
            WHERE document_id = ?
            """,
            (
                status,
                document_id
            )
        )


def list_documents(db_path=DATABASE_FILE):
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """
            SELECT
                document_id,
                filename,
                file_type,
                upload_time,
                status
            FROM documents
            ORDER BY upload_time DESC
            """
        ).fetchall()

    return [row_to_dict(row) for row in rows]


def create_chunk(
    document_id,
    chunk_text,
    chunk_index,
    embedding_ref=None,
    db_path=DATABASE_FILE
):
    chunk_id = str(uuid.uuid4())
    created_at = current_timestamp()

    with get_connection(db_path) as connection:
        connection.execute(
            """
            INSERT INTO chunks (
                chunk_id,
                document_id,
                chunk_index,
                chunk_text,
                embedding_ref,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                chunk_id,
                document_id,
                chunk_index,
                chunk_text,
                embedding_ref,
                created_at
            )
        )

    return chunk_id


def list_chunks(document_id=None, db_path=DATABASE_FILE):
    with get_connection(db_path) as connection:
        if document_id:
            rows = connection.execute(
                """
                SELECT
                    chunk_id,
                    document_id,
                    chunk_index,
                    chunk_text,
                    embedding_ref,
                    created_at
                FROM chunks
                WHERE document_id = ?
                ORDER BY chunk_index ASC
                """,
                (document_id,)
            ).fetchall()
        else:
            rows = connection.execute(
                """
                SELECT
                    chunk_id,
                    document_id,
                    chunk_index,
                    chunk_text,
                    embedding_ref,
                    created_at
                FROM chunks
                ORDER BY created_at DESC
                """
            ).fetchall()

    return [row_to_dict(row) for row in rows]


def create_chat_history(question, answer, db_path=DATABASE_FILE):
    chat_id = str(uuid.uuid4())
    timestamp = current_timestamp()

    with get_connection(db_path) as connection:
        connection.execute(
            """
            INSERT INTO chat_history (
                chat_id,
                question,
                answer,
                timestamp
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                chat_id,
                question,
                answer,
                timestamp
            )
        )

    return chat_id


def list_chat_history(db_path=DATABASE_FILE):
    with get_connection(db_path) as connection:
        rows = connection.execute(
            """
            SELECT
                chat_id,
                question,
                answer,
                timestamp
            FROM chat_history
            ORDER BY timestamp DESC
            """
        ).fetchall()

    return [row_to_dict(row) for row in rows]


def update_chunk_embedding_ref(chunk_id, embedding_ref, db_path=DATABASE_FILE):
    with get_connection(db_path) as connection:
        connection.execute(
            """
            UPDATE chunks
            SET embedding_ref = ?
            WHERE chunk_id = ?
            """,
            (
                embedding_ref,
                chunk_id
            )
        )


def get_chunks_by_ids(chunk_ids, db_path=DATABASE_FILE):
    if not chunk_ids:
        return []

    placeholders = ", ".join(["?"] * len(chunk_ids))

    with get_connection(db_path) as connection:
        rows = connection.execute(
            f"""
            SELECT
                chunks.chunk_id,
                chunks.document_id,
                chunks.chunk_index,
                chunks.chunk_text,
                chunks.embedding_ref,
                chunks.created_at,
                documents.filename,
                documents.file_type
            FROM chunks
            JOIN documents
                ON chunks.document_id = documents.document_id
            WHERE chunks.chunk_id IN ({placeholders})
            """,
            chunk_ids
        ).fetchall()

    chunks_by_id = {
        row["chunk_id"]: row_to_dict(row)
        for row in rows
    }

    return [
        chunks_by_id[chunk_id]
        for chunk_id in chunk_ids
        if chunk_id in chunks_by_id
    ]

def get_document(document_id, db_path=DATABASE_FILE):
    with get_connection(db_path) as connection:
        row = connection.execute(
            """
            SELECT
                document_id,
                filename,
                file_type,
                upload_time,
                status
            FROM documents
            WHERE document_id = ?
            """,
            (document_id,)
        ).fetchone()

    return row_to_dict(row)


def delete_document(document_id, db_path=DATABASE_FILE):
    with get_connection(db_path) as connection:
        connection.execute(
            """
            DELETE FROM chunks
            WHERE document_id = ?
            """,
            (document_id,)
        )
        cursor = connection.execute(
            """
            DELETE FROM documents
            WHERE document_id = ?
            """,
            (document_id,)
        )

    return cursor.rowcount > 0
