import sqlite3
import sqlite_vec
import struct

def serialize_f32(vector: list[float]) -> bytes:
    """Serializa uma lista de floats para bytes, formato exigido pelo sqlite-vec."""
    return struct.pack("%sf" % len(vector), *vector)

class VectorDB:
    """
    Wrapper ultraleve para sqlite-vec (zero sqlalchemy, zero orm).
    Complexidade ciclomática mínima.
    """
    def __init__(self, db_path: str = "R&D PLATFORM_rag.db", dimension: int = 384):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.enable_load_extension(True)
        sqlite_vec.load(self.conn)
        self.conn.enable_load_extension(False)
        
        self.dimension = dimension
        self._init_db()
        
    def _init_db(self):
        # Tabela virtual do sqlite-vec só guarda o vetor. Precisamos de uma tabela normal para os metadados.
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text_content TEXT,
                page_number INTEGER,
                source_file TEXT
            )
        ''')
        self.conn.execute(f'''
            CREATE VIRTUAL TABLE IF NOT EXISTS chunks_vec USING vec0(
                embedding float[{self.dimension}]
            )
        ''')
        self.conn.commit()

    def insert(self, text: str, embedding: list[float], page: int, source: str = "unknown"):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO chunks (text_content, page_number, source_file) VALUES (?, ?, ?)", (text, page, source))
        rowid = cursor.lastrowid
        cursor.execute(
            "INSERT INTO chunks_vec (rowid, embedding) VALUES (?, ?)", 
            (rowid, serialize_f32(embedding))
        )
        self.conn.commit()

    def search(self, query_embedding: list[float], k: int = 3) -> list[dict]:
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT chunks.text_content, chunks.page_number
            FROM chunks_vec
            LEFT JOIN chunks ON chunks.id = chunks_vec.rowid
            WHERE embedding MATCH ? AND k = ?
        """, (serialize_f32(query_embedding), k))
        
        return [{"text": row[0], "page": row[1]} for row in cursor.fetchall()]
