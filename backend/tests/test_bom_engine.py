import pytest
from backend.bom_engine import BOMEngine
import os

def test_bom_total_cost_calculation():
    """
    Valida se o motor Polars consegue calcular o custo total corretamente
    sem alucinação do LLM.
    """
    csv_path = "manuals/test_bom.csv"
    engine = BOMEngine(csv_path)
    
    # Query: Qual o valor total do inventário?
    # Cálculo manual: (10*15.5) + (5*45) + (500*0.05) + (12*12) + (2*150) = 849
    sql_query = "SELECT SUM(quantity * unit_price) as total FROM bom"
    result = engine.execute_sql(sql_query)
    
    total = result[0]["total"]
    assert total == 849.0, f"FALHA: Cálculo de custo total incorreto. Recebido: {total}"

def test_bom_filtering():
    """Valida a filtragem de categorias via SQL."""
    engine = BOMEngine("manuals/test_bom.csv")
    
    # Query: Quantos sensores temos no total?
    sql_query = "SELECT SUM(quantity) as total_sensors FROM bom WHERE category = 'Sensores'"
    result = engine.execute_sql(sql_query)
    
    total_sensors = result[0]["total_sensors"]
    assert total_sensors == 15 # 10 LID-35 + 5 TH-100
