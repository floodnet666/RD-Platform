import os
import polars as pl
from polars import SQLContext

class BOMEngine:
    """
    Motor Determinístico de Bill of Materials (BOM).
    Utiliza Polars (Rust) para bypass do LLM em tarefas matemáticas.
    Zero Alucinação.
    """
    def __init__(self, csv_path: str):
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Arquivo BOM não encontrado: {csv_path}")
        self.df = pl.read_csv(csv_path)
        # O SQLContext permite que o LLM Analyst gere queries estritas em SQL
        # e o Polars execute compilação para bytecode Rust hiperveloz.
        self.sql_ctx = SQLContext(frames={"bom": self.df})

    def get_parts_by_category(self, category: str) -> list[dict]:
        """Filtro linear direto via AST do Polars."""
        filtered = self.df.filter(pl.col("category") == category)
        return filtered.to_dicts()

    def calculate_total_cost(self) -> float:
        """Agregação matemática determinística."""
        cost = self.df.select(
            (pl.col("quantity") * pl.col("unit_price")).sum()
        ).item()
        return float(cost)

    def execute_sql(self, query: str) -> list[dict]:
        """
        Recebe uma instrução SQL injetada pelo Agente (LangGraph),
        avalia preguiçosamente e retorna os dicionários exatos.
        """
        result_df = self.sql_ctx.execute(query).collect()
        return result_df.to_dicts()
