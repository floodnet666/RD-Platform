import re

def parse_source_code(code: str, lang: str) -> list[str]:
    """
    Segmenta o código fonte em blocos lógicos (funções/classes).
    Suporta Python (indentação/def) e C (chaves).
    """
    blocks = []
    
    if lang == "py":
        # Divide por 'def ' ou 'class ' no início da linha
        # Usa lookahead para não consumir o delimitador
        raw_blocks = re.split(r'^(?=def |class )', code, flags=re.MULTILINE)
        blocks = [b.strip() for b in raw_blocks if b.strip()]
        
    elif lang == "c":
        # Lógica simplificada: busca blocos que terminam em '}' 
        # e começam com uma assinatura de função (tipo nome(args) {)
        # Regex busca: tipo_retorno nome(args) { ... }
        pattern = r'[\w\s\*]+\s+\w+\s*\([^)]*\)\s*\{[^\}]*\}'
        blocks = re.findall(pattern, code, flags=re.DOTALL)
        
        # Fallback se a regex de blocos falhar: dividir por chaves
        if not blocks:
            raw_blocks = code.split('}')
            blocks = [b.strip() + ' }' for b in raw_blocks if b.strip()]
            
    return blocks
