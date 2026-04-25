# Okolab R&D Platform - Documentação Técnica do Motor RAG Pro-Grade

Esta documentação descreve as técnicas avançadas e ferramentas implementadas no motor de RAG (Retrieval-Augmented Generation) da plataforma.

## 1. Estratégia de Ingestão: Markdown-First & Structured Parsing
Diferente de parsers simples que extraem texto bruto, nosso sistema utiliza uma abordagem estruturada:
- **Identificação de Hierarquia**: O motor detecta títulos (Headers) baseando-se em metadados de fonte (tamanho, peso) e agrupamento por linha.
- **Line-Unit Reconstruction**: Para evitar a fragmentação típica de PDFs (onde palavras de um título grande são fatiadas), o sistema reconstrói a linha como uma unidade semântica antes da classificação.
- **Heuristic Header Healing**: Filtros Regex (`sanitize_markdown`) fundem títulos fragmentados, garantindo que o contexto hierárquico chegue limpo ao banco de dados.
- **Lineage Estrito**: Cada fragmento de texto (chunk) é indexado com metadados de página e o nome da seção (`section_name`), permitindo rastreabilidade total da fonte.

## 2. Motor de Busca Híbrida (Hybrid Search)
O sistema combina o melhor de dois mundos para mitigar as limitações da busca puramente semântica:
- **Busca Densa (Vetorial)**: Utiliza `sentence-transformers` (modelo GTE ou similar) e `sqlite-vec` para capturar intenção e similaridade conceitual.
- **Busca Esparsa (Lexical)**: Utiliza `SQLite FTS5` com algoritmo BM25 para garantir a recuperação de termos técnicos exatos (ex: "50 hPa", "q=500") que embeddings podem diluir.
- **RRF (Reciprocal Rank Fusion)**: Os resultados de ambos os motores são fundidos matematicamente para priorizar documentos que aparecem no topo de ambos os rankings, equilibrando precisão e abrangência.

## 3. Orquestração Multi-Agente (Paradigma de Debate)
O processamento da resposta não é linear, mas sim um grafo de decisão (`LangGraph`):
- **Query Rewriter / HyDE**: Antes da busca, a pergunta do usuário é expandida com termos técnicos e uma resposta hipotética para melhorar o alinhamento com a base de conhecimento.
- **Agente Construtor**: Formula a resposta técnica inicial baseada estritamente no contexto recuperado.
- **Agente Crítico (Auditoria)**: Revisa a resposta em busca de "alucinações" (informações fora do contexto) e valida a precisão das citações de página.
- **Agente Sintetizador**: Consolida o debate em uma resposta final polida e validada, garantindo o tom profissional e técnico.

## 4. Infraestrutura e Segurança
- **Zero-Bloat Persistence**: Uso de `SQLite` com extensões modernas para busca vetorial e FTS5, evitando a dependência de bancos de dados externos pesados.
- **Local-First**: Processamento de embeddings e lógica de orquestração realizados localmente (ou via containers), garantindo privacidade dos dados de R&D.
- **Docker Named Volumes**: Persistência garantida da base de conhecimento através de volumes nomeados, evitando problemas de I/O e permissões em ambientes Windows/WSL.

## 5. Protocolo de Testes (TDD)
- **Suíte de Testes Automatizados**: Localizados em `backend/tests/`, cobrem desde a extração estruturada até a eficácia da busca híbrida em termos técnicos "trick questions".
- **Reset de Sessão (Tabula Rasa)**: Comando de startup que garante um ambiente limpo para cada ciclo de desenvolvimento, evitando contaminação de dados (Data Leakage).
