# Oko-Agent MVP Implementation Plan

## Goal
Construir o MVP on-premise "Oko-Agent" para a Okolab utilizando Gemma-4 local, SQLite Vector (sqlite-vec/sqlite-vss) para o RAG baseado na arquitetura do Orientador.IA, e Motor Determinístico (Polars) baseado no The Council v2. Realizar o download dos manuais da Okolab para vetorização.

## Phases

### Phase 1: Setup & Planning
- [x] Create planning files (task_plan, findings, progress).
- [ ] Analisar sistema de RAG do projeto Orientador.IA.
- [ ] Definir a arquitetura do SQLite Vector DB e do pipeline de ingestão.

### Phase 2: Data Acquisition (Okolab Manuals)
- [ ] Inspecionar `https://oko-lab.com/downloads/` para extrair links de PDFs.
- [ ] Fazer o download de todos os manuais para `D:\OKOlab\manuals`.

### Phase 3: RAG & DB Implementation
- [ ] Configurar o banco SQLite com plugin de vetores (sqlite-vec).
- [ ] Criar o script de ingestão, chunking e vetorização (via embeddings locais) dos manuais baixados.

### Phase 4: LangGraph & Deterministic Engine
- [ ] Construir o orquestrador (LangGraph).
- [ ] Integrar o Polars para mock de BOM.
- [ ] Integrar LLM Engine (Ollama / Gemma-4-E2B).
