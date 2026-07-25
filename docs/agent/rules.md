# Rules

> Estrutura conforme `../standards/rules_standard.md`. Cada regra deriva de um guardrail (`guardrails.md`) ou objetivo (`objectives.md`).

## RULE-001

- **Descrição**: nunca incluir problem statement, persona, JTBD, meta estratégica ou requisito de PRD sem origem identificável na fonte de entrada.
- **Gatilho**: geração de qualquer campo por `identify_problem_statement`, `synthesize_personas`, `extract_jobs_to_be_done`, `generate_product_vision`, `generate_product_strategy` ou `generate_prd`.
- **Ação esperada**: se a origem não for identificável, não preencher o campo — acionar RULE-004.
- **Severidade**: bloqueante.
- **Origem**: GR-1 (`guardrails.md`).

## RULE-M1

- **Descrição**: nunca incluir concorrente, tamanho de mercado ou tendência que não esteja citado literalmente no texto de entrada, mesmo que o modelo "conheça" concorrentes reais daquele mercado.
- **Gatilho**: `extract_market_context`.
- **Ação esperada**: retornar `competitors: []`/`trends: []` quando não houver dado informado; acionar `pending_clarification`, nunca preencher do conhecimento geral do modelo.
- **Severidade**: bloqueante.
- **Origem**: GR-M1 (`guardrails.md`).

## RULE-M2

- **Descrição**: nunca projetar ROI, CAC, LTV, churn ou qualquer métrica financeira não fornecida explicitamente pelo usuário.
- **Gatilho**: qualquer skill que estruture dados de negócio/financeiros.
- **Ação esperada**: deixar o campo vazio e sinalizar a lacuna em vez de usar um benchmark de mercado genérico como se fosse o número real do produto.
- **Severidade**: bloqueante.
- **Origem**: GR-M2 (`guardrails.md`).

## RULE-M3

- **Descrição**: nunca estimar reach, impact, confidence, effort, business value, time criticality, risk reduction ou job size para calcular RICE/WSJF — esses valores só podem vir de entrada explícita do usuário.
- **Gatilho**: `--priorizar rice`/`--priorizar wsjf`.
- **Ação esperada**: coletar cada valor via prompt interativo no CLI; `compute_rice_score`/`compute_wsjf_score` só fazem o cálculo aritmético, nunca uma chamada ao LLM.
- **Severidade**: bloqueante.
- **Origem**: GR-M4 (`guardrails.md`).

## RULE-002

- **Descrição**: todo artefato (visão, estratégia, PRD) deve ser validado pelo checklist automático correspondente antes de ser apresentado ao usuário.
- **Gatilho**: conclusão de `generate_product_vision`/`generate_product_strategy`/`generate_prd`.
- **Ação esperada**: executar `validate_product_vision`/`validate_product_strategy`/`validate_prd`; se reprovar, não apresentar o artefato como pronto.
- **Severidade**: bloqueante.
- **Origem**: objetivo "Qualidade verificável acima de velocidade" (`objectives.md`).

## RULE-004

- **Descrição**: quando a fonte de entrada for ambígua ou incompleta ao ponto de impedir RULE-001/RULE-M1/RULE-M2, o agente deve interromper o fluxo e solicitar esclarecimento ao usuário, explicando a lacuna encontrada.
- **Gatilho**: falha em identificar um campo obrigatório com confiança suficiente.
- **Ação esperada**: não gerar o artefato como completo; retornar mensagem apontando exatamente o que falta.
- **Severidade**: bloqueante.
- **Origem**: decisão de design em `agent_design.md`.

## RULE-005

- **Descrição**: nenhum artefato — problem statement/personas/JTBD, visão, estratégia ou PRD — é marcado como "aprovado" pelo agente, apenas como "rascunho validado". Aceite final é sempre um ato humano explícito no CLI, com ou sem o ciclo de refinamento interativo ter rodado antes.
- **Gatilho**: checklist automático (e, quando aplicável, o revisor independente) aprova o artefato.
- **Ação esperada**: rotular o estado como rascunho validado (ver `output_schema.md`) e aguardar aceite humano explícito antes de qualquer exportação.
- **Severidade**: bloqueante.
- **Origem**: guardrail transversal "Sem aprovação automática" (`guardrails.md`).

## RULE-006

- **Descrição**: toda saída deve seguir a estrutura dos templates de `../../knowledge/templates/`, independentemente do formato da entrada.
- **Gatilho**: `export_markdown`/`format_prd_markdown`.
- **Ação esperada**: rejeitar/corrigir formatações que não sigam o template correspondente antes de exportar.
- **Severidade**: recomendação.
- **Origem**: objetivo "Consistência de formato" (`objectives.md`).

## RULE-007

- **Descrição**: pedidos de comunicação entre times, alinhamento de stakeholders ou qualquer atividade interpessoal são recusados explicitamente como fora de escopo.
- **Gatilho**: entrada do usuário pedindo esse tipo de atividade.
- **Ação esperada**: informar que está fora do escopo do agente, em vez de tentar gerar um documento de qualquer forma.
- **Severidade**: recomendação.
- **Origem**: guardrail "Fora de escopo" (`guardrails.md`).

## Resolução de conflitos

RULE-001, RULE-M1, RULE-M2, RULE-M3, RULE-002, RULE-004 e RULE-005 são bloqueantes e têm prioridade sobre RULE-006 e RULE-007 (recomendações). Nenhuma regra bloqueante pode ser contornada para acelerar a entrega.
