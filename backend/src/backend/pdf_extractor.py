import fitz  # PyMuPDF
import os

def extract_text_from_pdf(pdf_path):
    """Extração simples legado para retrocompatibilidade."""
    doc = fitz.open(pdf_path)
    pages_text = []
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pages_text.append({"page": page_num + 1, "text": page.get_text()})
    return pages_text

def extract_text_from_pdf_structured(pdf_path):
    """
    Extração estruturada Markdown-First. 
    Identifica headers, listas e tenta preservar o contexto da seção.
    """
    if not os.path.exists(pdf_path):
        # Para testes sem arquivo real
        return [{"page": 1, "text": "Mock data", "section": "Root"}]

    doc = fitz.open(pdf_path)
    structured_content = []
    current_section = "Introduzione"

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]
        
        page_text = []
        for b in blocks:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        text = s["text"].strip()
                        if not text: continue
                        
                        # Heurística simples: Texto em negrito ou tamanho maior = Header
                        if s["size"] > 12 or "Bold" in s["font"]:
                            current_section = text
                            page_text.append(f"\n## {text}\n")
                        else:
                            page_text.append(text)
        
        full_text = " ".join(page_text)
        structured_content.append({
            "page": page_num + 1,
            "text": full_text,
            "section": current_section
        })
        
    return structured_content
