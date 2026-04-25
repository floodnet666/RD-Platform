import pytest
import os
import polars as pl
from backend.bom_engine import BOMEngine

@pytest.fixture(scope="module")
def setup_bom_csv():
    csv_path = "manuals/test_bom.csv"
    os.makedirs("manuals", exist_ok=True)
    data = {
        "part_number": ["PN01", "PN02", "PN03", "PN04", "PN05"],
        "description": ["Sensor LID-35", "Sensor TH-100", "Parafuso M8", "Válvula V1", "Controlador PLC"],
        "quantity": [10, 5, 500, 12, 2],
        "unit_price": [15.5, 45.0, 0.05, 12.0, 150.0],
        "category": ["Sensores", "Sensores", "Fixação", "Hidráulica", "Eletrônica"]
    }
    df = pl.DataFrame(data)
    df.write_csv(csv_path)
    yield csv_path
    if os.path.exists(csv_path):
        os.remove(csv_path)

def test_bom_total_cost_calculation(setup_bom_csv):
    """
    Valida se o motor Polars consegue calcular o custo total corretamente
    sem alucinação do LLM.
    """
    engine = BOMEngine(setup_bom_csv)
    
    # Query: Qual o valor total do inventário?
    # Cálculo manual: (10*15.5) + (5*45) + (500*0.05) + (12*12) + (2*150) = 849
    sql_query = "SELECT SUM(quantity * unit_price) as total FROM bom"
    result = engine.execute_sql(sql_query)
    
    total = result[0]["total"]
    assert total == 849.0, f"FALHA: Cálculo de custo total incorreto. Recebido: {total}"

def test_bom_filtering(setup_bom_csv):
    """Valida a filtragem de categorias via SQL."""
    engine = BOMEngine(setup_bom_csv)
    
    # Query: Quantos sensores temos no total?
    sql_query = "SELECT SUM(quantity) as total_sensors FROM bom WHERE category = 'Sensores'"
    result = engine.execute_sql(sql_query)
    
    total_sensors = result[0]["total_sensors"]
    assert total_sensors == 15 # 10 LID-35 + 5 TH-100
