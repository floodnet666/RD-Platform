import sqlite3
import sqlite_vec
import struct
import threading
import re


def serialize_f32(vector: list[float]) -> bytes:
    """Serializa uma lista de floats para bytes, formato exigido pelo sqlite-vec."""
    return struct.pack("%sf" % len(vector), *vector)


# ─────────────────────────────────────────────
# DIRECTIVA 2: Classificação de Rigor Lexical
# ─────────────────────────────────────────────

# Padrões que indicam que a query contém identificadores únicos que exigem
# correspondência exacta lexical (números, siglas técnicas, IDs de equações).
_LEXICAL_PRECISION_PATTERNS = [
    re.compile(r'\b\d+\b'),                    # números inteiros isolados (ex: "9 layer", "3021")
    re.compile(r'\b\d+[\.,]\d+\b'),            # decimais/floats (ex: "1e-3", "0.001")
    re.compile(r'\b[A-Z]{2,}\b'),              # siglas (ex: "PINN", "RK4", "MSE")
    re.compile(r'N_[a-zA-Z]+\b|\$N_'),         # notação de parâmetros (ex: N_u, N_f)
    re.compile(r'(?<!\w)[A-Z][a-z]*\d+\b'),   # identificadores alfanuméricos (ex: "Eq1", "Model2")
]

def _compute_lexical_boost(query: str) -> float:
    """
    Retorna o factor de boost para a componente BM25.
    +30% (→ 1.30) se a query contiver identificadores únicos.
    Baseline: 1.0 (sem boost — peso simétrico Dense/BM25).
    """
    for pattern in _LEXICAL_PRECISION_PATTERNS:
        if pattern.search(query):
            return 1.30
    return 1.0


def _extract_numeric_anchors(query: str) -> list[str]:
    """
    Extrai sequências numéricas da query para ancoragem de metadados.
    Ex: "modelo de 9 camadas com 3021 parâmetros" → ['9', '3021']
    """
    return re.findall(r'\b\d+(?:[.,]\d+)?\b', query)


class VectorDB:
    """
    Motor Híbrido R&D: Combina Busca Vetorial (sqlite-vec) com Busca Lexical (FTS5).
    Implementa Reciprocal Rank Fusion (RRF) com boost lexical dinâmico.
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

        # 3. Busca Lexical (FTS5) — suporte a termos específicos (BM25)
        self.conn.execute('''
            CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
                text_content,
                content='chunks',
                content_rowid='id'
            )
        ''')

        # Trigger para manter FTS5 sincronizado
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
        Fusão Híbrida via Reciprocal Rank Fusion (RRF).

        DIRECTIVA 2:
        - Boost lexical de +30% quando a query contém identificadores únicos
          (números, siglas, IDs de equações).
        - Filtro de Ancoragem Numérica: chunks sem os números exactos da query
          recebem penalização de ranking (não são descartados, para não bloquear
          queries válidas sem âncoras numéricas).
        """
        lexical_boost = _compute_lexical_boost(query_text)
        numeric_anchors = _extract_numeric_anchors(query_text)

        vec_results = self.search_vector(query_embedding, k=20)
        fts_results = self.search_fts(query_text, k=20)

        # RRF com boost dinâmico: score = Σ weight / (60 + rank)
        scores: dict[int, float] = {}

        for rank, res in enumerate(vec_results):
            cid = res["id"]
            scores[cid] = scores.get(cid, 0.0) + 1.0 / (60 + rank)

        for rank, res in enumerate(fts_results):
            cid = res["id"]
            scores[cid] = scores.get(cid, 0.0) + lexical_boost / (60 + rank)

        # Ancoragem Numérica: chunks que contêm os números exactos da query ganham bónus
        if numeric_anchors:
            all_res_map = {r["id"]: r for r in vec_results + fts_results}
            for cid in list(scores.keys()):
                chunk_text = all_res_map.get(cid, {}).get("text", "")
                matched = sum(1 for n in numeric_anchors if n in chunk_text)
                if matched > 0:
                    # Bónus proporcional ao número de âncoras encontradas
                    scores[cid] += 0.05 * matched

        sorted_ids = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k]

        all_res = {r["id"]: r for r in vec_results + fts_results}
        return [all_res[cid] for cid, _ in sorted_ids if cid in all_res]
