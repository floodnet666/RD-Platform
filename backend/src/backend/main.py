from fastapi import FastAPI, UploadFile, File, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import os
import git
from backend.orchestrator import build_graph
from backend.pdf_extractor import extract_text_from_pdf
from backend.chunker import chunk_text
from backend.vector_db import VectorDB
from backend.code_parser import parse_source_code
from backend.ifc_parser import IFCParser
from backend.bom_engine import BOMEngine
from sentence_transformers import SentenceTransformer

# Inicialização do Servidor de Produção R&D PLATFORM
app = FastAPI(title="R&D PLATFORM API")

# Configuração de CORS para o Dashboard R&D PLATFORM
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicialização do Orquestrador LangGraph (Singleton)
graph = build_graph()
model_path = os.getenv("EMBEDDING_MODEL_PATH", "all-MiniLM-L6-v2")
model = SentenceTransformer(model_path)
db = VectorDB("R&D PLATFORM_rag.db")

def reset_session():
    """Garantisce una sessione pulita: elimina file manuali e resetta il DB."""
    print("[SYSTEM] Esecuzione Reset Sessione...")
    
    # 1. Pulizia file fisici
    if os.path.exists("manuals"):
        for f in os.listdir("manuals"):
            file_path = os.path.join("manuals", f)
            try:
                if os.path.isfile(file_path): os.unlink(file_path)
            except Exception as e: print(f"Errore durante la pulizia di {f}: {e}")
            
    # 2. Reset del Database Vettoriale (Mantenendo la struttura)
    db = VectorDB("R&D PLATFORM_rag.db")
    try:
        db.conn.execute("DELETE FROM chunks")
        db.conn.execute("DELETE FROM chunks_vec")
        db.conn.execute("VACUUM")
        db.conn.commit()
    except Exception as e:
        print(f"Avviso Reset DB: {e} - Re-inizializzazione...")
        db._init_db()
    print("[SYSTEM] Tabula Rasa: Tutta la conoscenza precedente è stata epurata.")

@app.on_event("startup")
async def startup_event():
    reset_session()

class ChatQuery(BaseModel):
    message: str
    lang: str = "it"

class RepoRequest(BaseModel):
    repo_url: str
    token: str = None

@app.post("/upload")
async def upload_asset(file: UploadFile = File(...)):
    """
    Endpoint para ingestão dinâmica de manuais e código.
    """
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    filename = file.filename.lower()
    
    try:
        if filename.endswith(".pdf"):
            # Processamento RAG Dinâmico
            model_path = os.getenv("EMBEDDING_MODEL_PATH", "all-MiniLM-L6-v2")
            model = SentenceTransformer(model_path)
            db = VectorDB("R&D PLATFORM_rag.db")
            pages = extract_text_from_pdf(temp_path)
            for p in pages:
                chunks = chunk_text(p["text"])
                for c in chunks:
                    embedding = model.encode(c).tolist()
                    db.insert(c, embedding, p["page"], source=file.filename)
            return {"status": "success", "type": "pdf", "message": f"Manual {file.filename} indexado."}
        
        elif filename.endswith(".ifc"):
            # Processamento de Engenharia BIM -> BOM
            parser = IFCParser(temp_path)
            df = parser.to_dataframe()
            # Salva como base para o motor BOM da R&D PLATFORM
            bom_path = os.path.join("manuals", f"bom_{file.filename}.csv")
            df.write_csv(bom_path)
            return {"status": "success", "type": "csv", "message": f"Modelo IFC {file.filename} convertido em BOM de materiais."}
        
        elif any(filename.endswith(ext) for ext in [".c", ".py", ".h", ".cpp"]):
            # Ingestão Real de Código-Fonte Unitário
            db = VectorDB("R&D PLATFORM_rag.db")
            model = SentenceTransformer('all-MiniLM-L6-v2')
            with open(temp_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                blocks = parse_source_code(content, filename.split(".")[-1])
                for block in blocks:
                    emb = model.encode(block).tolist()
                    db.insert(block, emb, 1, source=file.filename)
            
            # Persistência opcional no disco para listagem
            manual_code_path = os.path.join("manuals", file.filename)
            shutil.copy(temp_path, manual_code_path)
            
            return {"status": "success", "type": "code", "message": f"Código {file.filename} indexado e disponível para o Agente R&D."}
            
        return {"status": "unsupported", "message": "Formato não suportado para ingestão automática."}
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.get("/assets")
async def list_assets():
    """
    Lista ativos baseados na realidade física do disco (pasta manuals/).
    """
    if not os.path.exists("manuals"):
        return []
        
    assets = []
    for filename in os.listdir("manuals"):
        ext = filename.split(".")[-1].lower()
        if ext in ["pdf", "ifc", "csv", "py", "c"]:
            atype = "pdf" if ext == "pdf" else "csv" if ext in ["csv", "ifc"] else "code"
            assets.append({"name": filename, "type": atype})
    
    return assets

@app.post("/clone")
async def clone_repository(req: RepoRequest):
    """
    Clona um repositório remoto (público ou privado) e ingere todo o código.
    """
    auth_url = req.repo_url
    if req.token:
        # Injeta token para repos privados: https://<token>@github.com/...
        auth_url = req.repo_url.replace("https://", f"https://{req.token}@")
        
    repo_name = req.repo_url.split("/")[-1].replace(".git", "")
    target_dir = os.path.join("temp_repos", repo_name)
    
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
        
    try:
        git.Repo.clone_from(auth_url, target_dir, depth=1)
        
        db = VectorDB("R&D PLATFORM_rag.db")
        model_path = os.getenv("EMBEDDING_MODEL_PATH", "all-MiniLM-L6-v2")
        model = SentenceTransformer(model_path)
        
        indexed_count = 0
        for root, _, files in os.walk(target_dir):
            for file in files:
                if any(file.endswith(ext) for ext in [".c", ".h", ".py", ".cpp", ".md"]):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                        blocks = parse_source_code(content, file.split(".")[-1])
                        for block in blocks:
                            emb = model.encode(block).tolist()
                            db.insert(block, emb, 1, source=f"{repo_name}/{file}")
                            indexed_count += 1
        
        return {"status": "success", "message": f"Repositório {repo_name} indexado. {indexed_count} blocos processados."}
    
    except Exception as e:
        error_msg = str(e)
        if "Authentication failed" in error_msg or "could not read Username" in error_msg or "403" in error_msg:
            return {"status": "need_token", "message": "Autenticazione fallita. Il repository sembra essere privato. Per favore, fornisci un Personal Access Token (PAT)."}
        return {"status": "error", "message": error_msg}

    finally:
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)

@app.delete("/assets/{filename}")
async def delete_asset(filename: str):
    """
    Remove um ativo e todos os seus vetores do banco de dados.
    """
    db = VectorDB("R&D PLATFORM_rag.db")
    # Deleta da tabela de metadados e a tabela vetorial limpa via rowid (se configurado trigger)
    # No sqlite-vec simples, deletamos os chunks e os vetores órfãos
    try:
        db.conn.execute("DELETE FROM chunks_vec WHERE rowid IN (SELECT id FROM chunks WHERE source_file = ?)", (filename,))
        db.conn.execute("DELETE FROM chunks WHERE source_file = ?", (filename,))
        db.conn.commit()
        return {"status": "success", "message": f"Ativo {filename} removido."}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.post("/chat")
async def chat(request: Request):
    """
    Endpoint de integração real com suporte a i18n e log de debug.
    """
    body = await request.json()
    print(f"DEBUG PAYLOAD: {body}")
    
    msg = body.get("message", "")
    lang = body.get("lang", "it")
    
    # Estado inicial do Grafo com idioma explícito
    initial_state = {
        "messages": [msg],
        "intent": "",
        "context": "",
        "language": lang
    }
    
    # Execução síncrona do Grafo (Regime de Teste Real)
    final_state = graph.invoke(initial_state)
    
    return {"response": final_state["context"]}

if __name__ == "__main__":
    import uvicorn
    print("Iniciando API de Produção na porta 8000...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
