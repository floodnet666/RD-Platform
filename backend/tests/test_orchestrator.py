import pytest
from backend.orchestrator import build_graph, AgentState

def test_graph_initialization():
    graph = build_graph()
    assert graph is not None
    # Verifica que os nós fundamentais foram compilados
    assert "router" in graph.nodes

def test_routing_to_rag():
    graph = build_graph()
    # "manual" na query deve forçar o roteamento para RAG
    state = {"messages": ["Como calibrar o manual da incubadora?"], "intent": "", "context": ""}
    
    # Executa o workflow
    result = graph.invoke(state)
    
    # O router node deve ter setado a intenção
    assert result["intent"] == "rag"
    # O rag_node deve ter injetado o contexto (mockado neste nível de teste)
    assert result["context"] == "rag_results_mock"

def test_routing_to_bom():
    graph = build_graph()
    # A query genérica de preço/peça deve rotear para o BOM
    state = {"messages": ["Qual o preço dos parafusos?"], "intent": "", "context": ""}
    
    result = graph.invoke(state)
    
    assert result["intent"] == "bom"
    assert result["context"] == "bom_results_mock"
