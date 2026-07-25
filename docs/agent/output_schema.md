# Output Schema

> Estrutura de dados retornada pelas skills geradoras e exportada por `export_markdown`/`format_prd_markdown`. Implementada como dataclasses reais em `../../src/aqua_qe_product_manager/models/` — o JSON abaixo é a representação conceitual.

## Schema de descoberta

```
{
  "problem_statement": {
    "problem": "<string>",
    "affected_users": "<string>",
    "impact": "<string>",
    "evidence": "<string, só o que o usuário informou>",
    "source_reference": "<string>"
  },
  "personas": [
    {
      "name": "<string>",
      "description": "<string>",
      "goals": ["<string>"],
      "pain_points": ["<string>"],
      "source_reference": "<string>"
    }
  ],
  "jobs_to_be_done": [
    {
      "situation": "<string, 'Quando ...'>",
      "motivation": "<string, 'eu quero ...'>",
      "expected_outcome": "<string, 'para que ...'>",
      "source_reference": "<string>"
    }
  ],
  "market_analysis": {
    "competitors": [
      {"name": "<string>", "strengths": ["<string>"], "weaknesses": ["<string>"], "source_reference": "<string>"}
    ],
    "trends": ["<string>"],
    "market_context": "<string>",
    "status": "draft_validated | pending_clarification | accepted",
    "review_notes": ["<string>"]
  }
}
```

Todos os campos são opcionais (string ou lista vazia quando não identificável, conforme GR-1/GR-M1) — descoberta nunca bloqueia o pipeline por estar incompleta.

## Schema de visão de produto

```
{
  "statement": "<string>",
  "target_audience": "<string>",
  "differentiators": ["<string>"],
  "north_star_metric": "<string, vazio se não informado — nunca inventado (GR-M3)>",
  "status": "draft_validated | pending_clarification | accepted",
  "review_notes": ["<string>"]
}
```

## Schema de estratégia de produto

```
{
  "goals": [
    {"description": "<string>", "metric": "<string>", "target": "<string>", "timeframe": "<string>", "source_reference": "<string>"}
  ],
  "roadmap_themes": ["<string>"],
  "time_horizon": "<string>",
  "status": "draft_validated | pending_clarification | accepted",
  "review_notes": ["<string>"]
}
```

## Schema de PRD

Gerado por `generate_prd`, opcionalmente incorporando descoberta/visão/estratégia via `contexto`. **Mesmos campos exatos do `PRDDraft` do AQuA-QE Product Owner** — garante que o PRD exportado por este agente seja consumível pelo `--modo lote` do Product Owner sem nenhuma adaptação:

```
{
  "context_problem": "<string>",
  "objective": "<string>",
  "target_audience": "<string>",
  "scope": "<string>",
  "out_of_scope": "<string>",
  "functional_requirements": ["<string>"],
  "non_functional_requirements": ["<string>"],
  "success_criteria": ["<string>"],
  "risks_assumptions": ["<string>"],
  "status": "draft_validated | pending_clarification | accepted",
  "review_notes": ["<string>"]
}
```

## Valores válidos de `status`

- **`draft_validated`** — passou no checklist automático e na revisão por um segundo LLM; ainda não tem aceitação humana (ver RULE-005 em `rules.md`).
- **`pending_clarification`** — o agente interrompeu a geração por ambiguidade/incompletude na fonte (RULE-004), ou por falta de dado de mercado/financeiro que não deve ser inventado (RULE-M1/RULE-M2), ou o revisor reprovou o artefato; use o par `generate_*_clarifying_questions`/`refine_*` (ver `skills.md`) para endereçar os apontamentos.
- **`accepted`** — setado **apenas** pelo CLI (`run.py`), nunca pela lógica automática do agente, após confirmação explícita do usuário — sempre pedida, com ou sem o ciclo de refinamento.

## Formato de exportação (`export_markdown`/`format_prd_markdown`)

A saída em Markdown do PRD segue diretamente `../standards/prd_standard.md` — mesma estrutura de seções que o AQuA-QE Product Owner já sabe interpretar. Visão e estratégia, quando exportadas para registro próprio (não consumidas pelo Product Owner), seguem `../../knowledge/templates/product_vision.md` e `.../product_strategy.md`.
