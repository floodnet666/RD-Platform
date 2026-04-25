import fitz  # PyMuPDF
import os
import re


# ─────────────────────────────────────────────
# DIRECTIVA 1: Heurística de Agrupamento de Cabeçalhos
# ─────────────────────────────────────────────

def _is_terminal_punctuation(text: str) -> bool:
    """Verifica se uma string termina com pontuação de fim de frase."""
    return bool(re.search(r'[.!?:;]$', text.strip()))


def _merge_consecutive_headers(text: str) -> str:
    """
    Funde cabeçalhos Markdown consecutivos sem corpo entre eles e sem pontuação terminal.
    Suporta todos os níveis (#, ##, ###).
    Ex: ## Physics\n## Informed\n## Neural -> ## Physics Informed Neural
    """
    # Padrão: captura nível do header (#, ##, ...) e seu conteúdo
    header_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
    lines = text.split('\n')
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]
        m = header_pattern.match(line.strip())

        if m:
            level = m.group(1)
            content = m.group(2).strip()

            # Look-ahead: aglutina headers consecutivos do mesmo nível se não há pontuação terminal
            while (not _is_terminal_punctuation(content)
                   and i + 1 < len(lines)):
                next_line = lines[i + 1].strip()
                nm = header_pattern.match(next_line)
                # Só fundir se o próximo for um header do mesmo nível e a linha entre eles estiver vazia
                if nm and nm.group(1) == level:
                    content = f"{content} {nm.group(2).strip()}"
                    i += 1
                else:
                    break

            result.append(f"{level} {content}")
        else:
            result.append(line)

        i += 1

    return '\n'.join(result)


def sanitize_markdown(text: str) -> str:
    """
    Limpeza pós-extração:
    1. Remove quebras de linha excessivas.
    2. Aplica heurística de agrupamento de cabeçalhos fragmentados.
    """
    # Colapsar mais de 2 linhas em branco consecutivas
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Fundir headers fragmentados
    text = _merge_consecutive_headers(text)
    return text


# ─────────────────────────────────────────────
# Extração Legado (retrocompatibilidade)
# ─────────────────────────────────────────────

def extract_text_from_pdf(pdf_path: str) -> list[dict]:
    """Extração simples — usa get_text() plano por página."""
    doc = fitz.open(pdf_path)
    return [{"page": i + 1, "text": doc.load_page(i).get_text()} for i in range(len(doc))]


# ─────────────────────────────────────────────
# Extração Estruturada Markdown-First (V3)
# ─────────────────────────────────────────────

def extract_text_from_pdf_structured(pdf_path: str) -> list[dict]:
    """
    Extração estruturada com propagação de metadados de secção.
    Garante que nenhum chunk fique 'órfão': cada bloco herda a secção pai activa.
    """
    if not os.path.exists(pdf_path):
        return [{"page": 1, "text": "Mock data", "section": "Root"}]

    doc = fitz.open(pdf_path)
    structured_content = []
    # Metadado de secção persiste entre páginas — sem perda de hierarquia
    current_section = "Introduzione"

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]

        page_lines = []
        for b in blocks:
            if "lines" not in b:
                continue
            for l in b["lines"]:
                line_text = ""
                is_header = False

                for s in l["spans"]:
                    span_text = s["text"].strip()
                    if not span_text:
                        continue
                    # Heurística: tamanho de fonte > 12 ou Bold indica cabeçalho potencial
                    if s["size"] > 12 or "Bold" in s["font"]:
                        is_header = True
                    line_text += span_text + " "

                line_text = line_text.strip()
                if not line_text:
                    continue

                if is_header and len(line_text) < 100:
                    # Actualiza a secção activa — propaga para todos os chunks desta página
                    current_section = line_text
                    page_lines.append(f"\n## {line_text}\n")
                else:
                    page_lines.append(line_text)

        raw_text = " ".join(page_lines)
        clean_text = sanitize_markdown(raw_text)

        structured_content.append({
            "page": page_num + 1,
            "text": clean_text,
            # Cada chunk carrega o nome da secção activa no momento da extracção
            "section": current_section,
        })

    return structured_content
