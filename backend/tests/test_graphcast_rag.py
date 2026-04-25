import pytest
from backend.database import db, embed_model
import os

def test_graphcast_hybrid_retrieval():
    """
    Verifica se a Busca Híbrida (BM25 + Vetorial) consegue recuperar o termo exato '50 hPa'
    da Domanda 4, que costuma ser difícil para busca puramente vetorial.
    """
    # Inserção de dados de teste (Self-Contained)
    test_text = "GraphCast perde para HRES na estratosfera, especialmente em altitudes acima de 50 hPa devido ao peso."
    db.insert(test_text, embed_model.encode(test_text).tolist(), page=1, source="test_doc.pdf", section="Test Section")
    
    query = "In quale regione GraphCast perde contro HRES e cosa c'entra il peso a 50 hPa?"
    q_emb = embed_model.encode(query).tolist()
    
    # Busca Híbrida
    results = db.search_hybrid(query, q_emb, k=3)
    
    print("\n[HYBRID DEBUG] Resultados Encontrados:")
    for i, r in enumerate(results):
        print(f"[{i}] ID: {r['id']} | {r['text'][:200]}...")

    # Verifica se encontrou o termo crítico
    found = any("50 hPa" in item["text"] and "stratosfera" in item["text"].lower() for item in results)
    
    assert found, "FALHA: A busca híbrida não encontrou a menção específica a '50 hPa' e 'stratosfera'."

def test_query_rewriting_logic():
    """
    Verifica se a lógica de HyDE/Rewriting funcionaria. 
    (Simulação simplificada do prompt usado no orchestrator)
    """
    # Inserção de dados de teste (Self-Contained)
    test_text = "ERA5 usa janelas assimétricas de 9 ore per 00z e 12z."
    db.insert(test_text, embed_model.encode(test_text).tolist(), page=1, source="era5_doc.pdf", section="Data Assimilation")
    
    query = "Perché 00z e 12z?"
    # Aqui testamos se o banco retorna algo útil para uma query tão curta usando a busca híbrida
    q_emb = embed_model.encode(query).tolist()
    results = db.search_hybrid(query, q_emb, k=5)
    
    found = any("9 ore" in item["text"] or "ERA5" in item["text"] for item in results)
    assert found, "FALHA: A busca híbrida falhou em recuperar o contexto ERA5 para a query curta '00z e 12z'."
