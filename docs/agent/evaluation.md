# Evaluation

> Estrutura conforme `../standards/evaluation_standard.md`. Define como medir se o agente está cumprindo `objectives.md` e respeitando `guardrails.md`.

## Casos de teste manuais (fumaça)

1. **Descoberta a partir de texto rico** — texto de entrada com problema, usuários afetados, ao menos uma persona implícita e um concorrente citado. Esperado: `identify_problem_statement`/`synthesize_personas`/`extract_jobs_to_be_done`/`extract_market_context` retornam campos preenchidos, todos rastreáveis ao texto de entrada.
2. **Descoberta a partir de texto pobre** — texto de entrada só com uma ideia de produto, sem problema/persona/concorrente explícitos. Esperado: campos de descoberta retornam vazios (string/lista vazia), sem inventar conteúdo, sem bloquear o restante do pipeline.
3. **Visão aprovada de primeira** — `review_product_vision` aprova sem apontamentos. Esperado: `status = draft_validated`, ciclo de clarifying questions não é acionado.
4. **Visão reprovada, refinada e aceita** — `review_product_vision` reprova; usuário responde às perguntas de esclarecimento; `refine_product_vision` incorpora as respostas preservando o que não foi perguntado (mesmo cuidado do `refine_prd` do PO, corrigido após bug real). Esperado: `status` final `accepted` só após confirmação humana explícita.
5. **Guardrail GR-M1 (mercado)** — texto de entrada não cita nenhum concorrente. Esperado: `extract_market_context` retorna `competitors: []`, nunca preenche com concorrentes reais que o modelo "conhece" do mercado citado.
6. **Guardrail GR-M3 (métrica de visão/estratégia)** — texto de entrada não define uma métrica-alvo. Esperado: `north_star_metric`/`goals[].target` ficam vazios, sem valor numérico inventado; `status = pending_clarification`.
7. **PRD a partir de descoberta+visão+estratégia já aceitas** — `contexto` populado. Esperado: `generate_prd` usa esse contexto para enriquecer os campos do PRD, sem contradizer a visão/estratégia já aceitas.
8. **PRD a partir de ideia crua, sem contexto** — `contexto=None`. Esperado: comportamento equivalente ao `--modo prd` atual do AQuA-QE Product Owner (compatibilidade do caminho simples).
9. **Handoff PM → PO** — `format_prd_markdown` exporta um `prd.md`; esse arquivo é lido com sucesso por `run.py --modo lote --arquivo prd.md` no repositório do Product Owner, sem nenhuma adaptação manual.
10. **Nenhuma aceitação automática** — em todos os casos acima, `status = accepted` só é setado após uma pergunta explícita respondida pelo usuário no CLI, nunca automaticamente pela lógica do agente.
11. **Enriquecimento de profundidade do PRD** — texto de entrada rico o suficiente para sustentar personas/jornadas/casos de uso/dependências. Esperado: os 10 campos de profundidade preenchidos, todos rastreáveis ao texto (GR-1), exceto `candidate_product_metrics` (GR-M5, ver caso 12).
12. **Guardrail GR-M5 (métricas candidatas)** — qualquer texto de entrada. Esperado: `identify_candidate_product_metrics` pode sugerir métricas típicas de mercado mesmo sem citação literal no texto (única exceção deliberada a GR-1), mas sempre no campo `candidate_product_metrics`, nunca mesclado com `success_criteria`; `format_prd_markdown` sempre rotula a seção como "sugeridas, a confirmar".
13. **Enriquecimento sobrevive ao refinamento** — PRD reprovado, refinado com respostas do usuário que alteram um campo central mapeado para um ou mais campos de profundidade (ver `_DEPENDENCIAS_PROFUNDIDADE` em `skills.md`). Esperado: os campos de profundidade afetados são re-derivados a partir do PRD já refinado (`refine_prd_draft`), não ficam com valores da geração original; campos de profundidade cujo mapa não foi afetado preservam o valor já existente, por design (refino seletivo, ver issue #10, fechada).

## Métricas de acompanhamento

- Taxa de interrupção por ambiguidade (`pending_clarification`) por artefato — não é uma métrica a minimizar às cegas; interrupção correta é o comportamento esperado quando a fonte é pobre (ver objetivo 1 em `objectives.md`).
- Número médio de rodadas de refinamento até aceite, por artefato (visão/estratégia/PRD).
- Zero ocorrências, em revisão manual de amostra, de dado de mercado/financeiro/meta não rastreável ao texto de entrada (auditoria de GR-M1/GR-M2/GR-M3).

## Regressão automatizada

Coberta por `uv run pytest` — ver `skills.md` para a lista de skills e seus testes correspondentes. Testes de guardrail (GR-M1, preservação de campo em refinamento) são explícitos, não implícitos, mesmo padrão dos testes de regressão adicionados ao Product Owner nesta mesma linha de trabalho.
