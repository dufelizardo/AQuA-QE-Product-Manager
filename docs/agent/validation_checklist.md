# Validation Checklist

> Checklist automático (Python puro, sem LLM) aplicado por `validate_product_vision`, `validate_product_strategy` e `validate_prd`, antes da revisão por segundo LLM. Equivalente ao checklist de `validate_prd`/`validate_story` no AQuA-QE Product Owner.

## Visão de produto (`validate_product_vision`)

- [ ] `statement` não vazio.
- [ ] `target_audience` não vazio.

Não exige `differentiators`/`north_star_metric` preenchidos — podem legitimamente ficar vazios quando o texto de entrada não os define (GR-M3), sem bloquear o checklist; a ausência aciona `pending_clarification` via revisão, não falha o checklist estrutural.

## Estratégia de produto (`validate_product_strategy`)

- [ ] `goals` tem ao menos um item.
- [ ] O primeiro item de `goals` tem `description` e `metric` não vazios.

## PRD (`validate_prd`)

Idêntico ao checklist do AQuA-QE Product Owner, para preservar compatibilidade de handoff:

- [ ] `context_problem` não vazio.
- [ ] `objective` não vazio.
- [ ] `scope` não vazio.
- [ ] `functional_requirements` tem ao menos um item.
- [ ] `success_criteria` tem ao menos um item.

Os 10 campos de profundidade (`personas`, `user_journeys`, `business_objectives`, `use_cases`, `dependencies`, `technical_assumptions`, `constraints`, `glossary`, `candidate_product_metrics`, `mvp_scope`/`future_scope`) são deliberadamente **não** obrigatórios neste checklist — são enriquecimento opcional, não bloqueiam o PRD por estarem vazios (mesmo princípio já aplicado a `components`/`integrations` no AQuA-QE Solution Architect).

## Regra geral

O checklist automático avalia apenas **presença estrutural**, nunca qualidade de conteúdo — qualidade e coerência ficam a cargo de `review_*` (segundo LLM) e, no fim, do julgamento humano no aceite (ver `acceptance_patterns.md`). Um artefato pode passar no checklist e ainda assim ser reprovado na revisão ou recusado no aceite.
