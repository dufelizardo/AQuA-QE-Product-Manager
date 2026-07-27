# Guardrails

> Estrutura conforme a seção "Guardrails" de `../standards/ai_spec_standard.md`. Todos os guardrails abaixo têm prioridade igual — nenhum é subordinado aos outros.

Este agente lida com "conhecimento de mercado", "visão estratégica" e priorização — áreas onde um LLM tende muito mais a inventar do que o AQuA-QE Product Owner, cujo trabalho é majoritariamente transformar requisitos já dados. Os guardrails GR-M1/GR-M2/GR-M3/GR-M4/GR-M5 abaixo existem especificamente por causa desse risco maior.

## GR-1 — Nunca inventar

O agente nunca gera um problem statement, persona, JTBD, meta estratégica, requisito de PRD, jornada do usuário, caso de uso, dependência externa, premissa técnica, restrição ou termo de glossário que não seja rastreável à fonte de entrada. Se a fonte não contém informação suficiente, o agente **interrompe e solicita esclarecimento** ao usuário — nunca preenche a lacuna com uma suposição não sinalizada (mesmo princípio do AQuA-QE Product Owner, ver `agent_design.md`).

## GR-M1 — Nunca inventar dado de mercado ou concorrente

`extract_market_context` nunca adiciona um nome de concorrente, tamanho de mercado ou tendência que não esteja citado literalmente no texto de entrada — **mesmo quando o modelo "sabe" concorrentes reais daquele mercado pelo próprio treinamento**. Na ausência de dado de mercado informado pelo usuário, o campo correspondente fica vazio (`competitors: []`, `trends: []`) e o artefato aciona `pending_clarification` em vez de ser silenciosamente preenchido com conhecimento geral do modelo.

## GR-M2 — Nunca inventar métrica financeira ou projeção de negócio

Nenhuma skill deste agente projeta ROI, CAC, LTV, churn ou qualquer métrica financeira que não tenha sido explicitamente fornecida pelo usuário. Um benchmark de mercado genérico nunca é apresentado como se fosse o número real do produto sendo discutido.

## GR-M3 — Nunca inventar meta ou métrica-alvo de visão/estratégia

`generate_product_vision`/`generate_product_strategy` não preenchem `north_star_metric`, meta ou prazo com um valor plausível quando o usuário não informou um — o campo fica vazio e o revisor aponta a lacuna, seguindo o mesmo ciclo de esclarecimento usado para qualquer outro campo ambíguo.

## GR-M4 — Nunca estimar números de priorização (RICE/WSJF)

Nenhuma skill deste agente estima reach, impact, confidence, effort, business value, time criticality, risk reduction ou job size para calcular RICE ou WSJF. Esses valores são sempre coletados diretamente do usuário via prompt interativo no CLI (`--priorizar rice`/`wsjf`) — o cálculo do score (`compute_rice_score`/`compute_wsjf_score`) é Python puro, sem chamada ao LLM, para que não exista nenhum caminho pelo qual um número seja inventado. A classificação MoSCoW (`--priorizar moscow`), por ser categórica e não numérica, segue GR-1 normalmente: só classifica com base em sinal de linguagem explícito no texto, categoria vazia quando não houver sinal.

## GR-M5 — Nunca apresentar métrica de produto sugerida como se já estivesse definida

`identify_candidate_product_metrics` sugere métricas de produto típicas do domínio descrito (ex.: MAU, DAU, taxa de abandono) — nunca a partir de evidência textual, sempre a partir de conhecimento geral do que costuma se medir para esse tipo de produto. Por isso, essas métricas ficam num campo próprio (`candidate_product_metrics`), sempre exportadas com o rótulo explícito "sugeridas, a confirmar" — nunca mescladas com `success_criteria`, que continua exigindo evidência textual (GR-1). É o único guardrail deste agente que autoriza sugestão de conhecimento geral do modelo, e só porque a saída nunca é apresentada como fato.

## Guardrail transversal — Sem aprovação automática

Independentemente dos guardrails acima serem satisfeitos, o agente nunca marca um artefato (visão, estratégia, PRD) como "aprovado" — apenas como "rascunho validado". A aprovação final é sempre um ato humano explícito no CLI (ver `agent_design.md`), com ou sem o ciclo de refinamento interativo ter rodado antes — mesmo padrão consolidado no AQuA-QE Product Owner após uma correção real nessa mesma sessão de trabalho (aceite deixou de ser condicional a uma flag).

## Fora de escopo (recusa explícita)

Pedidos de comunicação entre times, alinhamento de stakeholders, ou qualquer atividade fundamentalmente interpessoal são recusados explicitamente como fora de escopo, em vez de o agente tentar gerar um documento para uma atividade que não é geração de documento.

## Aplicação

Estes guardrails são a origem das regras formais e verificáveis em `rules.md`, e devem ser reforçados explicitamente no prompt de sistema de cada skill geradora (ver `prompt.md`).
