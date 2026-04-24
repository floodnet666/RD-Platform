import pytest
from backend.ifc_parser import IFCParser
from backend.bom_engine import BOMEngine
import os
import polars as pl

def test_real_ifc_bom_extraction():
    """
    PROVA DE FOGO: Extração de BOM a partir de um arquivo IFC real do buildingSMART.
    """
    ifc_path = "manuals/building_architecture.ifc"
    assert os.path.exists(ifc_path), "FALHA: Arquivo IFC real não encontrado."
    
    # 1. Parsear IFC
    parser = IFCParser(ifc_path)
    df = parser.to_dataframe()
    
    # Verifica se extraímos algo
    assert len(df) > 0
    print(f"\n[INFO] Extraídos {len(df)} elementos do IFC real.")
    
    # 2. Salva como CSV temporário para o BOMEngine
    temp_csv = "manuals/temp_ifc_bom.csv"
    df.write_csv(temp_csv)
    
    # 3. Consultar via BOMEngine (Polars SQL)
    engine = BOMEngine(temp_csv)
    
    # Query: Contar tipos de elementos
    result = engine.execute_sql("SELECT category, COUNT(*) as count FROM bom GROUP BY category ORDER BY count DESC")
    
    assert len(result) > 0
    # Imprime os 5 principais tipos encontrados para prova visual
    for row in result[:5]:
        print(f"[RESULT] Elemento: {row['category']} -> {row['count']} unidades")
    
    # Limpeza
    if os.path.exists(temp_csv):
        os.remove(temp_csv)

if __name__ == "__main__":
    test_real_ifc_bom_extraction()
