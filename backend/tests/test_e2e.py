import pytest
from playwright.sync_api import sync_playwright
import time
import requests

def test_full_system_integration():
    """
    Auditoria Final: Testa o fluxo completo UI -> API -> LangGraph -> Ollama.
    """
    # 1. Verificar se o Backend está vivo antes de iniciar o browser
    try:
        requests.get("http://127.0.0.1:8000/", timeout=2)
    except:
        pytest.fail("Backend (main.py) não está rodando na porta 8000.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("Acessando interface Oko-Agent...")
        page.goto("http://localhost:5173", timeout=10000)
        
        # 2. Injetar pergunta técnica no input
        selector = "input[placeholder*='query técnica']"
        page.wait_for_selector(selector)
        page.fill(selector, "Qual a temperatura máxima suportada pelo Top Stage?")
        
        print("Disparando inferência para Gemma-4-E2B...")
        page.click("button")
        
        # 3. Aguardar resposta do motor RAG (pode demorar devido à inferência local)
        # Procuramos pela resposta que contém dados do manual (20-45°C)
        agent_msg_selector = ".message-agent:has-text('45')"
        try:
            page.wait_for_selector(agent_msg_selector, timeout=90000)
            print("Sucesso: Resposta do RAG capturada com dados reais.")
        except:
            # Se falhar o texto exato, pegamos a última mensagem para diagnóstico
            last_msg = page.inner_text(".message-agent:last-child")
            pytest.fail(f"O sistema não retornou a resposta esperada do manual. Última mensagem: {last_msg}")
            
        browser.close()

if __name__ == "__main__":
    test_full_system_integration()
