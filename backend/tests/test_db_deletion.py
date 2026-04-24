import pytest
from backend.vector_db import VectorDB
import os

def test_selective_deletion_integrity():
    """
    Prova que a exclusão de um ativo remove apenas os seus dados,
    preservando a integridade dos outros ativos.
    """
    db_path = "test_cleanup.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        
    db = VectorDB(db_path)
    
    # 1. Simula inserção de dois arquivos
    emb = [0.1] * 384
    db.insert("Conteúdo do Manual A", emb, 1, source="manual_A.pdf")
    db.insert("Outro dado do Manual A", emb, 2, source="manual_A.pdf")
    db.insert("Conteúdo do Manual B", emb, 1, source="manual_B.pdf")
    
    # Verifica contagem inicial
    count = db.conn.execute("SELECT count(*) FROM chunks").fetchone()[0]
    assert count == 3
    
    # 2. Executa exclusão cirúrgica de Manual A
    filename_to_delete = "manual_A.pdf"
    db.conn.execute("DELETE FROM chunks_vec WHERE rowid IN (SELECT id FROM chunks WHERE source_file = ?)", (filename_to_delete,))
    db.conn.execute("DELETE FROM chunks WHERE source_file = ?", (filename_to_delete,))
    db.conn.commit()
    
    # 3. Verificações de Integridade
    count_after = db.conn.execute("SELECT count(*) FROM chunks").fetchone()[0]
    assert count_after == 1, "FALHA: A contagem de chunks após exclusão está incorreta."
    
    # Verifica se o que sobrou foi o Manual B
    remaining = db.conn.execute("SELECT source_file FROM chunks").fetchone()[0]
    assert remaining == "manual_B.pdf", "FALHA: O arquivo errado foi deletado ou sobrou lixo."
    
    # Verifica a tabela vetorial (chunks_vec)
    vec_count = db.conn.execute("SELECT count(*) FROM chunks_vec").fetchone()[0]
    assert vec_count == 1, "FALHA: A tabela de vetores não foi limpa corretamente."
    
    print("\nPROVA DE INTEGRIDADE: Exclusão cirúrgica validada. Zero resíduos do Manual A.")
    
    db.conn.close()
    os.remove(db_path)
