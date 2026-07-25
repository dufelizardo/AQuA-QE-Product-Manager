# Template — Estratégia de Produto

> Estrutura padrão, sem conteúdo de domínio. Preencher os campos entre `< >` ao gerar uma estratégia real. Ver `../../docs/standards/product_strategy_standard.md`.

## Campos

- **Metas** (uma ou mais), cada uma com:
  - **Descrição**: `<a meta em si>`
  - **Métrica**: `<como o progresso da meta é medido>`
  - **Alvo**: `<valor-alvo da métrica — vazio se não informado pela fonte>`
  - **Prazo**: `<horizonte de tempo da meta — vazio se não informado pela fonte>`
  - **Referência à fonte**: `<de onde esta meta foi derivada>`
- **Temas de roadmap**: `<áreas de investimento de alto nível que conectam a visão às metas>`
- **Horizonte de tempo**: `<período que a estratégia cobre>`

## Checklist de qualidade

- Cada meta é rastreável a um diferencial ou ao público-alvo da visão aceita — nenhuma meta "solta" (ver `../../docs/standards/product_strategy_standard.md`).
- Alvo e prazo só são preenchidos com base explícita na fonte — nunca uma projeção inventada (ver `../../docs/agent/guardrails.md`, GR-M2/GR-M3).
- Temas de roadmap descrevem áreas de investimento, não uma lista de features já comprometidas — comprometimento de escopo é responsabilidade do PRD (ver `prd.md`).
