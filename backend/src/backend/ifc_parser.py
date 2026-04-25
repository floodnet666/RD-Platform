import ifcopenshell
import polars as pl
import os

class IFCParser:
    """
    Extrator de Ativos de arquivos IFC (BIM).
    Converte modelos 3D complexos em tabelas de materiais (BOM) legíveis.
    """
    def __init__(self, ifc_path: str, price_catalog: dict = None):
        if not os.path.exists(ifc_path):
            raise FileNotFoundError(f"Arquivo IFC não encontrado: {ifc_path}")
        self.model = ifcopenshell.open(ifc_path)
        self.price_catalog = price_catalog or {}
        
        # Auditoria: Bloqueia simulação silenciosa de preços
        if not self.price_catalog:
             print("[WARNING] Nenhum catálogo de preços fornecido ao IFCParser. Custos serão reportados como 0.0.")

    def to_dataframe(self) -> pl.DataFrame:
        """
        Extrai elementos construtivos (Paredes, Janelas, Portas, etc)
        com seus atributos básicos para análise de custos.
        """
        data = []
        # Elementos comuns de uma BOM de arquitetura/engenharia
        elements = self.model.by_type("IfcElement")
        
        for el in elements:
            # Tenta extrair o nome e a classe IFC
            name = getattr(el, "Name", "Unnamed")
            ifc_type = el.is_a()
            
            # Tenta extrair tags ou propriedades básicas (ex: GlobalId)
            # Fix [HIGH-05]: Cruzamento real de preços ou fallback seguro
            price = self.price_catalog.get(el.GlobalId, 0.0)
            
            data.append({
                "part_number": el.GlobalId,
                "description": f"{ifc_type}: {name}",
                "quantity": 1,
                "unit_price": price,
                "category": ifc_type
            })
            
        return pl.DataFrame(data)

if __name__ == "__main__":
    # Teste de fumaça (Smoke Test)
    print("Parser IFC carregado com sucesso.")
