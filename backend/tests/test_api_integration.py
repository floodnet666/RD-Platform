import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_api_lid35_response():
    """
    Teste de Integração de Ponta a Ponta (Backend):
    Simula uma requisição HTTP do Frontend e valida a resposta final do RAG.
    """
    query = {"message": "Quando é utilizado o SENSOR LID-35?"}
    
    # Faz o POST para o endpoint real
    response = client.post("/chat", json=query)
    
    assert response.status_code == 200
    data = response.json()
    
    answer = data.get("response", "").upper()
    print(f"\nRESPOSTA FINAL DA API COM CITAÇÃO: {answer}")
    
    # Valida se a resposta contém informações úteis e a citação da página
    assert len(answer) > 20
    assert "PÁGINA" in answer or "PAGE" in answer, "FALHA: O sistema não incluiu a citação da página (rastreabilidade)."
    assert "LID" in answer or "SENSOR" in answer
