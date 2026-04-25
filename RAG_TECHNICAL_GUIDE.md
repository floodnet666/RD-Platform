# Okolab R&D Platform - Deep Dive: Motor RAG Pro-Grade

Esta documentação fornece uma visão exaustiva das camadas de inteligência, recuperação e processamento que compõem o ecossistema RAG da R&D PLATFORM.

---

## 1. Ingestão Estruturada & Markdown-First (V2)
A Fase de Ingestão é o alicerce de qualquer sistema RAG. Se o dado entra "sujo", a recuperação falha.
- **Line-Unit Reconstruction**: Diferente de parsers que processam *character-by-character*, nosso parser reconstrói a geometria da linha no PDF. Se uma linha possui fontes acima de 12pt ou estilo Bold, ela é candidata a Header.
- **Header Healing (Anti-Fragmentação)**: Implementamos um algoritmo de pós-processamento que detecta títulos quebrados visualmente no PDF (ex: títulos em múltiplas colunas ou com kerning excessivo) e os funde em um único identificador semântico. Isso evita o ruído de múltiplos `#` inúteis.
- **Sanitização Regex**: Removemos artefatos de controle, quebras de linha triplas e caracteres não-UTF8 que degradam a qualidade dos embeddings.

## 2. Busca Híbrida: A Simbiose Semântico-Lexical
A busca puramente vetorial falha em R&D porque embeddings muitas vezes não distinguem "SN-900" de "SN-901".
- **Busca Densa (Vector)**: Utiliza representação multidimensional para capturar "o que o usuário quis dizer". Excelente para perguntas conceituais.
- **Busca Esparsa (FTS5/BM25)**: Atua como uma indexação clássica de biblioteca. Se você busca por "E-212", o motor léxico garante que o documento com esse código exato seja encontrado, mesmo que o modelo de embedding ache que "Erro" é similar o suficiente a outro fragmento.
- **RRF (Reciprocal Rank Fusion)**: Aplicamos a fórmula:
  $$Score(d) = \sum_{r \in R} \frac{1}{k + r(d)}$$
  Onde $r(d)$ é a posição do documento no ranking. Isso garante que a plataforma priorize o "Equilíbrio Perfeito" — documentos que são semanticamente relevantes E contêm os termos exatos.

## 3. Orquestração Multi-Agente (Paradigma de Debate LangGraph)
A resposta final não é gerada em um único passo. Ela passa por uma "Banca Examinadora":
- **Query Rewriter (HyDE)**: O sistema gera uma resposta hipotética baseada no conhecimento interno do LLM e a usa para buscar no banco. Isso resolve o problema de perguntas curtas ou mal formuladas.
- **Agente Construtor**: Focado em síntese técnica. Ele extrai os fatos do contexto e monta a estrutura da resposta.
- **Agente Crítico (Auditor)**: Atua como um revisor impiedoso. Se o Construtor disser algo que não está explicitamente no PDF, o Crítico "devolve" a tarefa com um feedback de erro. Ele valida páginas, parágrafos e consistência.
- **Agente Sintetizador**: O maestro final. Ele pega a resposta validada e a ajusta para o tom profissional exigido pela Okolab.

## 4. Persistência Industrial
- **Named Volumes**: Utilizamos volumes Docker dedicados para a base vetorial. Isso garante que, mesmo que o container seja destruído ou atualizado, a indexação de milhares de manuais permaneça intacta.
- **Singleton Pattern**: O carregamento do modelo de embedding (100+ MB) e a conexão com o banco são feitos uma única vez no startup, garantindo latência mínima em cada chat.

---

## 5. Protocolo de Agnosticismo
O sistema foi projetado para ser **Independente de Domínio**. A inteligência reside na capacidade de processar estrutura e lógica, permitindo que a R&D PLATFORM seja aplicada com a mesma eficácia em:
- Firmware de Sensores.
- Projetos de Engenharia Civil (IFC/BIM).
- Manuais de Operação Industrial.
- Papers Científicos de IA/Física.
