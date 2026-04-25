import os
from backend.pdf_extractor import extract_text_from_pdf
from backend.chunker import chunk_text
from backend.vector_db import VectorDB
from sentence_transformers import SentenceTransformer

def run_ingestion():
    # Reset do Banco para novo Schema (Páginas)
    db_path = "R&D PLATFORM_rag.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    print("Iniciando Ingestão com Rastreabilidade de Páginas...")
    
    # Motores
    model = SentenceTransformer('all-MiniLM-L6-v2')
    db = VectorDB(db_path)
    
    manuals_dir = os.path.join("..", "manuals")
    if not os.path.exists(manuals_dir):
        print(f"Diretório de manuais não encontrado: {manuals_dir}")
        return

    for file in os.listdir(manuals_dir):
        if file.endswith(".pdf"):
            path = os.path.join(manuals_dir, file)
            print(f"Processando: {file}")
            
            # Extração por página
            pages = extract_text_from_pdf(path)
            
            for p in pages:
                # Chunking de cada página
                chunks = chunk_text(p["text"])
                for c in chunks:
                    embedding = model.encode(c).tolist()
                    db.insert(c, embedding, p["page"])
                    
    print("Ingestão concluída. Banco de Dados pronto para Citations.")

if __name__ == "__main__":
    run_ingestion()
