import pytest
from unittest.mock import patch
from backend.orchestrator import build_graph

@pytest.fixture
def graph():
    return build_graph()

@patch("backend.orchestrator.call_gemma")
def test_routing_to_rag(mock_gemma, graph):
    # Mock do roteamento e da resposta do RAG
    mock_gemma.side_effect = ["rag", "Resposta RAG Simulada"]
    
    state = {
        "messages": ["Como calibrar o manual da incubadora?"],
        "intent": "",
        "context": "",
        "language": "it"
    }
    
    result = graph.invoke(state)
    
    assert result["intent"] == "rag"
    assert "Resposta RAG Simulada" in result["context"]

@patch("backend.orchestrator.call_gemma")
@patch("backend.orchestrator.db.search")
def test_routing_to_code(mock_search, mock_gemma, graph):
    # Mock do roteamento e do contexto de código
    mock_gemma.side_effect = ["code", "Análise de Código Simulada"]
    mock_search.return_value = [{"text": "void main() {}", "page": 1}]
    
    state = {
        "messages": ["Explique a função main"],
        "intent": "",
        "context": "",
        "language": "it"
    }
    
    result = graph.invoke(state)
    
    assert result["intent"] == "code"
    assert "Análise de Código Simulada" in result["context"]
