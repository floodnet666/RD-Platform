# Research Findings: Oko-Agent MVP

## Vector DB Analysis
- O sistema Orientador.IA utiliza o **Qdrant** como provado pelos logs e diffs encontrados (`diff_qdrant.txt`).
- A substituição natural e serverless sugerida é o **`sqlite-vec`** (sucessor do `sqlite-vss`). Ele escreve vetores diretamente em tabelas SQLite virtuais e possui busca de similaridade ANN e exata extremamente veloz, sendo ideal para aplicações On-Premise e de borda sem depender de containers Docker separados (o que elimina uma camada de complexidade/entropia no deploy final na máquina dos pesquisadores).
- O modelo de LLM local será o Gemma-4-E2B via Ollama.

## Data Acquisition
- A página da Okolab renderiza o catálogo dinamicamente. Um parser estático extrai links diretos de PDF na superfície estrutural (ex: `flyer_selection-guide-UNO_BL3.pdf`). Isso já é suficiente para montar o índice de RAG de prova de conceito.
