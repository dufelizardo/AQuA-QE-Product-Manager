# AQuA-QE Product Manager

> Also available in [Portuguese](README.pt.md).

Agent that drives the product discovery and strategy phase — problem statement, personas, jobs to be done, market context, product vision, product strategy and PRD — from an informal idea or chat transcript, following the same agent engineering flow as its sibling agent, the [AQuA-QE Product Owner](https://github.com/dufelizardo/AQuA-QE-Product-Owner):

```
PRD → System Design → Agent Design → AI Specs/Rules/Skills → Context Engineering → Memory/MCP → Agents → Outputs
```

## Relationship with AQuA-QE Product Owner

This agent and the AQuA-QE Product Owner are **independent** — separate repositories, no shared runtime, no direct call between them. Product Manager covers the **strategy** side (what to build and why, before any requirement exists); Product Owner covers the **execution** side (turning a PRD into Epics/User Stories/Acceptance Criteria). The bridge between the two is a plain text artifact: the PRD generated and accepted here is exported as Markdown and consumed by Product Owner as a normal input:

```bash
# In this project: generate and export the PRD
uv run python run.py --modo prd --texto "Customers need to be able to buy CDs through the app" --refinar --saida prd.md

# In the AQuA-QE Product Owner repository: consume the PRD, skipping its own --modo prd
# (since this agent already ran its own validate/review/refine cycle)
uv run python run.py --modo lote --arquivo prd.md --saida saida_epic/
```

No change is needed in Product Owner's code — it already accepts a `.md` file as input.

## Structure

- **`docs/standards/`** — platform standards (how to write an AI Spec, a Rule, a PRD, a Product Vision/Strategy, etc.). Change rarely; most of it is shared with Product Owner.
- **`docs/agent/`** — this agent's full specification: PRD, System Design, Agent Design, AI Spec, Rules, Persona, Objectives, Output Schema, Guardrails, Evaluation, Prompt, and `agent_manifest.yaml`.
- **`knowledge/methodology/`** — methodological material that guides the agent (JTBD, North Star Framework, BABOK, ISO 29148).
- **`knowledge/templates/`** — pure structure, no knowledge (templates for Problem Statement, Persona, Product Vision, Product Strategy, PRD).
- **`src/aqua_qe_product_manager/skills/`** — the agent's 24 skills in Python (read text file, parse/format chat transcript, identify problem statement, synthesize personas, extract jobs to be done, extract market context, generate/validate/review/refine product vision, generate/validate/review/refine product strategy, generate/validate/review/refine PRD, export to Markdown).
- **`src/aqua_qe_product_manager/models/`** — the agent's data structures (ProblemStatement, Persona, JobToBeDone, MarketAnalysis/Competitor, ProductVision, ProductStrategy/StrategicGoal, PRDDraft — the latter with the exact same fields as Product Owner's `PRDDraft`).
- **`src/aqua_qe_product_manager/workflow/`** — orchestration of the skill sequence per artifact (discovery, vision, strategy, PRD).
- **`src/aqua_qe_product_manager/orchestrator/`** — entry point that decides which workflow to run per mode.
- **`src/aqua_qe_product_manager/services/`** — external integrations: `llm_service` (local Ollama, generation/review), `jira_service`/`confluence_service` (Jira Cloud/Confluence Cloud REST API, **read-only** — writing/creating stays exclusive to Product Owner). No RAG at this phase.

## Setup

This is a standalone repository (not part of any monorepo) — `uv sync` here resolves and installs its own dependencies.

1. Install [Python 3.12+](https://www.python.org/) and [uv](https://docs.astral.sh/uv/).
2. Install [Ollama](https://ollama.com) and pull the two local models used by this agent:
   ```bash
   ollama pull mistral   # generation
   ollama pull phi4      # independent reviewer
   ```
   Jira/Confluence are optional — only fill in `JIRA_BASE_URL`/`JIRA_EMAIL`/`JIRA_API_TOKEN` in `.env` if you plan to use `--jira`/`--confluence` (token generated at `id.atlassian.com/manage-profile/security/api-tokens`).
3. Clone this repository and install dependencies:
   ```bash
   git clone https://github.com/dufelizardo/AQuA-QE-Product-Manager.git
   cd AQuA-QE-Product-Manager
   uv sync
   ```
4. Copy `.env.example` to `.env` (defaults already work with a local Ollama install):
   ```bash
   cp .env.example .env
   ```
5. Run the test suite (fully mocked, no real Ollama calls) to confirm the setup:
   ```bash
   uv run pytest
   ```

## Usage

```bash
# Standalone discovery (problem statement, personas, JTBD, market) — no formal acceptance cycle
uv run python run.py --modo descoberta --texto "Unit managers waste time manually consolidating reports"

# Product vision from an idea, with the interactive refinement cycle
uv run python run.py --modo visao --texto "An app that automatically consolidates reports" --refinar --saida visao.md

# Product strategy (generates the vision internally and, once accepted, the strategy)
uv run python run.py --modo estrategia --arquivo idea.txt --refinar --saida estrategia.md

# PRD from a raw idea, with no prior discovery/vision/strategy — the simplest path
uv run python run.py --modo prd --texto "Customers need to be able to buy CDs through the app" --refinar --saida prd.md

# Full pipeline — discovery -> vision -> strategy -> PRD, with human acceptance at each step
uv run python run.py --modo completo --arquivo idea.txt --refinar --saida prd.md

# Input from a Jira Cloud ticket or a Confluence Cloud page
uv run python run.py --modo completo --jira PROJ-123 --refinar --saida prd.md
uv run python run.py --modo completo --confluence "https://your-site.atlassian.net/wiki/.../pages/163841/..." --refinar --saida prd.md

# Refine an existing PRD .md (loads the original fields, doesn't rewrite from scratch)
uv run python run.py --modo prd --prd-existente prd.md --refinar --saida prd.md
```

`--saida` is optional in every mode that produces an artifact (without it, the result is only printed to the terminal). `--refinar` enables the interactive clarifying-questions/refinement cycle before acceptance — but acceptance itself is **always** explicitly asked, with or without this flag (see `docs/agent/acceptance_patterns.md`).

`--prd-existente` only works with `--modo prd`: instead of generating a new PRD via LLM, it loads the given `.md` as a structured `PRDDraft` (`parse_prd_markdown`, no LLM), preserving the original wording field by field, and goes straight into the same validate/review/refine cycle — useful to resume an already-exported PRD without rewriting it from scratch.

`--jira`/`--confluence` are read-only — they fetch the source text (ticket summary+description, or page title+body), but this agent never writes back to those systems; write-back and ticket/page creation stay exclusive to Product Owner.

The `completo` mode is the recommended path for the Product Owner handoff: it chains discovery, vision, strategy and PRD in a single run, using each accepted artifact as context for the next, and produces a single `prd.md` ready for `--modo lote --arquivo prd.md` in Product Owner. The standalone `prd` mode, with no prior context, behaves like Product Owner's own `--modo prd` (raw idea → PRD) — useful when formal discovery/vision/strategy aren't needed.

## Status

`docs/agent/`, `docs/standards/` and `knowledge/` are filled with real content. In `src/`, all 24 skills and the four workflows (discovery, vision, strategy, PRD) are implemented and covered by tests (LLM mocks, no real Ollama call). Prioritization (RICE/MoSCoW/Kano/WSJF), formal MVP scope and business case are left for a future Phase 2 — deliberately out of scope for this first version (see `docs/agent/prd.md`, "Fora de escopo" section).

This project has its own git repository, independent from the workspace root monorepo (per the "every new project gets its own repository" convention — see the workspace root `CLAUDE.md`).

---

**Eduardo Felizardo Cândido**
Senior QA Automation Engineer | AI-driven Testing | Robot Framework & Python
