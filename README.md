# 🚀 Build Your Own RAG

> A step-by-step journey of building a Retrieval-Augmented Generation (RAG) system from scratch using Python.

This repository documents my learning journey during my AI internship, where I progressively built a RAG pipeline from simple keyword search to semantic retrieval using Sentence Transformers and FAISS.

Instead of relying on high-level frameworks such as LangChain, every component is implemented manually to better understand how Retrieval-Augmented Generation (RAG) works under the hood.

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
    └── LLM Response
    │
Mini RAG V4 (Coming Soon)
    │
    ├── Embedding Cache
    ├── Modular Structure
    └── Engineering Refactor
```

---

# 🏗️ Project Workflow

```text
          User Question
                │
                ▼
      Sentence Embedding
                │
                ▼
        Vector Search (FAISS)
                │
                ▼
        Top-K Retrieval
                │
                ▼
        Prompt Builder
                │
                ▼
        Large Language Model
                │
                ▼
              Answer
```

---

# 🛠️ Tech Stack

- Python
- Sentence Transformers
- FAISS
- NumPy

---

# 🎯 Learning Objectives

Throughout this project, I aim to understand:

- How Retrieval works
- Why Embeddings are needed
- How FAISS performs similarity search
- How Prompt Engineering connects Retrieval and LLMs
- The difference between Embedding Models and Generation Models

---

# 🗺️ Project Roadmap

- ✅ Mini RAG V1 — Keyword Search
- ✅ Mini RAG V2 — Top-K Retrieval
- ✅ Mini RAG V3 — Sentence Embedding
- ✅ Mini RAG V3.5 — FAISS + Prompt Engineering
- ⏳ Mini RAG V4 — Engineering Refactor
- ⏳ FastAPI Integration
- ⏳ Ollama Support
- ⏳ AI Agent Workflow
- ⏳ Docker Deployment

---

# 💡 Why This Repository?

Many tutorials build RAG systems directly with frameworks such as LangChain or LlamaIndex.

In this repository, I intentionally rebuild each component from scratch to gain a deeper understanding of the complete RAG pipeline before using higher-level frameworks.

The goal is **not only to build a working RAG application, but also to understand why every component exists.**