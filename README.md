# Build Your Own RAG

> Build a Retrieval-Augmented Generation (RAG) system from scratch.

This repository documents my learning journey during my AI internship, where I progressively built a RAG pipeline from keyword search to semantic retrieval using embeddings and FAISS.

Rather than relying on high-level frameworks such as LangChain, each component is implemented manually to better understand how RAG works internally.

> Learning Roadmap

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
├── Embedding
│
Mini RAG V3.5
│
├── FAISS
│
├── Prompt
│
└── LLM

>Project Workflow

Question
        │
        ▼
Embedding
        │
        ▼
Vector Search
        │
        ▼
Top-K Retrieval
        │
        ▼
Prompt Builder
        │
        ▼
LLM
        │
        ▼
Answer

## Roadmap

- [x] Mini RAG V1 - Keyword Search
- [x] Mini RAG V2 - Top-K Retrieval
- [x] Mini RAG V3 - Sentence Embedding
- [x] Mini RAG V3.5 - FAISS + Prompt
- [ ] Mini RAG V4 - Engineering Refactor
- [ ] FastAPI Integration
- [ ] Ollama Support
- [ ] Agent Workflow