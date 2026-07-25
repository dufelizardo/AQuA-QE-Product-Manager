# CLAUDE.md

Este arquivo orienta o Claude Code ao trabalhar neste repositório.

## O que é este projeto

Agente que conduz a fase de descoberta e estratégia de produto — problem statement, personas, jobs to be done, contexto de mercado, visão de produto, estratégia de produto e PRD — a partir de uma ideia informal ou transcrição de chat. Produz um PRD que serve de entrada direta para o agente irmão [AQuA-QE Product Owner](../AQuA-QE%20Product%20Owner/) via `--modo lote --arquivo prd.md`. Ver `README.pt.md`/`README.md` para a visão geral, `docs/agent/` para a especificação completa e `docs/architecture/` para os diagramas (draw.io + SVG).

Este é um **repositório standalone**, próprio, independente de qualquer monorepo — não assuma dependências herdadas de um workspace pai.

## Comandos essenciais

```bash
# Instalar/sincronizar dependências
uv sync

# Rodar toda a suíte de testes (mockada, sem chamadas reais a Ollama)
uv run pytest

# Rodar um teste único
uv run pytest tests/test_generate_prd.py::test_nome_do_teste

# Descoberta isolada (sem ciclo de aceite formal)
uv run python run.py --modo descoberta --arquivo ideia.txt

# Pipeline completo (descoberta -> visão -> estratégia -> PRD), o caminho recomendado para o handoff ao Product Owner
uv run python run.py --modo completo --arquivo ideia.txt --refinar --saida prd.md

# Ver todas as opções (--modo, --arquivo/--texto, --saida, --refinar)
uv run python run.py --help
```

Não há configuração própria de lint/type-check (`ruff`/`basedpyright`) neste `pyproject.toml` — isso existe apenas na raiz do monorepo que originou este projeto, não neste repositório standalone.

## Setup local

Ver a seção "Setup"/"Configuração" em `README.md`/`README.pt.md`: requer Python 3.12+, `uv`, Ollama instalado com os modelos `mistral` e `phi4` baixados, e um `.env` preenchido a partir de `.env.example`.

## Arquitetura (resumo — detalhe completo em `docs/agent/system_design.md`)

```
Entrada (.txt/Markdown/chat)
  → CLI (run.py) → orchestrator/product_manager.py → workflow/* → skills/* → models/* → services/*
```

- `src/aqua_qe_product_manager/models/` — `ProblemStatement`, `Persona`, `JobToBeDone`, `MarketAnalysis`/`Competitor`, `ProductVision`, `ProductStrategy`/`StrategicGoal`, `PRDDraft` (mesmos campos exatos do `PRDDraft` do Product Owner), `ChatMessage`, enum `ArtifactStatus`.
- `src/aqua_qe_product_manager/skills/` — 24 funções de responsabilidade única (ver `docs/agent/skills.md`).
- `src/aqua_qe_product_manager/workflow/` — orquestra a sequência de skills por artefato (`generate_problem_discovery`, `generate_product_vision`, `generate_product_strategy`, `generate_prd`).
- `src/aqua_qe_product_manager/orchestrator/product_manager.py` — `handle_discovery`/`handle_vision`/`handle_strategy`/`handle_prd`, um por modo.
- `src/aqua_qe_product_manager/services/` — integração externa: `llm_service` (Ollama). Sem RAG/Jira/Confluence nesta fase.

## Convenções críticas

- **Nunca inventar** (GR-1, `docs/agent/guardrails.md`): todo campo gerado só existe se rastreável à fonte de entrada. Quando não identificável, os campos ficam vazios (`""`/`[]`), o que aciona `pending_clarification` — nunca preencha com suposição.
- **Nunca inventar dado de mercado, financeiro ou meta de visão/estratégia** (GR-M1/GR-M2/GR-M3, o guardrail mais crítico deste agente, sem equivalente direto no Product Owner): mesmo que o LLM "reconheça" o mercado/domínio descrito, esse conhecimento geral nunca é usado para preencher `MarketAnalysis`, métricas financeiras ou metas de estratégia/visão — só o que a fonte de entrada informou.
- **Sem aprovação automática** (cobre Visão/Estratégia/PRD): nenhuma skill/workflow define `ArtifactStatus.ACCEPTED`. Esse status só é atribuído pelo CLI (`run.py`), após confirmação humana explícita no terminal — sempre pedida, com ou sem `--refinar`.
- **Toda saída de LLM gerador/revisor é sempre em português**, por design, independentemente do idioma da fonte de entrada — instrução explícita e hardcoded nos prompts de geração/refinamento. Não é um comportamento adaptativo por idioma da entrada.
- **Dois LLMs sempre diferentes**: `OLLAMA_MODEL` (padrão `mistral`) gera; `OLLAMA_REVIEW_MODEL` (padrão `phi4`) revisa. É deliberado — mitiga *self-preference bias* de um modelo aprovar a própria saída.
- **Testes sempre mockam** Ollama — nenhum teste em `tests/` faz chamada real de rede. Ao adicionar um teste para uma skill/service novo, siga esse padrão.
- **PRD é o único artefato de handoff** para o AQuA-QE Product Owner — `format_prd_markdown` produz Markdown byte-compatível com o que o Product Owner já sabe interpretar via `--modo lote --arquivo`. Visão e Estratégia, quando exportadas, seguem `knowledge/templates/product_vision.md`/`product_strategy.md`, mas não são consumidas pelo Product Owner.
- **Priorização (RICE/MoSCoW/Kano/WSJF), MVP scope formal e business case** foram avaliados e deliberadamente adiados para uma Fase 2 futura — não implementar especulativamente; ver `docs/agent/prd.md`, seção "Fora de escopo".
- **Sem RAG/embeddings nesta fase** — `knowledge/methodology/` é pequeno o suficiente para caber direto no prompt de cada skill (ver `docs/agent/context_engineering.md`).

## Onde procurar mais detalhe

- `docs/agent/` — PRD, System Design, Agent Design, Rules, Guardrails, Persona, Objectives, Skills, Evaluation (a spec formal completa do agente).
- `knowledge/methodology/` — os frameworks reais que fundamentam os critérios de qualidade (JTBD, North Star Framework, BABOK, ISO 29148) — nenhum critério do agente foi inventado à parte desses documentos.
- `docs/standards/` — padrões da plataforma, em sua maioria compartilhados com o Product Owner; `product_strategy_standard.md` é o único sem equivalente lá.
- `docs/architecture/` — diagramas visuais (draw.io + SVG) dos mesmos fluxos: arquitetura em camadas, fluxo por artefato (Visão/Estratégia/PRD), fluxo de descoberta, ciclo de refinamento humano-no-loop e o pipeline completo com o handoff para o Product Owner.
