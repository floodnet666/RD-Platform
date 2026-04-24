import sqlite3
import os

db_path = "okolab_rag.db"

if not os.path.exists(db_path):
    print(f"ERRO: O arquivo {db_path} NÃO EXISTE na pasta backend.")
else:
    try:
        conn = sqlite3.connect(db_path)
        # Verifica as tabelas existentes
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        print(f"Tabelas encontradas: {tables}")
        
        # Conta documentos
        cursor.execute("SELECT count(*) FROM vec_documents")
        count = cursor.fetchone()[0]
        print(f"Total de Chunks no banco de vetores: {count}")
        
        if count > 0:
            # Mostra o conteúdo de um chunk para validar a extração
            cursor.execute("SELECT content FROM vec_documents LIMIT 1")
            content = cursor.fetchone()[0]
            print(f"Amostra de conteúdo do primeiro chunk:\n{content[:200]}...")
            
    except Exception as e:
        print(f"Erro ao acessar o banco: {str(e)}")
