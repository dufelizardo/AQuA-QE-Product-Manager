# Agent Design

> Ponte entre o System Design (arquitetura técnica) e a AI Spec/Rules (comportamento). Descreve como o agente decide, não apenas por onde os dados fluem.

## Pontos de decisão do agente

1. **Descoberta é opcional, mas nunca inventada** — o agente pode gerar visão/estratégia/PRD sem descoberta prévia (ideia crua), mas quando descoberta existe, ela é usada; quando não existe, o agente não a inventa retroativamente para "parecer mais completo".
2. **Prosseguir vs. interromper por ambiguidade** — após cada skill geradora, o agente avalia se há informação suficiente para um artefato rastreável. Se não houver, **interrompe e solicita esclarecimento** (não gera suposição silenciosa) — mesma decisão de design mais importante herdada do AQuA-QE Product Owner (ver `guardrails.md`).
3. **Nunca inventar dado de mercado/financeiro mesmo quando o modelo "sabe"** — esta é a decisão de design mais específica deste agente (não existe equivalente direto no Product Owner): mesmo que o LLM tenha conhecimento real sobre concorrentes de um mercado, esse conhecimento nunca é usado para preencher `MarketAnalysis`/`BusinessCase` — só o que o usuário informou.
4. **Aprovar automaticamente vs. exigir revisão humana** — o agente **nunca** decide aprovação final de nenhum artefato. `validate_*` decide apenas se passa no checklist automático (nível "rascunho validado"); a aprovação de negócio permanece sempre humana, sempre perguntada explicitamente no CLI.

## Papel de cada camada nas decisões

- **AI Spec** (`ai_spec.md`) — descreve o comportamento esperado em cada ponto de decisão acima.
- **Rules** (`rules.md`) — tornam esses comportamentos verificáveis e aplicáveis.
- **Skills** (`skills.md`) — implementam a capacidade técnica que cada decisão utiliza.

## Modelo de interação com o usuário

O agente é **colaborativo e consultivo**, não uma caixa-preta: ao interromper por ambiguidade ou por falta de dado de mercado/financeiro, explica qual informação está faltando e por quê; ao entregar um artefato, explica as decisões tomadas para que o revisor humano valide rapidamente (ver `persona.md`).

## Relação com o AQuA-QE Product Owner

Os dois agentes são **independentes** — repositórios separados, sem runtime compartilhado, sem chamada direta entre um e outro. A única ponte é um artefato de texto: o PRD gerado e aceito por este agente (`format_prd_markdown`) é exportado em Markdown e consumido pelo Product Owner como uma entrada normal (`--modo lote --arquivo prd.md`), pulando o próprio `--modo prd` do Product Owner (já que este agente já rodou seu próprio ciclo validate/review/refine). Essa separação preserva a característica determinística/auditável de cada agente — nenhum dos dois delega decisão em tempo real ao outro.

## Fora do escopo do agente

Pesquisa de mercado real, entrevistas com clientes, priorização formal, definição de MVP scope, business case, comunicação entre times e gestão de stakeholders — ver `prd.md`, seção "Fora de escopo", para a lista completa e o que está deliberadamente adiado vs. permanentemente fora do escopo deste agente.
