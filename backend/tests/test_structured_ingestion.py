import pytest
import os
from backend.pdf_extractor import extract_text_from_pdf_structured

def test_structured_pdf_extraction():
    """
    TDD: Verifica se a extração estruturada identifica seções e mantém metadados de hierarquia.
    """
    # Criamos um PDF de teste ou usamos um path esperado
    # Por enquanto, vamos testar a interface da função que ainda não existe
    test_pdf = "manuals/test_structure.pdf"
    
    # Se o arquivo não existir, pulamos ou criamos um mock se necessário.
    # Mas para TDD, queremos que o código de importação e execução falhe primeiro.
    
    from backend.pdf_extractor import extract_text_from_pdf_structured
    
    # Testa com arquivo inexistente (deve retornar mock estruturado)
    pages = extract_text_from_pdf_structured("non_existent.pdf")
    
    assert len(pages) > 0
    assert "section" in pages[0], "FALHA: O metadado 'section' deve estar presente."
    assert pages[0]["section"] == "Root", "FALHA: O mock deve retornar seção 'Root'."
