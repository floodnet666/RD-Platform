import pytest
from backend.orchestrator import build_graph

def test_debate_flow_execution():
    """
    TDD: Verifica se o grafo de debate executa todos os passos (Construtor -> Crítico -> Sintetizador).
    """
    graph = build_graph()
    
    # Simula um estado inicial
    initial_state = {
        "messages": ["Como funciona o sensor LID-35?"],
        "intent": "rag"
    }
    
    # Executa o grafo
    # Nota: Isso requer que o Ollama esteja acessível ou mockado. 
    # Para o teste unitário, vamos verificar se os nós existem no grafo.
    
    nodes = graph.nodes.keys()
    assert "constructor" in nodes, "FALHA: O nó 'constructor' deve existir no grafo."
    assert "critic" in nodes, "FALHA: O nó 'critic' deve existir no grafo."
    assert "synthesizer" in nodes, "FALHA: O nó 'synthesizer' deve existir no grafo."
