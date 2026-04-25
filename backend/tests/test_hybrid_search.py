import pytest
from backend.database import db, embed_model
import os

def test_hybrid_search_technical_precision():
    """
    Valida a eficácia da Busca Híbrida em recuperar termos técnicos exatos (BM25)
    e conceitos similares (Vetorial) em um cenário de engenharia genérico.
    """
    # 1. Ingestão de Dados Técnicos Genéricos (Self-Contained)
    # Termo difícil para busca vetorial pura: Código Alfanumérico Exato
    test_data = [
        {"text": "Il sensore modello SN-XP9000 deve essere calibrato con una tolleranza di 0.005mm.", "page": 1, "section": "Calibrazione"},
        {"text": "L'errore critico E-212 si verifica quando la pressione supera i 450 bar nel modulo primario.", "page": 2, "section": "Troubleshooting"},
        {"text": "Il protocollo di comunicazione utilizza il baud rate standard di 115200 bps.", "page": 3, "section": "Configurazione"}
    ]
    
    for item in test_data:
        emb = embed_model.encode(item["text"]).tolist()
        db.insert(item["text"], emb, page=item["page"], source="manual_generico.pdf", section=item["section"])
    
    # 2. Teste de Recuperação Lexical (Termo Exato)
    query_lexical = "Qual è la tolleranza per SN-XP9000?"
    q_emb_lex = embed_model.encode(query_lexical).tolist()
    results_lex = db.search_hybrid(query_lexical, q_emb_lex, k=3)
    
    found_lex = any("0.005mm" in r["text"] and "SN-XP9000" in r["text"] for r in results_lex)
    assert found_lex, "FALHA: A busca híbrida não recuperou o termo técnico exato 'SN-XP9000'."

    # 3. Teste de Recuperação Semântica (Conceito)
    query_semantic = "Cosa fare se la pressione è troppo alta nel sistema?"
    q_emb_sem = embed_model.encode(query_semantic).tolist()
    results_sem = db.search_hybrid(query_semantic, q_emb_sem, k=3)
    
    found_sem = any("E-212" in r["text"] and "450 bar" in r["text"] for r in results_sem)
    assert found_sem, "FALHA: A busca híbrida não associou 'pressione alta' ao erro 'E-212' via semântica."

def test_hybrid_search_reranking_logic():
    """
    Verifica se o RRF (Reciprocal Rank Fusion) prioriza corretamente documentos 
    que aparecem em ambos os rankings.
    """
    query = "baud rate 115200"
    q_emb = embed_model.encode(query).tolist()
    results = db.search_hybrid(query, q_emb, k=1)
    
    assert "bps" in results[0]["text"], "FALHA: RRF não priorizou o documento de configuração de baud rate."
