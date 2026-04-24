import pytest
from backend.llm_client import call_gemma

def test_gemma_inference_on_premise():
    """
    Valida se o Ollama está rodando e se o modelo Gemma-4-E2B responde.
    """
    prompt = "Responda apenas 'OK' se você está funcionando."
    response = call_gemma(prompt)
    
    print(f"\nRESPOSTA DO GEMMA: {response}")
    
    assert "OK" in response.upper(), f"FALHA: O modelo Gemma-4 no Ollama não respondeu como esperado. Resposta: {response}"

def test_gemma_technical_reasoning():
    """
    Valida se o modelo consegue processar uma lógica técnica simples.
    """
    prompt = "Qual a unidade de medida comum para temperatura em laboratórios biológicos?"
    response = call_gemma(prompt)
    
    assert "CELSIUS" in response.upper() or "C" in response.upper(), "FALHA: O modelo falhou no raciocínio técnico básico."
