import pytest
from backend.chunker import chunk_text

def test_chunk_text_basic():
    text = "Este é um teste. Segunda frase. Terceira frase aqui. Quarta e final."
    chunks = chunk_text(text, chunk_size=20, overlap=5)
    
    assert len(chunks) > 1, "Deve dividir textos grandes em múltiplos pedaços"
    assert "Este é um teste" in chunks[0]

def test_chunk_text_empty():
    chunks = chunk_text("", chunk_size=100, overlap=20)
    assert chunks == [], "Texto vazio deve retornar lista vazia"

def test_chunk_overlap():
    text = "1234567890"
    # chunk 1: 12345
    # chunk 2: 45678
    # chunk 3: 7890
    chunks = chunk_text(text, chunk_size=5, overlap=2)
    assert len(chunks) == 3
    assert chunks[0] == "12345"
    assert chunks[1] == "45678"
    assert chunks[2] == "7890"
