# Padrão de Visão, Estratégia e Análise de Mercado

> Estrutura padrão para os artefatos de Visão de Produto, Estratégia de Produto e Análise de Mercado de um agente desta plataforma. Sem equivalente no AQuA-QE Product Owner — este padrão nasce com o AQuA-QE Product Manager. Define o formato; o conteúdo deste agente fica em `../agent/output_schema.md`.

## Propósito

Visão e Estratégia respondem **para onde o produto vai** e **como chegar lá**, antes de qualquer requisito específico existir — a camada acima do PRD na cadeia `Descoberta → Visão → Estratégia → PRD → System Design`. Análise de Mercado é um insumo de descoberta que alimenta ambas.

## Análise de Mercado (`MarketAnalysis`)

1. **Concorrentes** — nome, pontos fortes, pontos fracos, cada um com referência à fonte de onde foi citado.
2. **Tendências** — tendências de mercado relevantes, apenas as citadas na fonte de entrada.
3. **Contexto de mercado** — síntese textual do cenário competitivo descrito pela fonte.

**Critério de qualidade não negociável**: todo item desta seção deve ser rastreável a uma citação literal na fonte de entrada. Concorrente ou tendência "conhecido" pelo LLM mas não citado pelo usuário nunca deve aparecer aqui — a ausência de dado é o resultado correto, não uma falha a ser compensada com conhecimento geral do modelo.

## Visão de Produto (`ProductVision`)

1. **Statement** — a visão em uma frase: o futuro que o produto pretende criar.
2. **Público-alvo** — para quem essa visão é relevante (conecta com `Persona`, ver `prd_standard.md` § Público-alvo).
3. **Diferenciais** — o que torna essa visão distinta de alternativas existentes, apenas os sustentados pela fonte.
4. **Métrica norte (north star metric)** — a métrica que melhor representa o valor entregue pela visão, quando informada ou diretamente inferível da fonte; vazia quando não — nunca uma métrica "típica de mercado" inventada.

## Estratégia de Produto (`ProductStrategy`)

1. **Metas** — cada meta com descrição, métrica, alvo e prazo; alvo/prazo vazios quando não informados pela fonte (mesma disciplina de não inventar da Visão).
2. **Temas de roadmap** — áreas de investimento de alto nível que conectam a visão às metas, sem comprometer com uma lista de features (isso é responsabilidade do PRD/backlog, fora deste padrão).
3. **Horizonte de tempo** — período que a estratégia cobre (ex.: "próximos 2 trimestres"), quando informado.

## Critérios de qualidade

- Cada meta de estratégia deve ser rastreável a um diferencial ou ao público-alvo da visão aceita — nenhuma meta "solta", sem conexão com a visão.
- Métrica-alvo e prazo seguem a mesma disciplina de "requisito bem escrito" da ISO/IEC/IEEE 29148 quando presentes (mensurável, verificável) — ver `../../knowledge/methodology/iso29148.md`.
- Visão e Estratégia usam os mesmos valores de `status` (`draft_validated`/`pending_clarification`/`accepted`) que o PRD (ver `prd_standard.md`), com o mesmo requisito de aceite humano explícito, nunca automático.
