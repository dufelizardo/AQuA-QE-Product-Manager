# AQuA-QE Product Manager

> Também disponível em [English](README.md).

Agente que conduz a fase de descoberta e estratégia de produto — problem statement, personas, jobs to be done, contexto de mercado, visão de produto, estratégia de produto e PRD — a partir de uma ideia informal ou transcrição de chat, seguindo o mesmo fluxo de engenharia de agentes do seu agente irmão, o [AQuA-QE Product Owner](https://github.com/dufelizardo/AQuA-QE-Product-Owner):

```
PRD → System Design → Agent Design → AI Specs/Rules/Skills → Context Engineering → Memory/MCP → Agents → Outputs
```

## Relação com o AQuA-QE Product Owner

Este agente e o AQuA-QE Product Owner são **independentes** — repositórios separados, sem runtime compartilhado, sem chamada direta entre um e outro. O Product Manager cobre a parte de **estratégia** (o quê construir e por quê, antes de qualquer requisito existir); o Product Owner cobre a parte de **execução** (transformar um PRD em Epics/User Stories/Critérios de Aceitação). A ponte entre os dois é um artefato de texto: o PRD gerado e aceito aqui é exportado em Markdown e consumido pelo Product Owner como uma entrada normal:

```bash
# Neste projeto: gera e exporta o PRD
uv run python run.py --modo prd --texto "Clientes precisam conseguir contratar CDB pelo app" --refinar --saida prd.md

# No repositório do AQuA-QE Product Owner: consome o PRD, pulando o próprio --modo prd
# (já que este agente roda seu próprio ciclo validate/review/refine)
uv run python run.py --modo lote --arquivo prd.md --saida saida_epic/
```

Nenhuma mudança é necessária no código do Product Owner — ele já aceita arquivo `.md` como entrada.

## Estrutura

- **`docs/standards/`** — padrões da plataforma (como escrever um AI Spec, uma Rule, um PRD, uma Visão/Estratégia de produto, etc.). Mudam pouco; a maior parte é compartilhada com o Product Owner.
- **`docs/agent/`** — especificação completa deste agente: PRD, System Design, Agent Design, AI Spec, Rules, Persona, Objectives, Output Schema, Guardrails, Evaluation, Prompt e o `agent_manifest.yaml`.
- **`knowledge/methodology/`** — material metodológico que orienta o agente (JTBD, North Star Framework, BABOK, ISO 29148).
- **`knowledge/templates/`** — estrutura pura, sem conhecimento (templates de Problem Statement, Persona, Visão de Produto, Estratégia de Produto, PRD).
- **`src/aqua_qe_product_manager/skills/`** — skills do agente em Python (ler arquivo de texto/ticket Jira/página Confluence, parsear/formatar transcrição de chat, identificar problem statement, sintetizar personas, extrair jobs to be done, extrair contexto de mercado, gerar/validar/revisar/refinar a visão de produto, gerar/validar/revisar/refinar a estratégia de produto, gerar/validar/revisar/refinar/carregar o PRD, exportar em Markdown, publicar/atualizar página no Confluence). Lista completa em `docs/agent/skills.md`.
- **`src/aqua_qe_product_manager/models/`** — estruturas de dados do agente (ProblemStatement, Persona, JobToBeDone, MarketAnalysis/Competitor, ProductVision, ProductStrategy/StrategicGoal, PRDDraft — este último com os mesmos campos exatos do `PRDDraft` do Product Owner).
- **`src/aqua_qe_product_manager/workflow/`** — orquestração da sequência de skills por artefato (descoberta, visão, estratégia, PRD).
- **`src/aqua_qe_product_manager/orchestrator/`** — ponto de entrada que decide qual workflow executar por modo.
- **`src/aqua_qe_product_manager/services/`** — integrações externas: `llm_service` (Ollama local, geração/revisão), `jira_service` (Jira Cloud REST API, **apenas leitura**) e `confluence_service` (Confluence Cloud REST API, leitura + criação de página nova + atualização de página existente, usadas por `--publicar-confluence`/`--atualizar-confluence`). Sem RAG nesta fase.

## Configuração

Este é um repositório independente (não faz parte de nenhum monorepo) — o `uv sync` aqui resolve e instala suas próprias dependências.

1. Instale [Python 3.12+](https://www.python.org/) e [uv](https://docs.astral.sh/uv/).
2. Instale o [Ollama](https://ollama.com) e baixe os dois modelos locais usados por este agente:
   ```bash
   ollama pull mistral   # geração
   ollama pull phi4      # revisor independente
   ```
   Jira/Confluence são opcionais — só preencha `JIRA_BASE_URL`/`JIRA_EMAIL`/`JIRA_API_TOKEN` no `.env` se for usar `--jira`/`--confluence`/`--publicar-confluence` (token gerado em `id.atlassian.com/manage-profile/security/api-tokens`; `CONFLUENCE_SPACE_KEY` só é necessário para `--publicar-confluence`).
3. Clone este repositório e instale as dependências:
   ```bash
   git clone https://github.com/dufelizardo/AQuA-QE-Product-Manager.git
   cd AQuA-QE-Product-Manager
   uv sync
   ```
4. Copie `.env.example` para `.env` (os padrões já funcionam com uma instalação local do Ollama):
   ```bash
   cp .env.example .env
   ```
5. Rode a suíte de testes (totalmente mockada, sem chamadas reais a Ollama) para confirmar a configuração:
   ```bash
   uv run pytest
   ```

## Uso

```bash
# Descoberta isolada (problem statement, personas, JTBD, mercado) — sem ciclo de aceite formal
uv run python run.py --modo descoberta --texto "Gestores de unidade perdem tempo consolidando relatórios manualmente"

# Visão de produto a partir de uma ideia, com ciclo interativo de refinamento
uv run python run.py --modo visao --texto "Um app de consolidação automática de relatórios" --refinar --saida visao.md

# Estratégia de produto (gera a visão internamente e, uma vez aceita, a estratégia)
uv run python run.py --modo estrategia --arquivo ideia.txt --refinar --saida estrategia.md

# PRD a partir de uma ideia crua, sem descoberta/visão/estratégia prévias — caminho mais simples
uv run python run.py --modo prd --texto "Clientes precisam conseguir contratar CDB pelo app" --refinar --saida prd.md

# Pipeline completo — descoberta -> visão -> estratégia -> PRD, com aceite humano em cada etapa
uv run python run.py --modo completo --arquivo ideia.txt --refinar --saida prd.md

# Entrada a partir de um ticket Jira Cloud ou de uma página do Confluence Cloud
uv run python run.py --modo completo --jira PROJ-123 --refinar --saida prd.md
uv run python run.py --modo completo --confluence "https://seu-site.atlassian.net/wiki/.../pages/163841/..." --refinar --saida prd.md

# Refinar um PRD .md já existente (carrega os campos originais, não reescreve do zero)
uv run python run.py --modo prd --prd-existente prd.md --refinar --saida prd.md

# Publicar o PRD aceito como página nova no Confluence Cloud
uv run python run.py --modo prd --texto "<ideia>" --refinar --publicar-confluence

# Atualizar uma página já existente no Confluence, em vez de criar uma nova
uv run python run.py --modo prd --texto "<ideia>" --refinar --atualizar-confluence 163841

# Publicar a visão de produto (não só o PRD) como página no Confluence
uv run python run.py --modo visao --texto "<ideia>" --refinar --publicar-confluence
```

`--saida` é opcional em todos os modos que produzem artefato (sem ela, o resultado só é impresso no terminal). `--refinar` ativa o ciclo interativo de perguntas/refinamento antes do aceite — mas o aceite em si é **sempre** perguntado explicitamente, com ou sem essa flag (ver `docs/agent/acceptance_patterns.md`).

`--prd-existente` só funciona com `--modo prd`: em vez de gerar um PRD novo via LLM, carrega o `.md` informado como `PRDDraft` estruturado (`parse_prd_markdown`, sem LLM), preservando a redação original campo a campo, e segue direto para o mesmo ciclo de validação/revisão/refinamento — útil para retomar um PRD já exportado sem reescrevê-lo do zero.

`--publicar-confluence`/`--atualizar-confluence` (mutuamente exclusivos; válidos com `--modo prd`/`completo`/`visao`/`estrategia`) perguntam, depois do artefato aceito, se deve publicá-lo como página **nova** no Confluence (`CONFLUENCE_SPACE_KEY`) ou atualizar uma página **já existente** (`--atualizar-confluence <URL ou ID>`, mantendo título, incrementando a versão) — sempre sob confirmação humana explícita, distinta do aceite do artefato.

`--jira`/`--confluence` são apenas leitura — buscam o texto de origem (resumo+descrição do ticket, ou título+corpo da página), mas este agente nunca escreve de volta nesses sistemas; write-back e criação de ticket/página continuam exclusivos do Product Owner.

O modo `completo` é o caminho recomendado para o handoff ao Product Owner: encadeia descoberta, visão, estratégia e PRD numa execução só, usando cada artefato aceito como contexto para o próximo, e produz um único `prd.md` pronto para `--modo lote --arquivo prd.md` no Product Owner. O modo `prd` isolado, sem contexto prévio, se comporta como o `--modo prd` do Product Owner (ideia crua → PRD) — útil quando descoberta/visão/estratégia formais não são necessárias.

## Status

`docs/agent/`, `docs/standards/` e `knowledge/` estão com conteúdo real preenchido. Em `src/`, todas as skills e os quatro workflows (descoberta, visão, estratégia, PRD) estão implementados e cobertos por testes (mocks de LLM, sem chamada real a Ollama/Jira/Confluence). Priorização (RICE/MoSCoW/Kano/WSJF), MVP scope formal e business case ficam para uma Fase 2 futura — deliberadamente fora do escopo desta primeira versão (ver `docs/agent/prd.md`, seção "Fora de escopo").

Este projeto tem repositório git próprio, independente do monorepo raiz (conforme a convenção "todo projeto novo recebe repositório separado" — ver `CLAUDE.md` raiz do workspace).

---

**Eduardo Felizardo Cândido**
Senior QA Automation Engineer | AI-driven Testing | Robot Framework & Python
