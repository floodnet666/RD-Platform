import os
import pytest
from backend.vector_db import VectorDB

def test_db_initialization():
    db = VectorDB(":memory:", dimension=3)
    assert db is not None
    # Verify table exists
    tables = db.conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    table_names = [t[0] for t in tables]
    assert "chunks_vec" in table_names or "chunks_vec_rowid" in table_names

def test_insert_and_search():
    db = VectorDB(":memory:", dimension=3)
    
    # Inserir mock data
    db.insert("texto 1", [1.0, 0.0, 0.0], page=1)
    db.insert("texto 2", [0.0, 1.0, 0.0], page=2)
    
    # Buscar
    results = db.search([1.0, 0.0, 0.0], k=1)
    
    assert len(results) == 1
    assert results[0]["text"] == "texto 1"
