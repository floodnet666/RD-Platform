def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """
    Divide um texto longo em blocos de tamanho fixo com sobreposição.
    Filosofia: Zero dependências externas (sem Langchain RecursiveCharacterTextSplitter), 
    usando lógica pura com baixa complexidade.
    """
    if not text:
        return []
        
    chunks = []
    start = 0
    text_length = len(text)
    
    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        
        if end >= text_length:
            break
            
        start += (chunk_size - overlap)
        
    return chunks
