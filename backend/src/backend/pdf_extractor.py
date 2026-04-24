import os
import fitz  # PyMuPDF

def extract_text_from_pdf(filepath: str) -> list[dict]:
    """
    Extrai texto de um arquivo PDF mantendo o mapeamento de páginas.
    Retorna uma lista de dicionários: [{"text": str, "page": int}, ...]
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Arquivo não encontrado: {filepath}")
        
    pages_data = []
    
    with fitz.open(filepath) as pdf:
        for page_num in range(pdf.page_count):
            page = pdf[page_num]
            text = page.get_text().strip()
            if text:
                pages_data.append({
                    "text": text,
                    "page": page_num + 1
                })
                
    return pages_data
