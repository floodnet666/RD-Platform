from typing import TypedDict, Annotated
import operator
import os
import re
from langgraph.graph import StateGraph, END

from backend.llm_client import call_gemma
from backend.database import db, embed_model
from backend.vector_db import VectorDB
from backend.bom_engine import BOMEngine
from backend.code_parser import parse_source_code
# Decoupled Prompts
from backend.prompts.rag_prompts import CONSTRUCTOR_PROMPT, CRITIC_PROMPT, SYNTHESIZER_PROMPT

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
    - 'CODE': Analisi di file sorgente (.py, .c, .cpp), debug di firmware, spiegazione di algoritmi implementati nel codice o documentazione di API interne.
    - 'RAG': Ricerca di informazioni in manuali, PDF, datasheet o documentazione tecnica generale (es. specifiche, calibrazioni, teoria scientifica, procedure operative).
    
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

def query_rewriter_node(state: AgentState):
    """
    Query Rewriting / HyDE: Espande la query dell'utente per migliorare il retrieval.
    """
    if state.get("intent") != "rag":
        return state

    query = state["messages"][-1]
    prompt = f"""
    Sei un esperto di sistemi R&D. Riscrevi la domanda seguente per ottimizzare la ricerca semantica e lessicale.
    Aggiungi termini tecnici correlati, sinonimi o una brevissima risposta ipotetica (HyDE).
    
    Domanda: "{query}"
    
    Risposta: Fornisci SOLO la query espansa, senza commenti.
    """
    expanded_query = call_gemma(prompt, "Esperto di Information Retrieval.")
    print(f"[ORCHESTRATOR] 📝 Query Espansa: {expanded_query.strip()}")
    return {"messages": [expanded_query.strip()]}

def retriever_node(state: AgentState):
    """
    Retriever Híbrido com Context Isolation.
    [RIGOR]: Valida âncoras semânticas para evitar contaminação entre seções distintas.
    """
    print(f"[ORCHESTRATOR] 🔍 Recuperando Contexto Híbrido com Rigor Semântico...")
    retrieval_query = state["messages"][-1]
    q_emb = embed_model.encode(retrieval_query).tolist()
    context_data = db.search_hybrid(retrieval_query, q_emb, k=5)
    
    # Extrair IDs/Variáveis/Números da query para validação de âncoras
    anchors = re.findall(r'\b[A-Z0-9_\-]{2,}\b|\d+(?:\.\d+)?', retrieval_query)
    
    context_parts = []
    for item in context_data:
        text = item['text']
        section = item.get("section", "N/A")
        
        # Validação de Âncoras: Se a query tem identificadores específicos, 
        # eles devem estar presentes no chunk para serem considerados válidos.
        if anchors:
            found_anchors = [a for a in anchors if a in text]
            # Se a query cita um Modelo A, mas o chunk é do Modelo B, descartamos se não houver coabitação
            if not found_anchors and len(anchors) > 1:
                print(f"[ORCHESTRATOR] ⚠️ Descartando chunk da Seção '{section}' por falta de âncoras.")
                continue
                
        context_parts.append(f"[FONTE: Página {item['page']} | Seção: {section}] {text}")
    
    if not context_parts:
        # Fallback: se o rigor for excessivo, pegamos o melhor resultado sem filtro para não travar
        context_parts = [f"[FONTE: Página {item['page']} | Seção: {item.get('section', 'N/A')}] {item['text']}" for item in context_data[:1]]

    context = "\n---\n".join(context_parts)
    return {"context": context}

def constructor_node(state: AgentState):
    """Agente Construtor: Formula a resposta inicial."""
    print(f"[ORCHESTRATOR] 🛠️ Agente Construtor em ação...")
    query = state["messages"][0]
    prompt = CONSTRUCTOR_PROMPT.format(context=state["context"], query=query)
    response = call_gemma(prompt, "Ingegnere Construttore R&D.")
    return {"messages": [response]}

def critic_node(state: AgentState):
    """Agente Crítico: Verifica alucinações e precisão."""
    print(f"[ORCHESTRATOR] ⚖️ Agente Crítico revisando...")
    answer = state["messages"][-1]
    prompt = CRITIC_PROMPT.format(answer=answer, context=state["context"])
    feedback = call_gemma(prompt, "Revisore Critico R&D.")
    return {"messages": [feedback]}

def synthesizer_node(state: AgentState):
    """Agente Sintetizador: Consolida a resposta final."""
    print(f"[ORCHESTRATOR] 🎤 Agente Sintetizador finalizando...")
    query = state["messages"][0]
    critic_feedback = state["messages"][-1]
    # No LangGraph com operator.add, precisamos ter cuidado com a indexação
    # Mas aqui simplificamos retornando a resposta final
    
    prompt = SYNTHESIZER_PROMPT.format(query=query, context=state["context"], answer=critic_feedback)
    final_response = call_gemma(prompt, "Sintetizzatore R&D.")
    return {"messages": [final_response]}

def bom_node(state: AgentState):
    """Execução determinística Polars com arquivo CSV dinâmico."""
    print(f"[ORCHESTRATOR] 📊 Executing BOM/IFC Engine Node...")
    manual_dir = "manuals"
    if not os.path.exists(manual_dir): os.makedirs(manual_dir)
    
    files = [os.path.join(manual_dir, f) for f in os.listdir(manual_dir) if f.endswith(".csv")]
    if not files: return {"context": "Erro: Nenhuma base de dados BOM encontrada."}
    
    latest_bom_path = max(files, key=os.path.getmtime)
    engine = BOMEngine(latest_bom_path)
    query = state["messages"][-1]
    
    sql_prompt = f"Convert to SQL (table 'bom'): {query}\nSchema: part_number, description, quantity, unit_price, category\nReturn ONLY SQL."
    sql_query = call_gemma(sql_prompt, "NL to SQL translator.")
    sql_clean = sql_query.replace("```sql", "").replace("```", "").strip()
    
    try:
        results = engine.execute_sql(sql_clean)
        return {"messages": [f"Analisi BOM:\n{results}"]}
    except Exception as e:
        return {"messages": [f"Errore BOM: {str(e)}"]}

def code_node(state: AgentState):
    """Análise de código real."""
    print(f"[ORCHESTRATOR] 💻 Analisi Codice Sorgente...")
    query = state["messages"][-1]
    q_emb = embed_model.encode(query).tolist()
    context_data = db.search_hybrid(query, q_emb, k=5)
    context = "\n---\n".join([f"[FILE: {item.get('page', 'N/A')}] {item['text']}" for item in context_data])
    
    prompt = f"Analise o código:\n{context}\n\nTarefa: {query}"
    answer = call_gemma(prompt, "Engenheiro de Firmware Sênior.")
    return {"messages": [answer]}

def manual_node(state: AgentState):
    """Geração de manuais técnicos."""
    print(f"[ORCHESTRATOR] 📖 Generazione Manuale...")
    query = state["messages"][-1]
    q_emb = embed_model.encode(query).tolist()
    context_data = db.search_hybrid(query, q_emb, k=10)
    context = "\n---\n".join([item['text'] for item in context_data])
    
    prompt = f"Crie um Manual Técnico para: {query}\nBase de dados:\n{context}"
    final_manual = call_gemma(prompt, "Escritor Técnico Sênior.")
    return {"messages": [final_manual]}

def build_graph():
    workflow = StateGraph(AgentState)
    workflow.add_node("router", router_node)
    workflow.add_node("query_rewriter", query_rewriter_node)
    workflow.add_node("retriever", retriever_node)
    workflow.add_node("constructor", constructor_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("synthesizer", synthesizer_node)
    
    workflow.add_node("bom", bom_node)
    workflow.add_node("manual", manual_node)
    workflow.add_node("code", code_node)

    workflow.set_entry_point("router")
    
    workflow.add_conditional_edges(
        "router",
        lambda x: x["intent"],
        {
            "rag": "query_rewriter",
            "bom": "bom",
            "manual": "manual",
            "code": "code"
        }
    )

    # Fluxo de Debate RAG
    workflow.add_edge("query_rewriter", "retriever")
    workflow.add_edge("retriever", "constructor")
    workflow.add_edge("constructor", "critic")
    workflow.add_edge("critic", "synthesizer")
    workflow.add_edge("synthesizer", END)
    
    workflow.add_edge("bom", END)
    workflow.add_edge("manual", END)
    workflow.add_edge("code", END)
    
    return workflow.compile()
