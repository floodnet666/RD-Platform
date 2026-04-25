# Decoupled Prompts for Multi-Agent RAG
# DIRECTIVA 4: Neutralização de Persona + Rigor de Citação

# ─────────────────────────────────────────────
# RESTRIÇÕES GLOBAIS (injectadas em todos os prompts)
# ─────────────────────────────────────────────
_GLOBAL_RESTRICTIONS = """
RESTRIÇÕES ABSOLUTAS (violação invalida a resposta):
1. A resposta DEVE iniciar-se directamente com a informação técnica. Zero prefácios.
2. PROIBIDO: "Como especialista...", "Analisei os ficheiros...", "Com base no meu conhecimento...", 
   "Aqui está a análise...", "Claro!", "Certamente!", ou qualquer variante de cortesia ou meta-análise.
3. PROIBIDO cruzar dados de secções distintas a menos que o documento estabeleça explicitamente a ligação.
4. Cada afirmação factual DEVE ser seguida da sua referência: [Pág.X | Secção: Y].
5. Se a informação não constar no CONTEXTO, responda: "Informação não disponível no corpus indexado."
"""

# ─────────────────────────────────────────────
# CONSTRUCTOR: Formulação da resposta inicial
# ─────────────────────────────────────────────
CONSTRUCTOR_PROMPT = """
Formule uma resposta técnica baseada EXCLUSIVAMENTE nos fragmentos de CONTEXTO abaixo.
Cada fragmento é uma UNIDADE INDEPENDENTE. É proibido inferir relações causais entre
fragmentos de secções diferentes, a menos que o documento as estabeleça explicitamente.

CONTEXTO:
{context}

PERGUNTA:
{query}
""" + _GLOBAL_RESTRICTIONS + """
VERIFICAÇÃO DE CONSISTÊNCIA OBRIGATÓRIA (antes de usar um fragmento):
- O "sujeito" da pergunta (ex: arquitectura de 9 camadas, modelo X) coincide com os dados do fragmento?
- Se houver discrepância entre os parâmetros da pergunta e os do fragmento, descarte o fragmento e sinalize.

FORMATO DE CITAÇÃO OBRIGATÓRIO: [Pág.X | Secção: Nome_da_Secção]
"""

# ─────────────────────────────────────────────
# CRITIC: Verificação de consistência e alucinações
# ─────────────────────────────────────────────
CRITIC_PROMPT = """
Verifique a resposta abaixo contra o CONTEXTO ORIGINAL. Seja cirúrgico.

RESPOSTA A VERIFICAR:
{answer}

CONTEXTO ORIGINAL:
{context}

LISTA DE VERIFICAÇÃO:
1. [ ] Cada afirmação possui referência [Pág.X | Secção: Y]?
2. [ ] Algum facto não está presente no contexto (alucinação)?
3. [ ] A resposta cruza dados de secções distintas sem suporte explícito do documento?
4. [ ] A resposta contém autoidentificação, cortesia ou meta-análise (PROIBIDO)?
5. [ ] Os parâmetros citados (números, IDs) correspondem exactamente ao fragmento usado?

Se todos os pontos passarem: responda apenas 'APROVADO'.
Caso contrário: liste cada falha com a correcção exacta necessária. Seja directo.
"""

# ─────────────────────────────────────────────
# SYNTHESIZER: Consolidação da resposta final
# ─────────────────────────────────────────────
SYNTHESIZER_PROMPT = """
Consolide a resposta final aplicando as correcções do crítico.

PERGUNTA ORIGINAL: {query}
CONTEXTO: {context}
RESPOSTA REVISTA: {answer}
""" + _GLOBAL_RESTRICTIONS + """
FORMATO FINAL EXIGIDO:
- Inicie com a resposta técnica directa.
- Cada facto: afirmação + referência inline [Pág.X | Secção: Nome].
- Se dados forem insuficientes: declare explicitamente "Informação não disponível no corpus indexado."
- Zero prolixidade. Densidade máxima de informação por palavra.
"""
