# Decoupled Prompts for Multi-Agent RAG
# Fix [PROMPT-DECOUPLING]: Isolando as personalidades dos agentes

CONSTRUCTOR_PROMPT = """
Il tuo compito è formulare una risposta tecnica dettagliata basata ESCLUSIVAMENTE sul CONTESTO fornito.

CONTESTO:
{context}

DOMANDA:
{query}

RESTRIZIONE NEGATIVA GLOBALE: 
Proibito iniziare la resposta con autoidentificazione ("Come esperto...", "Ho analizzato..."), descrizioni do processo de análise ou frases de cortesia. 
La resposta deve essere puramente tecnica, factual e iniziare diretamente com a informação extraída do contexto.

Istruzioni:
1. Sii preciso e usa terminologia técnica.
2. Cita sempre a [FONTE: Página X].
3. Se mancarem informações, sinalize claramente.
"""

CRITIC_PROMPT = """
Analise a resposta fornecida e verifique:
1. Alucinações: A resposta contém fatos não presentes no CONTESTO?
2. Omissões: Foram ignoradas partes importantes do contexto?
3. Precisão: As citações das páginas estão corretas?
4. Persona: A resposta contém introduções prolixas ou autoidentificações (PROIBIDO)?

RESPOSTA PARA REVISÃO:
{answer}

CONTEXTO ORIGINAL:
{context}

Instruções:
- Se a resposta estiver perfeita, escreva 'APROVADO'.
- Caso contrário, indique as correções necessárias, especialmente removendo meta-linguagem.
"""

SYNTHESIZER_PROMPT = """
Sintetize a resposta final baseando-se na resposta original e no feedback do crítico.

PERGUNTA: {query}
CONTEXTO: {context}
RESPOSTA REVISADA: {answer}

RESTRIÇÃO MANDATÓRIA:
Inicie a resposta DIRETAMENTE com os dados técnicos. Elimine qualquer prefixo como "Aqui está a análise...", "Com base no contexto...", "Como solicitado...".
Mantenha rigorosamente as citações [FONTE: Página X].
"""
