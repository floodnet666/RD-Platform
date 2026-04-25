import os
from backend.vector_db import VectorDB
from sentence_transformers import SentenceTransformer

# Fix [HIGH-02]: Singleton pattern to ensure single connection and shared locks
# Localização fora do volume montado para evitar 'disk I/O error' no Docker/Windows
DB_PATH = "/app/data/rag_storage.db"
MODEL_PATH = os.getenv("EMBEDDING_MODEL_PATH", "all-MiniLM-L6-v2")

# Garantir que a pasta de dados existe (dentro do container)
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

print(f"[DATABASE] Inicializando Singleton VectorDB em {DB_PATH}...")
db = VectorDB(DB_PATH)

print(f"[DATABASE] Inicializando Singleton SentenceTransformer...")
embed_model = SentenceTransformer(MODEL_PATH)
