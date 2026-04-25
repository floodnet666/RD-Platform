from typing import TypedDict, Annotated
import operator
import os
from langgraph.graph import StateGraph, END

from backend.llm_client import call_gemma
from backend.vector_db import VectorDB
from backend.bom_engine import BOMEngine
from backend.code_parser import parse_source_code
from sentence_transformers import SentenceTransformer

# Singleton instances para evitar overhead de recarregamento
embed_model = SentenceTransformer('all-MiniLM-L6-v2')
db = VectorDB("R&D PLATFORM_rag.db")

class AgentState(TypedDict):
    messages: Annotated[list[str], operator.add]
    intent: str
    context: str
    language: str

def router_node(state: AgentState):
    """Agente di Routing Semantico. Analizza l'intento senza euristiche rigide."""
    last_msg = state["messages"][-1]
    
    prompt = f"""
    Analizza la richiesta dell'utente e classificala in UNA delle categorie seguenti:
    - 'BOM': Domande su conteggio pezzi, prezzi, materiali, estrazione dati da file IFC/CSV.
    - 'MANUAL': Richieste per generare, creare o scrivere documentazione tecnica per UTENTI FINALI.
    - 'CODE': Domande su firmware, funzioni, logica di codice o richieste di DOCUMENTAZIONE di file sorgente (.py, .c).
    - 'RAG': Domande generiche su sensori, calibrazione o istruzioni contenute nei manuali PDF.
    
    Utente: "{last_msg}"
    Rispondi SOLO con il nome della categoria.
    """
    
    intent_raw = call_gemma(prompt, "Sei il Cervello di Routing di R&D PLATFORM.")
    intent = intent_raw.strip().upper()
    
    # Normalizzazione e Fallback
    valid_intents = ["BOM", "MANUAL", "CODE", "RAG"]
    final_intent = next((i.lower() for i in valid_intents if i in intent), "rag")
    
    print(f"\n[ORCHESTRATOR] 🧠 Intento Rilevato: {final_intent.upper()}")
    return {"intent": final_intent}

def rag_node(state: AgentState):
    """Busca vetorial real no sqlite-vec e síntese via Gemma-4 com Citações."""
    print(f"[ORCHESTRATOR] 🔍 Executing RAG Node...")
    query = state["messages"][-1]
    q_emb = embed_model.encode(query).tolist()
    context_data = db.search(q_emb, k=3)
    
    context_parts = []
    for item in context_data:
        context_parts.append(f"[FONTE: Página {item['page']}] {item['text']}")
    
    context = "\n---\n".join(context_parts)
    
    prompt = f"Contexto Técnico R&D PLATFORM:\n{context}\n\nPergunta: {query}\n\nInstrução: Responda obrigatoriamente no idioma [{state['language'].upper()}]. Seja técnico e cite a [Página X]."
    answer = call_gemma(prompt, f"Você é um assistente de engenharia da R&D PLATFORM. Responda em {state['language']}.")
    return {"context": answer}

def bom_node(state: AgentState):
    """Execução determinística Polars com arquivo CSV dinâmico."""
    print(f"[ORCHESTRATOR] 📊 Executing BOM/IFC Engine Node...")
    manual_dir = "manuals"
    if not os.path.exists(manual_dir):
        os.makedirs(manual_dir)
        
    files = [os.path.join(manual_dir, f) for f in os.listdir(manual_dir) if f.endswith(".csv")]
    if not files:
        return {"context": "Erro: Nenhuma base de dados BOM encontrada. Carregue um arquivo CSV ou IFC primeiro."}
    
    latest_bom_path = max(files, key=os.path.getmtime)
    print(f"[BOM_ENGINE] Using file: {latest_bom_path}")
    engine = BOMEngine(latest_bom_path)
    
    query = state["messages"][-1]
    sql_prompt = f"""
    Convert to SQL (table 'bom'): {query}
    Table Schema:
    - part_number (string)
    - description (string)
    - quantity (integer)
    - unit_price (float)
    - category (string, example: 'IfcWall', 'IfcWindow', 'IfcSlab')
    
    Use simple ANSI SQL. Do NOT use subqueries with '='. Use 'IN' for subqueries. 
    Return ONLY the SQL string.
    """
    sql_query = call_gemma(sql_prompt, "You are a Natural Language to Polars SQL translator. Be precise about column names.")
    
    sql_query = sql_query.replace("```sql", "").replace("```", "").strip()
    if "SELECT" in sql_query.upper() and "= (" in sql_query:
        sql_query = sql_query.replace("= (", "IN (")
    
    print(f"[SQL_DEBUG] Executing: {sql_query}")
    try:
        results = engine.execute_sql(sql_query)
        context = f"Analisi deterministica (File: {os.path.basename(latest_bom_path)}):\n{results}"
    except Exception as e:
        print(f"[BOM_ERROR] {str(e)}")
        return {"context": f"Erro no processamento da BOM: {str(e)}"}
    
    return {"context": context}

def code_node(state: AgentState):
    """Nó de análise de firmware/código fonte real (RAG-based)."""
    print(f"[ORCHESTRATOR] 💻 Analisi Codice Sorgente Reale...")
    query = state["messages"][-1]
    
    # 1. Recupera blocchi di codice rilevanti dal VectorDB
    q_emb = embed_model.encode(query).tolist()
    # Aumentiamo k per avere più contesto del codice
    context_data = db.search(q_emb, k=5) 
    
    if not context_data:
        return {"context": "Errore: Nessun frammento di codice trovato nel database. Ingerisci un repository prima."}

    context_parts = []
    for item in context_data:
        # Filtriamo per assicurarci che siano frammenti di codice (solitamente hanno estensioni .c, .py, .h)
        context_parts.append(f"[FILE: {item.get('page', 'Unknown')}] {item['text']}")
    
    context = "\n---\n".join(context_parts)
    
    prompt = f"Analise o seguinte trecho de firmware/código da R&D PLATFORM:\n{context}\n\nTarefa: {query}\n\nInstrução: Baseie sua resposta estritamente no código fornecido. Responda no idioma: {state['language']}"
    answer = call_gemma(prompt, "Você é um Engenheiro de Firmware Sênior da R&D PLATFORM, especialista em análise estática e lógica de controle.")
    return {"context": answer}

def manual_node(state: AgentState):
    """Geração de manuais técnicos reais baseada em dados indexados."""
    print(f"[ORCHESTRATOR] 📖 Generazione Manuale Tecnico Reale...")
    query = state["messages"][-1]
    
    # 1. Recupero contesto per il manuale
    q_emb = embed_model.encode(query).tolist()
    context_data = db.search(q_emb, k=10) # Maggiore contesto per documentazione estesa
    
    context_parts = [item['text'] for item in context_data]
    context = "\n---\n".join(context_parts)
    
    # 2. Generazione Strutturata
    prompt = f"""
    Com base no projeto R&D PLATFORM e nos seguintes dados técnicos:
    {context}
    
    Crie um Manual Técnico estruturado para: {query}
    Inclua:
    - Introdução
    - Arquitetura de Sistema
    - Instruções de Operação/Implementação
    - Protocolos de Segurança
    
    Idioma: {state['language']}
    """
    final_manual = call_gemma(prompt, "Você é um Escritor Técnico Sênior e Engenheiro de Sistemas da R&D PLATFORM.")
    
    # Persistência no disco para o usuário baixar
    manual_filename = f"manual_gerado_{query.replace(' ', '_')[:20]}.md"
    manual_path = os.path.join("manuals", manual_filename)
    with open(manual_path, "w", encoding="utf-8") as f:
        f.write(final_manual)
    
    print(f"[MANUAL_GEN] Real manual saved to {manual_path}")
    return {"context": f"Manual técnico gerado com sucesso baseado na base de conhecimento real.\n\nArquivo salvo em: {manual_path}\n\n{final_manual}"}

def route_edge(state: AgentState):
    if state["intent"] == "manual":
        return "manual_node"
    if state["intent"] == "code":
        return "code_node"
    return "rag_node" if state["intent"] == "rag" else "bom_node"

def build_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("router", router_node)
    workflow.add_node("rag_node", rag_node)
    workflow.add_node("bom_node", bom_node)
    workflow.add_node("code_node", code_node)
    workflow.add_node("manual_node", manual_node)
    
    workflow.set_entry_point("router")
    workflow.add_conditional_edges("router", route_edge)
    workflow.add_edge("rag_node", END)
    workflow.add_edge("bom_node", END)
    workflow.add_edge("code_node", END)
    workflow.add_edge("manual_node", END)
    return workflow.compile()
