import pytest
from fastapi.testclient import TestClient
from backend.main import app
from unittest.mock import patch

client = TestClient(app)

@patch("git.Repo.clone_from")
def test_clone_with_token_propagation(mock_clone):
    """
    Verifica se o token é injetado corretamente na URL de clonagem 
    para suportar repositórios privados da R&D PLATFORM.
    """
    repo_url = "https://github.com/R&D PLATFORM/private-repo"
    token = "ghp_secure_token_123"
    
    # Simula a requisição com token
    response = client.post("/clone", json={
        "repo_url": repo_url,
        "token": token
    })
    
    # Verifica se o GitPython recebeu a URL autenticada
    expected_url = f"https://{token}@github.com/R&D PLATFORM/private-repo"
    args, kwargs = mock_clone.call_args
    assert args[0] == expected_url, f"FALHA: Token não foi injetado na URL. Recebido: {args[0]}"
