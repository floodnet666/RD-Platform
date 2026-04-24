import httpx
import os

def call_gemma(prompt: str, system_prompt: str = "") -> str:
    """
    Interface de inferência real com o modelo Gemma-4-E2B via Ollama.
    Usa host.docker.internal se estiver no Docker, caso contrário localhost.
    """
    # Detecção automática de ambiente Docker vs Host
    ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    url = f"{ollama_host}/api/generate"
    payload = {
        "model": "hf.co/mradermacher/gemma-4-E2B-it-uncensored-GGUF:Q8_0",
        "prompt": prompt,
        "system": system_prompt,
        "stream": False
    }
    
    try:
        with httpx.Client(timeout=90.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            return response.json().get("response", "Erro: Resposta vazia do Ollama.")
    except Exception as e:
        return f"Falha na conexão On-Premise (Ollama): {str(e)}"
