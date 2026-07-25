# Template — PRD

> Estrutura padrão, sem conteúdo de domínio. Preencher os campos entre `< >` ao gerar um PRD real. Ver `../../docs/standards/prd_standard.md` e `../../docs/agent/output_schema.md` — mesmos campos exatos do `PRDDraft` consumido pelo AQuA-QE Product Owner via `--modo lote --arquivo`.

## Campos

- **Contexto e problema**: `<necessidade de negócio que motiva o produto — rastreável ao problem statement da descoberta, quando houver>`
- **Objetivo**: `<resultado que o produto deve produzir, em uma frase>`
- **Público-alvo**: `<personas que usam o produto ou consomem seus resultados>`
- **Escopo**: `<o que o produto faz>`
- **Fora de escopo**: `<o que o produto explicitamente não faz>`
- **Requisitos funcionais**: `<lista de capacidades, uma declaração singular por item — ver ../methodology/iso29148.md>`
- **Requisitos não funcionais**: `<desempenho, segurança, disponibilidade, quando aplicável>`
- **Critérios de sucesso**: `<como medir se o produto está entregando valor — conectam com a métrica norte da visão, quando houver>`
- **Riscos e premissas**: `<dependências externas, limitações conhecidas, suposições assumidas>`

## Checklist de qualidade

- Cada requisito funcional é rastreável a um objetivo do PRD e, quando existirem, à visão/estratégia aceitas (ver `../../docs/standards/product_strategy_standard.md`).
- Escopo e fora de escopo são mutuamente exclusivos e, juntos, exaustivos o suficiente para não deixar zona cinzenta (ver `../../docs/standards/prd_standard.md`).
- Nenhum campo é inventado sem rastreabilidade à fonte, à descoberta ou à visão/estratégia já aceitas (ver `../../docs/agent/guardrails.md`, GR-1).
