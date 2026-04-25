import fitz  # PyMuPDF
import os
import re

def sanitize_markdown(text):
    """
    Limpa artefatos de extração, unindo cabeçalhos fragmentados.
    Ex: ## Physics \n ## Informed -> ## Physics Informed
    """
    # Remove quebras de linha excessivas
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Une headers fragmentados: ## Palavra \n ## Outra -> ## Palavra Outra
    # Loop para pegar fragmentos múltiplos (3 ou mais palavras)
    for _ in range(3):
        text = re.sub(r'## (.*?)\n+## (.*?)', r'## \1 \2', text)
    
    return text

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
    Extração estruturada Markdown-First (V2). 
    Identifica headers por linha, une spans e aplica sanitização Regex.
    """
    if not os.path.exists(pdf_path):
        return [{"page": 1, "text": "Mock data", "section": "Root"}]

    doc = fitz.open(pdf_path)
    structured_content = []
    current_section = "Introduzione"

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]
        
        page_lines = []
        for b in blocks:
            if "lines" in b:
                for l in b["lines"]:
                    line_text = ""
                    is_header = False
                    
                    # Analisamos a linha como uma unidade
                    for s in l["spans"]:
                        span_text = s["text"].strip()
                        if not span_text: continue
                        
                        # Se houver spans grandes ou bold na linha, marcamos como potencial header
                        if s["size"] > 12 or "Bold" in s["font"]:
                            is_header = True
                        
                        line_text += span_text + " "
                    
                    line_text = line_text.strip()
                    if not line_text: continue

                    if is_header and len(line_text) < 100: # Headers geralmente não são parágrafos longos
                        current_section = line_text
                        page_lines.append(f"\n## {line_text}\n")
                    else:
                        page_lines.append(line_text)
        
        raw_text = " ".join(page_lines)
        clean_text = sanitize_markdown(raw_text)
        
        structured_content.append({
            "page": page_num + 1,
            "text": clean_text,
            "section": current_section
        })
        
    return structured_content
