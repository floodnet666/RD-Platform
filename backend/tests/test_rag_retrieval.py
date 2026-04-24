import pytest
from backend.vector_db import VectorDB
from sentence_transformers import SentenceTransformer
import os

def test_lid35_retrieval_integrity():
    """
    Teste de Integração Real: Verifica se o motor de busca consegue encontrar 
    a menção ao sensor LID-35 no banco de dados populado.
    """
    db_path = "okolab_rag.db"
    assert os.path.exists(db_path), "ERRO: Banco de dados não encontrado. Ingestão falhou."
    
    # Inicializa motores reais
    embed_model = SentenceTransformer('all-MiniLM-L6-v2')
    db = VectorDB(db_path)
    
    # Query específica sobre o sensor LID-35
    query = "quando é utilizado o SENSOR LID-35 ?"
    q_emb = embed_model.encode(query).tolist()
    
    # Executa busca
    results = db.search(q_emb, k=5)
    
    # Valida se o termo LID-35 aparece em pelo menos um dos chunks recuperados
    found = any("LID-35" in chunk.upper() or "LID35" in chunk.upper() for chunk in results)
    
    if not found:
        # Debug: Mostrar o que foi encontrado para análise de falha
        print("\nCHUNKS ENCONTRADOS (NÃO CONTÉM LID-35):")
        for i, c in enumerate(results):
            print(f"[{i}]: {c[:100]}...")
            
    assert found, "FALHA: O motor de busca não recuperou informações sobre o SENSOR LID-35."

def test_db_not_empty():
    """Verifica se a ingestão realmente persistiu dados."""
    db_path = "okolab_rag.db"
    db = VectorDB(db_path)
    count = db.conn.execute("SELECT count(*) FROM chunks").fetchone()[0]
    assert count > 0, "FALHA: O banco de dados está vazio após a ingestão."
