"""
Mini RAG V4 Configuration
"""

# ==========================
# Embedding
# ==========================

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ==========================
# Retrieval
# ==========================

VECTOR_DIM = 384
TOP_K = 2

# ==========================
# Files
# ==========================

KNOWLEDGE_FILE = "data/knowledge.txt"
CACHE_FILE = "cache/embeddings.npy"
DATABASE_FILE = "storage/app.db"
UPLOAD_DIR = "storage/uploads"

# ==========================
# LLM
# ==========================

API_KEY = "ecbbdbfb23fc48c81e8096dd23cc2003:YmMyNjRkMTBjNGQ1NDFlYjdjMTEwODk1"

BASE_URL = "https://maas-api.cn-huabei-1.xf-yun.com/v2"

LLM_MODEL = "xop3qwen1b7"