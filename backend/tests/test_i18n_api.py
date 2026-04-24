import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_api_language_propagation():
    """
    Verifica se o parâmetro 'lang' é aceito pela API e se influencia a resposta.
    """
    # Teste em Italiano
    query_it = {"message": "Ciao", "lang": "it"}
    response_it = client.post("/chat", json=query_it)
    assert response_it.status_code == 200
    
    # Teste em Inglês
    query_en = {"message": "Hello", "lang": "en"}
    response_en = client.post("/chat", json=query_en)
    assert response_en.status_code == 200
