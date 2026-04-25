import os
import sys

# Adiciona o caminho do projeto para importar os módulos internos
sys.path.append("/app/src")

from backend.database import db, embed_model
from backend.chunker import chunk_text

def ingest_file(file_path):
    if not os.path.exists(file_path):
        print(f"Erro: Arquivo {file_path} não encontrado.")
        return

    print(f"Lendo arquivo: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Chunking
    chunks = chunk_text(content, chunk_size=2000)
    print(f"Gerados {len(chunks)} chunks.")
    
    # Indexação
    for i, c in enumerate(chunks):
        embedding = embed_model.encode(c).tolist()
        db.insert(c, embedding, page=1, source=os.path.basename(file_path))
        print(f"Chunk {i+1}/{len(chunks)} indexado.")

if __name__ == "__main__":
    target = "/app/manuals/graphcast_questions_it.md"
    ingest_file(target)
    print("Ingestão concluída com sucesso.")
