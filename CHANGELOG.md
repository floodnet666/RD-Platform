# CHANGELOG - OKOlab RD Platform

## [2026-04-25] Refinamento de Robustez do Pipeline RAG

### 1. Saneamento de Ingestão (Header Merging)
- **Arquivo**: `backend/src/backend/pdf_extractor.py`
- **Mudança**: Atualização da função `sanitize_markdown`.
- **Detalhe**: Implementada lógica de pós-processamento que aglutina headers Markdown (`##`) consecutivos apenas se o header anterior não possuir pontuação terminal (`.!?:;`).
- **Motivo**: Eliminar fragmentação de títulos de grande formato que poluíam a estrutura do contexto.

### 2. Implementação de Rigor Semântico (Context Isolation)
- **Arquivo**: `backend/src/backend/orchestrator.py`
- **Mudança**: Injeção de "Validação de Âncoras" no `retriever_node`.
- **Detalhe**: Adicionada extração de âncoras (IDs, números, termos alfanuméricos) da query e verificação de coabitação no chunk recuperado.
- **Motivo**: Impedir contaminação lógica entre seções distintas (ex: usar dados do Modelo A para responder sobre o Modelo B).

### 3. Purificação de Resposta (Persona Erasure)
- **Arquivo**: `backend/src/backend/prompts/rag_prompts.py`
- **Mudança**: Reescrita completa dos templates `CONSTRUCTOR_PROMPT`, `CRITIC_PROMPT` e `SYNTHESIZER_PROMPT`.
- **Detalhe**: Removidas instruções de persona ("Sei o Ingegnere..."). Adicionada "Restrição Negativa Global" para início direto e técnico da resposta, proibindo descrições de processo ou cortesias.
- **Motivo**: Eliminar vazamento de meta-linguagem e introduções prolixas.

### 4. Ajuste de Pesos na Busca Híbrida
- **Arquivo**: `backend/src/backend/vector_db.py`
- **Mudança**: Modificação do método `search_hybrid`.
- **Detalhe**: Implementado `lexical_boost` (peso 1.5) na componente BM25 (FTS5) quando a query contém termos técnicos, sequências alfanuméricas ou é altamente específica.
- **Motivo**: Corrigir falhas na recuperação de termos técnicos raros e fórmulas que a componente vetorial tendia a diluir.

### 5. Hotfix: Missing Module Import
- **Arquivo**: `backend/src/backend/vector_db.py`
- **Mudança**: Adicionado `import re` no cabeçalho do arquivo (linhas 4-5).
- **Detalhe**: Adicionado `import re` no topo do arquivo que estava ausente e causava um `NameError` ao executar o `lexical_boost` com `re.search`.
- **Motivo**: Restaurar a funcionalidade de busca no backend que estava falhando (Internal Server Error) na etapa de detecção lexical.

### 6. Hotfix: Docker PID 1 SIGTERM Handling
- **Arquivo**: `frontend/Dockerfile`
- **Mudança**: Alteração da instrução `CMD` de `npm run dev` para a invocação direta do binário `./node_modules/.bin/vite`.
- **Detalhe**: O `npm` atuando como PID 1 interceptava o sinal `SIGTERM` gerado pelo `docker-compose stop` e o tratava como um erro anômalo (`npm error signal SIGTERM`). Substituir pelo executável direto do `vite` remove esse ruído sem perda de funcionalidade.
- **Motivo**: Eliminar falsos positivos de erro no log de shutdown do container frontend.
