# Okolab R&D Platform: Industrial Deployment Guide

## 🔬 Philosophy: Zero-Cloud High Fidelity
This platform is an **Air-Gapped Engineering Intelligence** system. It operates on the principle of **Thermodynamic Efficiency**—minimizing data entropy while maximizing deterministic output. Designed by **Thiago C. Mendonça**, it represents the intersection of Theoretical Physics and Senior Software Architecture.

---

## 🛠️ Prerequisites
- **Docker Engine** (Linux/WSL2 context)
- **Ollama** (Local Inference Engine)
- **Nvidia GPU** (Recommended for Whisper/Sentence-Transformers performance)

---

## 🚀 Rapid Deployment

### 1. Model Preparation (Ollama)
The orchestrator relies on the **Gemma** architecture for semantic routing and SQL translation. Pull the weights locally:
```bash
ollama pull gemma:2b
```

### 2. Environment Configuration
Ensure `PYTHONPATH` is correctly mapped for the internal graph modules:
```bash
# Within the project root
export PYTHONPATH=$PYTHONPATH:$(pwd)/backend/src
```

### 3. Container Orchestration
The system utilizes a multi-stage Docker build to ensure zero-overhead in production.
```bash
docker-compose up --build -d
```
The platform will be exposed at:
- **Frontend**: `http://localhost:5173`
- **Backend API**: `http://localhost:8000`

---

## 📐 Internal Architecture

### Semantic Router (The Brain)
The system uses a **State-Graph (LangGraph)** to route requests. Unlike heuristic-based systems, it performs a **First-Principles Analysis** of the user query to decide whether to trigger the **Deterministic BOM Engine** or the **Semantic RAG Node**.

### BOM Engine (Deterministic CAD)
Utilizes **IfcOpenShell** for 3D metadata extraction and **Polars (Rust)** for sub-millisecond query execution on construction data.

### RAG Node (Vector Integrity)
Powered by **SQLite-Vec**, ensuring that technical documentation is retrieved with mathematical precision. Every response includes a **Source Attribution** (e.g., Page X of Manual Y).

---

## 🔒 Security & Privacy
- **Zero External API Calls**: All inference (Gemma) and vector searches (SQLite-Vec) happen within the container boundary.
- **Session Purge**: Every restart executes the `Tabula Rasa` protocol, wiping the ephemeral knowledge base to prevent data leakage between projects.

---
**Architected by Thiago Cordeiro Mendonça**  
*Okolab R&D - High Fidelity Engineering Platform*
