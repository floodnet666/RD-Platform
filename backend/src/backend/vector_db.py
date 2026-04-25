import sqlite3
import sqlite_vec
import struct
import threading

def serialize_f32(vector: list[float]) -> bytes:
    """Serializa uma lista de floats para bytes, formato exigido pelo sqlite-vec."""
    return struct.pack("%sf" % len(vector), *vector)

class VectorDB:
    """
    Motor Híbrido R&D: Combina Busca Vetorial (sqlite-vec) com Busca Lexical (FTS5).
    Implementa Reciprocal Rank Fusion (RRF) para fusão de resultados.
    """
    def __init__(self, db_path: str = "R&D PLATFORM_rag.db", dimension: int = 384):
        self._lock = threading.Lock()
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.enable_load_extension(True)
        sqlite_vec.load(self.conn)
        self.conn.enable_load_extension(False)
        
        self.dimension = dimension
        with self._lock:
            self._init_db()
        
    def _init_db(self):
        # 1. Metadados (Tabela Normal)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS chunks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                text_content TEXT,
                page_number INTEGER,
                source_file TEXT,
                section_name TEXT
            )
        ''')
        
        # 2. Busca Vetorial (sqlite-vec)
        self.conn.execute(f'''
            CREATE VIRTUAL TABLE IF NOT EXISTS chunks_vec USING vec0(
                embedding float[{self.dimension}]
            )
        ''')
        
        # 3. Busca Lexical (FTS5) - Fix [HYBRID-SEARCH]: Suporte a termos específicos (BM25)
        self.conn.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                text_content,
                content='chunks',
                content_rowid='id'
            )
        ''')
        
        # Triggers para manter FTS5 sincronizado com a tabela chunks
        self.conn.execute("DROP TRIGGER IF EXISTS chunks_ai")
        self.conn.execute("""
            CREATE TRIGGER chunks_ai AFTER INSERT ON chunks BEGIN
                INSERT INTO chunks_fts(rowid, text_content) VALUES (new.id, new.text_content);
            END
        """)
        
        self.conn.commit()

    def insert(self, text: str, embedding: list[float], page: int, source: str = "unknown", section: str = "N/A"):
        with self._lock:
            cursor = self.conn.cursor()
            cursor.execute(
                "INSERT INTO chunks (text_content, page_number, source_file, section_name) VALUES (?, ?, ?, ?)", 
                (text, page, source, section)
            )
            rowid = cursor.lastrowid
            cursor.execute(
                "INSERT INTO chunks_vec (rowid, embedding) VALUES (?, ?)", 
                (rowid, serialize_f32(embedding))
            )
            self.conn.commit()

    def search_vector(self, query_embedding: list[float], k: int = 10) -> list[dict]:
        """Busca puramente semântica."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT chunks.id, chunks.text_content, chunks.page_number, chunks.section_name
            FROM chunks_vec
            LEFT JOIN chunks ON chunks.id = chunks_vec.rowid
            WHERE embedding MATCH ? AND k = ?
        """, (serialize_f32(query_embedding), k))
        return [{"id": row[0], "text": row[1], "page": row[2], "section": row[3]} for row in cursor.fetchall()]

    def search_fts(self, query_text: str, k: int = 10) -> list[dict]:
        """Busca puramente lexical (BM25)."""
        cursor = self.conn.cursor()
        sanitized_query = query_text.replace('"', ' ').replace("'", " ")
        try:
            cursor.execute("""
                SELECT id, text_content, page_number, section_name
                FROM chunks
                WHERE id IN (SELECT rowid FROM chunks_fts WHERE chunks_fts MATCH ?)
                LIMIT ?
            """, (sanitized_query, k))
            return [{"id": row[0], "text": row[1], "page": row[2], "section": row[3]} for row in cursor.fetchall()]
        except sqlite3.OperationalError:
            return []

    def search_hybrid(self, query_text: str, query_embedding: list[float], k: int = 5) -> list[dict]:
        """
        Fusão Híbrida usando Reciprocal Rank Fusion (RRF).
        Resolve o problema de termos específicos que o embedding às vezes ignora.
        """
        vec_results = self.search_vector(query_embedding, k=20)
        fts_results = self.search_fts(query_text, k=20)
        
        # RRF: score = sum( 1 / (60 + rank) )
        scores = {}
        
        for rank, res in enumerate(vec_results):
            cid = res["id"]
            scores[cid] = scores.get(cid, 0) + 1 / (60 + rank)
            
        for rank, res in enumerate(fts_results):
            cid = res["id"]
            scores[cid] = scores.get(cid, 0) + 1 / (60 + rank)
            
        # Ordenar por score e pegar os metadados dos melhores
        sorted_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k]
        
        final_results = []
        all_res = {r["id"]: r for r in vec_results + fts_results}
        
        for cid, score in sorted_ids:
            if cid in all_res:
                final_results.append(all_res[cid])
                
        return final_results
