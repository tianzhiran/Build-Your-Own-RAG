# 🚀 Build Your Own RAG

> A step-by-step journey of building a Retrieval-Augmented Generation (RAG) system from scratch using Python.

This repository documents my learning journey during my AI Software Engineering internship.

Instead of relying on high-level frameworks such as LangChain or LlamaIndex, every component is implemented manually to understand how Retrieval-Augmented Generation (RAG) works under the hood.

The project gradually evolves from a simple keyword search demo into a modular and engineering-oriented RAG system.

---

# 🏗️ System Architecture (V4)

```text
                User Question
                      │
                      ▼
             Load Knowledge Base
                      │
                      ▼
        Load / Create Embeddings
                      │
                      ▼
             Build FAISS Index
                      │
                      ▼
              Retrieve Top-K
                      │
                      ▼
              Prompt Builder
                      │
                      ▼
             Enterprise LLM API
                      │
                      ▼
                Generate Answer
```

---

# 📂 Project Structure

```text
build-your-own-rag/

├── main.py                 # Workflow Orchestration
├── config.py               # Project Configuration
├── utils.py                # Helper Functions
├── embedding.py            # Embedding & Cache
├── retrieval.py            # FAISS Retrieval
├── prompt_builder.py       # Prompt Construction
├── llm.py                  # LLM API Adapter
│
├── knowledge.txt           # Knowledge Base
│
├── cache/
│     embeddings.npy
│
└── README.md
```

---

# 📚 Learning Roadmap

```text
Mini RAG V1
│
├── Keyword Search
│
Mini RAG V2
│
├── Top-K Retrieval
│
Mini RAG V3
│
├── Sentence Embedding
│
Mini RAG V3.5
│
├── FAISS Vector Search
├── Prompt Construction
└── Enterprise LLM API
│
Mini RAG V4 ✅
│
├── Embedding Cache
├── Modular Architecture
├── Configuration Management
├── Retrieval Module
├── Prompt Builder
└── LLM Adapter
```

---

# 🔄 Workflow

```text
Knowledge Base

↓

Embedding Model

↓

Vector Embeddings

↓

FAISS Index

↓

User Question

↓

Question Embedding

↓

Similarity Search

↓

Top-K Knowledge

↓

Prompt Builder

↓

Large Language Model

↓

Answer
```

---

# 🛠️ Tech Stack

- Python
- Sentence Transformers
- FAISS
- NumPy
- OpenAI SDK (Enterprise API)
- Qwen LLM

---

# 🎯 What I Learned

Throughout this project, I explored:

- Tokenization
- Sentence Embeddings
- Vector Search
- FAISS Indexing
- Prompt Engineering
- Retrieval-Augmented Generation (RAG)
- Modular Software Architecture
- Configuration Management
- Enterprise LLM API Integration

Rather than simply building a working demo, the focus is on understanding why each component exists and how they work together.

---

# 🚀 Future Roadmap

- ✅ Mini RAG V1 — Keyword Search
- ✅ Mini RAG V2 — Top-K Retrieval
- ✅ Mini RAG V3 — Sentence Embedding
- ✅ Mini RAG V3.5 — FAISS + Enterprise LLM
- ✅ Mini RAG V4 — Engineering Refactor

Next Steps

- ⏳ FastAPI Backend
- ⏳ Docker Deployment
- ⏳ Ollama Local Models
- ⏳ Conversation Memory
- ⏳ Tool Calling
- ⏳ AI Agent Workflow

---

# 💡 Why This Repository?

The goal of this project is **not simply to build another RAG demo**.

Instead, I want to understand:

- Why Retrieval is needed
- Why Embeddings work
- Why FAISS is efficient
- Why Prompt Engineering matters
- How a production-ready AI application should be architected

This repository records my journey from learning AI fundamentals to building real-world AI applications.

---

# 🌐 FastAPI Backend

Run the backend service:

```bash
uvicorn api:app --reload
```

Health check:

```text
GET /health
```

Ask a RAG question:

```text
POST /ask
```

Request body:

```json
{
  "question": "Your question here"
}
```

Response body:

```json
{
  "answer": "Generated answer",
  "contexts": ["Retrieved context"]
}
```
