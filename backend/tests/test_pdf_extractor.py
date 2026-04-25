import os
import pytest
from backend.pdf_extractor import extract_text_from_pdf

def test_extract_text_valid_pdf():
    """
    Testa se o parser consegue extrair texto do manual real.
    Garante integridade com o mundo real (Integration-like test).
    """
    pdf_path = r"D:\R&D PLATFORM\manuals\UM-BL3-Top-Stage_User-Manual-BL3_EN.pdf"
    
    if not os.path.exists(pdf_path):
        pytest.skip(f"Arquivo de teste não encontrado: {pdf_path}")
        
    text = extract_text_from_pdf(pdf_path)
    
    assert text is not None, "O texto extraído não deve ser None"
    assert len(text) > 0, "O texto extraído não deve ser vazio"
    assert isinstance(text, str), "O retorno deve ser uma string"

def test_extract_text_file_not_found():
    """
    Testa se o sistema rejeita arquivos inexistentes preemptivamente
    para evitar erros cascata no orquestrador.
    """
    with pytest.raises(FileNotFoundError):
        extract_text_from_pdf("arquivo_fantasma_inexistente.pdf")
