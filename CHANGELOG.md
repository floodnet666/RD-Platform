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

---

## [2026-04-25] Refactoring: Arquitectura RAG e Engenharia de Contexto

### D1 — Camada de Ingestão: Consolidação de Estrutura
- **Arquivo**: `backend/src/backend/pdf_extractor.py`
- **Mudança**: Reescrita completa. Novo algoritmo `_merge_consecutive_headers` com look-ahead multi-nível (`#`, `##`, `###`). Funções auxiliares `_is_terminal_punctuation` extraídas.
- **Detalhe**: Cada bloco extrai e propaga `current_section` para todos os chunks da página, garantindo zero chunks órfãos de contexto hierárquico.

### D2 — Camada de Recuperação: Refinamento de Pesquisa Híbrida
- **Arquivo**: `backend/src/backend/vector_db.py`
- **Mudança**: Reescrita completa. Novo módulo de classificação `_compute_lexical_boost` (5 padrões regex), boost calibrado a +30% (1.30). Nova função `_extract_numeric_anchors` para bónus de ranking proporcional.
- **Detalhe**: Chunks com âncoras numéricas exactas ganham `+0.05 * matched` no score RRF, sem descartar chunks sem âncoras (evita bloqueio em queries abertas).

### D3 — Camada de Síntese: Isolamento e Validação Lógica
- **Arquivo**: `backend/src/backend/orchestrator.py`
- **Mudança**: `retriever_node` reescrito com ancoragem numérica + alfanumérica separadas, fallback para top-2 se contexto ficar vazio. `constructor_node`, `critic_node`, `synthesizer_node`: system prompts explícitos com Diretiva de Fronteira Rígida e Verificação de Consistência de Sujeito/Parâmetro.
- **Detalhe**: Helper `_extract_numeric_anchors_from_query` isolado. Formato de citação unificado `[Pág.X | Secção: Y]`.

### D4 — Engenharia de Output: Neutralização e Persona
- **Arquivo**: `backend/src/backend/prompts/rag_prompts.py`
- **Mudança**: Reescrita completa. `_GLOBAL_RESTRICTIONS` extraídas como constante partilhada pelos 3 prompts. Checklist estruturada no `CRITIC_PROMPT`. Formato `[Pág.X | Secção: Nome]` imposto em todos os prompts.
- **Detalhe**: Proibição explícita de 10+ padrões de persona leakage. Fallback declarativo para informação ausente do corpus.

