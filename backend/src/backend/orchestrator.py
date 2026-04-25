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

def _extract_numeric_anchors_from_query(query: str) -> list[str]:
    """Extrai sequências numéricas específicas para ancoragem de contexto."""
    return re.findall(r'\b\d+(?:[.,]\d+)?\b', query)


def retriever_node(state: AgentState):
    """
    Retriever Híbrido com Isolamento de Contexto (DIRECTIVA 3).
    Filtra chunks que não contêm âncoras numéricas exactas da query.
    Fallback inteligente: se todos os chunks forem descartados, retorna os top-2 sem filtro.
    """
    print(f"[ORCHESTRATOR] 🔍 Recuperando Contexto com Ancoragem de Metadados...")
    retrieval_query = state["messages"][-1]
    q_emb = embed_model.encode(retrieval_query).tolist()
    context_data = db.search_hybrid(retrieval_query, q_emb, k=7)

    # Âncoras numéricas exactas da query (ex: '9', '3021', '100')
    numeric_anchors = _extract_numeric_anchors_from_query(retrieval_query)
    # Âncoras alfanuméricas/siglas (ex: 'PINN', 'MSE', 'N_u')
    alpha_anchors = re.findall(r'\b[A-Z]{2,}\b|N_[a-zA-Z]+', retrieval_query)
    all_anchors = numeric_anchors + alpha_anchors

    validated = []
    discarded = []
    for item in context_data:
        text = item['text']
        section = item.get("section", "N/A")

        if all_anchors:
            matched = [a for a in all_anchors if a in text]
            if not matched:
                print(f"[ORCHESTRATOR] ⚠️ Chunk descartado (Seção: '{section}') — sem âncoras: {all_anchors}")
                discarded.append(item)
                continue

        validated.append(f"[Pág.{item['page']} | Secção: {section}] {text}")

    # Fallback inteligente: evita contexto vazio que bloquearia a síntese
    if not validated:
        print(f"[ORCHESTRATOR] ⚠️ Fallback activado — usando top-2 sem filtro de âncoras.")
        validated = [f"[Pág.{item['page']} | Secção: {item.get('section', 'N/A')}] {item['text']}" for item in context_data[:2]]

    context = "\n---\n".join(validated)
    return {"context": context}

def constructor_node(state: AgentState):
    """
    Agente Construtor (DIRECTIVA 3).
    O system prompt reforça a Diretiva de Fronteira Rígida: o LLM recebe instrução
    explícita para validar a consistência sujeito/parâmetro antes de usar um fragmento.
    """
    print(f"[ORCHESTRATOR] 🛠️ Agente Construtor em ação...")
    query = state["messages"][0]
    prompt = CONSTRUCTOR_PROMPT.format(context=state["context"], query=query)
    system = (
        "És um motor de recuperação de informação técnica. "
        "Respondes apenas com dados presentes no CONTEXTO fornecido. "
        "PROIBIDO: inferir, extrapolar, ou cruzar dados de secções distintas sem ligação explícita no documento. "
        "Cada afirmação requer referência [Pág.X | Secção: Y]."
    )
    response = call_gemma(prompt, system)
    return {"messages": [response]}

def critic_node(state: AgentState):
    """Agente Crítico: Verifica consistência, alucinações e persona leakage."""
    print(f"[ORCHESTRATOR] ⚖️ Agente Crítico revisando...")
    answer = state["messages"][-1]
    prompt = CRITIC_PROMPT.format(answer=answer, context=state["context"])
    system = (
        "És um auditor de precisão factual. "
        "Verifica se cada afirmação da resposta tem suporte no contexto e se os parâmetros numéricos coincidem exactamente. "
        "Sinaliza qualquer cruzamento indevido de secções distintas."
    )
    feedback = call_gemma(prompt, system)
    return {"messages": [feedback]}

def synthesizer_node(state: AgentState):
    """Agente Sintetizador: Consolida a resposta final com densidade máxima e zero persona."""
    print(f"[ORCHESTRATOR] 🎤 Agente Sintetizador finalizando...")
    query = state["messages"][0]
    critic_feedback = state["messages"][-1]
    prompt = SYNTHESIZER_PROMPT.format(query=query, context=state["context"], answer=critic_feedback)
    system = (
        "Consolida a resposta aplicando as correcções do crítico. "
        "Inicia DIRECTAMENTE com os dados técnicos. "
        "Zero introduções. Zero autoidentificação. "
        "Cada facto com referência inline [Pág.X | Secção: Y]."
    )
    final_response = call_gemma(prompt, system)
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
