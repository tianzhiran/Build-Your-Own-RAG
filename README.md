# Communication Knowledge RAG Assistant

A lightweight enterprise-style RAG backend for communication-domain knowledge, evolved from the Mini RAG V4 project.

The current system supports:

- FastAPI backend
- Markdown document upload
- Text extraction and chunking
- SQLite document/chunk/chat storage
- SentenceTransformer embeddings
- FAISS vector storage
- RAG question answering over uploaded chunks
- Answer response with retrieved contexts and source metadata

> Current focus: backend RAG data flow first. Frontend comes after backend end-to-end testing is stable.

---

## 1. Current Architecture

```text
User / curl / Postman / future frontend
        ↓
FastAPI Backend
        ↓
Document Service ──────→ SQLite documents / chunks
        ↓                         ↓
Markdown Loader                  chunk metadata
        ↓                         ↓
Chunking                         embedding_ref
        ↓
Embedding Service
        ↓
FAISS Vector Store + vector_metadata.json
        ↓
RAGService
        ↓
Prompt Builder
        ↓
OpenAI-compatible LLM API
        ↓
Answer + Contexts + Sources
```

---

## 2. Current Project Structure

```text
Build-Your-Own-RAG/

├── api.py                    # FastAPI routes
├── main.py                   # CLI entrypoint
├── config.py                 # Project configuration
│
├── database.py               # SQLite schema and DB helpers
├── document_service.py       # Markdown upload → chunk → embed → vector store
├── chunking.py               # Paragraph-aware text chunking
│
├── loaders/
│   ├── __init__.py
│   └── markdown_loader.py    # Markdown file validation and loading
│
├── embedding_service.py      # embed_text / embed_texts wrapper
├── vector_store.py           # FAISS index + vector metadata mapping
├── rag_service.py            # Vector-backed RAG workflow
├── schemas.py                # RAG response dataclasses
│
├── prompt_builder.py         # Prompt construction
├── llm.py                    # OpenAI-compatible LLM adapter
│
├── embedding.py              # Legacy static embedding cache helper
├── retrieval.py              # Legacy static FAISS retrieval helper
├── utils.py                  # Legacy static knowledge loader
│
├── data/
│   └── knowledge.txt         # Legacy static knowledge file
│
├── storage/                  # Runtime-created local storage
│   ├── app.db
│   ├── faiss.index
│   ├── vector_metadata.json
│   └── uploads/
│
├── requirements.txt
└── README.md
```

---

## 3. What Can Run Now?

You can run the backend and test the full Markdown RAG flow from the command line.

You do **not** need a frontend yet.

Use one of these tools first:

- `curl`
- Postman
- VS Code REST Client
- FastAPI Swagger UI at `http://127.0.0.1:8000/docs`

Recommended testing order:

```text
1. Install dependencies
2. Start FastAPI
3. Check /health
4. Upload a Markdown file
5. List uploaded documents
6. Ask a question based on that Markdown file
7. Inspect answer + contexts + sources
```

---

## 4. Setup

### 4.1 Create and activate a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
```

On Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 4.2 Install dependencies

```bash
pip install -r requirements.txt
```

### 4.3 Check LLM configuration

The LLM client uses the OpenAI-compatible settings in `config.py`:

```text
API_KEY
BASE_URL
LLM_MODEL
```

Before running real `/ask` tests, make sure these settings are valid for your enterprise LLM API.

---

## 5. Start the Backend

```bash
uvicorn api:app --reload
```

Expected server URL:

```text
http://127.0.0.1:8000
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

---

## 6. Test Flow from Command Line

### 6.1 Health check

```bash
curl http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

---

### 6.2 Create a sample Markdown document

```bash
cat > otn_los_alarm.md <<'EOF_MD'
# OTN LOS Alarm Handling

LOS means Loss of Signal. It usually indicates that the optical receiver cannot detect a valid optical signal.

## Common Causes

- Fiber disconnected
- Optical module failure
- Incorrect fiber connection
- Low optical power
- Upstream transmission interruption

## Troubleshooting Steps

1. Check whether the fiber is connected correctly.
2. Check optical power on the receive side.
3. Verify whether the peer device is transmitting optical signal.
4. Replace the optical module if the power level is abnormal.
5. Check whether upstream equipment has alarms.
EOF_MD
```

---

### 6.3 Upload the Markdown document

```bash
curl -X POST http://127.0.0.1:8000/documents/upload \
  -F "file=@otn_los_alarm.md"
```

Expected response shape:

```json
{
  "document_id": "...",
  "filename": "otn_los_alarm.md",
  "file_type": "markdown",
  "status": "completed",
  "chunk_count": 1
}
```

What happens internally:

```text
Upload file
↓
Save to storage/uploads/
↓
Load Markdown text
↓
Chunk text
↓
Create SQLite document record
↓
Create SQLite chunk records
↓
Generate embeddings
↓
Store vectors in storage/faiss.index
↓
Store vector metadata in storage/vector_metadata.json
↓
Update chunk embedding_ref
```

---

### 6.4 List uploaded documents

```bash
curl http://127.0.0.1:8000/documents
```

Expected response shape:

```json
[
  {
    "document_id": "...",
    "filename": "otn_los_alarm.md",
    "file_type": "markdown",
    "upload_time": "...",
    "status": "completed"
  }
]
```

---

### 6.5 Ask a question based on uploaded knowledge

```bash
curl -X POST http://127.0.0.1:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question":"OTN设备出现LOS告警应该如何处理？"}'
```

Expected response shape:

```json
{
  "answer": "...",
  "contexts": [
    "retrieved chunk text"
  ],
  "sources": [
    {
      "document_id": "...",
      "chunk_id": "...",
      "filename": "otn_los_alarm.md",
      "distance": 0.0
    }
  ]
}
```

If no uploaded chunks are found in the vector store, the service returns:

```text
当前知识库没有找到相关信息.
```

---

## 7. Important Runtime Files

These files are created while running the backend:

```text
storage/app.db                  # SQLite database
storage/faiss.index             # FAISS vector index
storage/vector_metadata.json    # vector_index → chunk_id / document_id mapping
storage/uploads/                # uploaded Markdown files
```

If you want to reset local test data:

```bash
rm -rf storage/
```

Then restart the backend and upload documents again.

---

## 8. Current Data Flow

### 8.1 Upload flow

```text
POST /documents/upload
↓
document_service.ingest_markdown_upload
↓
save_uploaded_file
↓
load_markdown
↓
chunk_text
↓
create_document / create_chunk
↓
embed_texts
↓
vector_store.add_vectors
↓
update_chunk_embedding_ref
↓
return document_id + status + chunk_count
```

### 8.2 Ask flow

```text
POST /ask
↓
RAGService.ask
↓
embed_text(question)
↓
vector_store.search
↓
database.get_chunks_by_ids
↓
build_prompt(contexts, question)
↓
generate_answer(prompt)
↓
create_chat_history
↓
return answer + contexts + sources
```

---

## 9. Do I Need a Frontend Now?

Not yet.

Before building React, first verify the backend end-to-end:

```text
Markdown upload works
↓
SQLite records are created
↓
FAISS index is created
↓
Question retrieves uploaded chunks
↓
Answer includes sources
```

After this works reliably with `curl` or Swagger UI, then build the frontend.

Recommended frontend timing:

```text
Backend end-to-end verified
↓
Build Knowledge Management page
↓
Build Chat page
```

---

## 10. What Is Still Missing?

The current backend is a working MVP foundation, but it is not finished.

Important next improvements:

1. Move API secrets from `config.py` to environment variables.
2. Add a small automated test suite.
3. Improve chunking for communication manuals and alarm procedures.
4. Add source display improvements.
5. Add DOCX loader.
6. Add PDF loader.
7. Add React frontend.

---

## 11. Recommended Next Step

Do **not** start with a complex frontend yet.

Recommended next engineering step:

```text
Add a small test suite for the backend RAG pipeline.
```

Minimum useful tests:

```text
1. Markdown upload creates document + chunks
2. Chunk embedding_ref is updated after vector storage
3. Vector metadata maps vector_index to chunk_id/document_id
4. /ask returns answer + contexts + sources
5. Unknown knowledge returns 当前知识库没有找到相关信息.
```

After these pass, start the React frontend.

---

## 12. Delete an Uploaded Document

If you upload the wrong document version, remove it with:

```bash
curl -X DELETE http://127.0.0.1:8000/documents/{document_id}
```

Example:

```bash
curl -X DELETE http://127.0.0.1:8000/documents/your-document-id
```

Expected response shape:

```json
{
  "document_id": "your-document-id",
  "deleted": true,
  "removed_vectors": 3
}
```

What happens internally:

```text
DELETE /documents/{document_id}
↓
Remove matching vector metadata
↓
Rebuild FAISS index for remaining vectors
↓
Delete chunks from SQLite
↓
Delete document from SQLite
```

Use this when you upload the wrong file, for example an outdated `OTN_manual_v1.md`.
