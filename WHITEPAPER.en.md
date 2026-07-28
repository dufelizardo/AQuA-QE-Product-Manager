# AQuA-QE Product Manager — Whitepaper

> Também disponível em [Portuguese](WHITEPAPER.md).

> Product discovery and strategy agent that synthesizes a problem statement, personas, jobs to be done, market context, product vision, product strategy and PRD from an informal idea or chat transcript — with mandatory traceability to source, automatic validation and human review at the center of the cycle, producing a PRD that feeds directly into the sibling agent AQuA-QE Product Owner.

Repository: [github.com/dufelizardo/AQuA-QE-Product-Manager](https://github.com/dufelizardo/AQuA-QE-Product-Manager)

---

## 1. Executive summary

The AQuA-QE Product Owner already covers the **execution** side well: it turns a PRD into Epics, User Stories and Acceptance Criteria, with a full human-in-the-loop cycle. What was missing was the **strategy** side — deciding what to build and why, before any PRD exists. A PRD generated from a raw idea, with no prior discovery (personas, jobs to be done, the real problem), with no formalized product vision and strategy, carries that gap forward: well-structured Epics and User Stories, potentially solving the wrong problem.

The AQuA-QE Product Manager closes that gap as a new, independent agent, not as an extension bolted onto Product Owner. From an informal idea or a conversation transcript, it synthesizes a problem statement, personas, jobs to be done and market context — whenever the source supports that synthesis —, generates a product vision, derives a product strategy from it and, finally, generates the PRD, incorporating everything accepted in the previous steps. Every artifact goes through the same quality pattern: automatic validation, review by a second, independent LLM, and acceptance always explicitly asked from a human — never automatic.

The most critical differentiator of this agent, with no direct equivalent in Product Owner, is the guardrail against inventing market and financial data: an LLM tends to fill "market knowledge" gaps with real information that was never actually cited by the user — competitor names, market size, projections. This agent treats that as the most serious mistake it can make, and explicitly forbids it at both the prompt and architecture level, even when the model "knows" the right answer.

## 2. Methodological foundation

No quality criterion used by the agent was invented. Each one is documented in `knowledge/methodology/` and referenced directly by the agent's skills and guardrails:

| Framework | Role in the agent |
|---|---|
| **Jobs to Be Done** (`jtbd.md`) | Structures `extract_jobs_to_be_done` in the "When ..., I want ..., so that ..." format and guides the vision's `statement` to address a real job, not a feature. |
| **North Star Framework** (`north_star_framework.md`) | Guides the vision's `north_star_metric` field — a metric of value to the customer, not a vanity or pure business metric. |
| **BABOK** (`babok.md`) | The BACCM model (Need/Stakeholder/Value/Solution/Change/Context) provides the structural vocabulary for discovery and vision. |
| **ISO/IEC/IEEE 29148** (`iso29148.md`) | Reference for quality and completeness of the PRD's functional/non-functional requirements. |

These documents aren't decoration: `generate_product_vision` references the North Star Framework directly in its prompt to guide (without forcing) the target metric's format, and `validate_prd`/`review_prd` apply the ISO 29148 "well-written requirement" criteria.

## 3. Design principles (guardrails)

Six guardrails govern the agent's behavior (`docs/agent/guardrails.md`):

- **GR-1 — Never invent.** Inherited from Product Owner: no discovery, vision, strategy or PRD field is generated without traceable origin in the input source. Fields that can't be identified stay empty, which triggers `pending_clarification`.
- **GR-M1 — Never invent market data.** `extract_market_context` never lists a competitor or trend that isn't literally cited in the input text, even when the model recognizes the market described and "knows" who the real competitors are.
- **GR-M2 — Never invent financial metrics.** No ROI, CAC, LTV projection or financial metric is generated without explicit basis in the source.
- **GR-M3 — Never invent a vision/strategy target.** The vision's `north_star_metric` and each strategy goal's `target`/`timeframe` stay empty when unsupported by the source — never filled with a "typical for the industry" value.
- **GR-M4 — Never estimate a prioritization number (RICE/WSJF).** Reach, impact, confidence, effort, business value, time criticality, risk reduction and job size always come from `input()` in the CLI; `compute_rice_score`/`compute_wsjf_score` are pure Python, with no LLM call at all.
- **Cross-cutting guardrail — No automatic approval.** No skill/workflow ever sets `ArtifactStatus.ACCEPTED`. Approval of Vision, Strategy and PRD is always an explicit human act in the CLI, with or without the interactive refinement cycle.

GR-M1/GR-M2/GR-M3/GR-M4 are what sets this agent apart from Product Owner: GR-1 protects against inventing what the source *should* contain but doesn't mention; GR-M1-M4 protect against the opposite, subtler risk — the model (or, for RICE/WSJF, the agent itself) filling a gap with a number that *looks* plausible, but wasn't authorized by the source or the user, which is more dangerous to miss in review than an obvious mistake.

## 4. Architecture

```
Input (.txt/Markdown/chat/Jira/Confluence)
   → read_text_file / parse_chat_transcript+format_chat_transcript (chat only) / read_jira_issue / read_confluence_page (read-only)
   → identify_problem_statement / synthesize_personas / extract_jobs_to_be_done / extract_market_context (discovery, optional)
   → generate_product_vision  (generator LLM — mistral)
   → validate_product_vision  (pure Python checklist)
   → review_product_vision    (independent reviewer LLM — phi4)
   → [if rejected] generate_vision_clarifying_questions → human answer → refine_product_vision → revalidate
   → explicit human acceptance
   → generate_product_strategy (uses the accepted vision) → validate/review/refine → explicit human acceptance
   → generate_prd (uses discovery + vision + strategy, when they exist) → validate/review/refine → explicit human acceptance
   → format_prd_markdown → export_markdown
   → [optional] create_confluence_page / update_confluence_page (--publicar-confluence / --atualizar-confluence, after explicit human confirmation)
   → [optional] classify_moscow or compute_rice_score/compute_wsjf_score (--priorizar, file separate from the PRD)
   → (outside this agent) AQuA-QE Product Owner consumes the PRD via --modo lote --arquivo
```

Code layers (`src/aqua_qe_product_manager/`):

- **`models/`** — data structures: `ProblemStatement`, `Persona`, `JobToBeDone`, `MarketAnalysis`/`Competitor`, `ProductVision`, `ProductStrategy`/`StrategicGoal`, `PRDDraft`, `PrioritizedRequirement`/`PriorityInputs` (deliberately outside `PRDDraft`, never changing the handoff contract) and the `ArtifactStatus` enum (`draft_validated` / `pending_clarification` / `accepted`).
- **`skills/`** — each with a single side effect and a single responsibility (see section 5).
- **`workflow/`** — orchestrates the skill sequence per artifact: `generate_problem_discovery.py` (no generate/finalize/refine trio — discovery has no formal acceptance cycle), `generate_product_vision.py`, `generate_product_strategy.py`, `generate_prd.py` (the latter three following the `generate_x_draft`/`finalize_x`/`refine_x_draft` trio).
- **`orchestrator/product_manager.py`** — four thin entry points, one per mode (`handle_discovery`/`handle_vision`/`handle_strategy`/`handle_prd`), each delegating to its corresponding workflow.
- **`services/`** — `llm_service` (Ollama, generation/review), `jira_service` (Jira Cloud REST API, **read-only**) and `confluence_service` (Confluence Cloud REST API, reading + new-page creation + existing-page update — this agent's only external writes, used by `--publicar-confluence`/`--atualizar-confluence`).

`PRDDraft` has the exact same fields as Product Owner's `PRDDraft` — not by coincidence, but by design: it's the compatibility contract that enables the handoff (section 7) with zero code changes on Product Owner's side. Rich artifacts (discovery, vision, strategy) are **input that enriches the generation** of those same fields, not new sections in the exported PRD.

## 5. The skills

Skills with no LLM (pure Python, deterministic):

- `validate_product_vision`, `validate_product_strategy`, `validate_prd` — structural checklist.
- `format_prd_markdown` — formats the PRD as Markdown, byte-compatible with the input Product Owner expects.
- `parse_prd_markdown` — the inverse: reconstructs a `PRDDraft` from an already-existing PRD `.md`, preserving the original wording field by field (`--modo prd --prd-existente`), instead of the LLM rewriting everything from scratch based on the text.
- `read_text_file`, `read_jira_issue`, `read_confluence_page`, `parse_chat_transcript`/`format_chat_transcript`, `export_markdown` — input I/O and normalization. `read_jira_issue`/`read_confluence_page` make a real HTTP call (Jira/Confluence Cloud REST API), **read-only** — never writing back.
- `create_confluence_page`/`update_confluence_page` — this agent's only skills that write to an external system: publish the accepted PRD/vision/strategy as a **new** Confluence Cloud page or update an **already-existing** one (`--publicar-confluence`/`--atualizar-confluence`, mutually exclusive), always after explicit human confirmation, separate from the artifact's own acceptance. Unlike Product Owner, which has the update skill but never wired it to any of its own CLI commands — here it has a real consumer.
- `validate_moscow_classification` — confirms the MoSCoW classification matches the original requirements 1:1; if it fails, triggers the safe fallback (empty category for all).
- `compute_rice_score`/`compute_wsjf_score` — compute the RICE/WSJF score from numbers **always** collected from the user (GR-M4), never from the LLM.

Skills with a generator LLM (`OLLAMA_MODEL`, default `mistral`):

- `identify_problem_statement`, `synthesize_personas`, `extract_jobs_to_be_done`, `extract_market_context` (discovery).
- `generate_product_vision`, `generate_vision_clarifying_questions`, `refine_product_vision` (vision).
- `generate_product_strategy`, `generate_strategy_clarifying_questions`, `refine_product_strategy` (strategy).
- `generate_prd`, `generate_prd_clarifying_questions`, `refine_prd` (PRD — 9 core fields).
- `identify_user_journeys`, `identify_business_objectives`, `identify_use_cases`, `identify_external_dependencies`, `identify_technical_assumptions`, `identify_constraints`, `identify_prd_glossary`, `identify_candidate_product_metrics`, `identify_mvp_scope` (PRD — 10 depth fields, section 5.1).
- `classify_moscow` — classifies the accepted PRD's functional requirements in MoSCoW, based on explicit language signals in the text (categorical, follows GR-1 normally — RICE/WSJF's numeric invention risk doesn't apply here).

Skills with an independent reviewer LLM (`OLLAMA_REVIEW_MODEL`, default `phi4` — deliberately a different model from the generator, to mitigate *self-preference bias*):

- `review_product_vision`, `review_product_strategy`, `review_prd`.

Embedding/RAG skills (Ollama `bge-m3` + embedded Qdrant, no external server — this agent's first embedding/vector infrastructure):

- `record_refinement_answer`/`suggest_refinement_answer` — institutional memory of human answers from refinement cycles (`refinement_answer_memory` collection): records each answer given in a cycle (vision, strategy or PRD) and suggests — never auto-applies — the most similar one already given before, for a similar question in a future cycle of the same or a different project (see section 11).

Full input/output/error breakdown of each skill in `docs/agent/skills.md`.

### 5.1 PRD depth

A senior Product Manager's review of a real PRD generated by this agent flagged 12 depth gaps against a mature market-standard PRD. The root cause of most: infrastructure that already existed (personas, synthesized during discovery) but never reached the PRD, and concepts (journey, use cases, dependencies, assumptions, constraints, glossary, KPIs, RF/RNF numbering) that simply had no skill/field at all. The 9 `identify_*` skills above cover those gaps, all under the same GR-1 discipline (never invent, empty if not supported by the source) — with one deliberate exception: `identify_candidate_product_metrics` (GR-M5) suggests metrics typical of the described domain, always in its own field and clearly labeled as a suggestion to confirm, never mixed with `success_criteria` (which stays evidence-only). The MVP-vs-future-scope grouping (`identify_mvp_scope`) is the **lightweight** version of the "formal MVP scope and business case" item that was deliberately deferred (section 11) until a real consumer existed — the very Product Manager who reviewed the PRD is that consumer.

## 6. The interactive refinement cycle (inherited from Product Owner)

The same pattern that sets Product Owner apart repeats here, per artifact (vision, strategy, PRD):

1. `review_*` rejects and produces `review_notes` — concrete findings.
2. `generate_*_clarifying_questions` turns each finding into an objective question.
3. The CLI (`run.py --refinar`) presents the questions in the terminal; a real human answers.
4. `refine_*` rewrites the fields using the answers as real context, explicitly preserving fields the answers don't address — the same care applied to Product Owner's `refine_prd` after a real content-erosion bug found in production.
5. The cycle revalidates and repeats if needed.
6. A prompt explicitly asks whether the user **accepts** the artifact — only that explicit acceptance changes the status to `accepted`, with or without `--refinar`.

## 7. The handoff to AQuA-QE Product Owner

The two agents are **independent** — separate repositories, no shared runtime, no direct call between them. The only bridge is a plain text artifact:

```bash
# Here: generate and export the PRD
uv run python run.py --modo completo --arquivo idea.txt --refinar --saida prd.md

# In Product Owner: consume the PRD, skipping its own --modo prd
# (this agent already ran its own validate/review/refine cycle)
uv run python run.py --modo lote --arquivo prd.md --saida saida_epic/
```

This separation preserves each agent's deterministic/auditable nature — neither agent delegates real-time decisions to the other, and no code change was needed in Product Owner: it already accepts a `.md` file as input.

## 8. Operating modes

- **Discovery** (`--modo descoberta`) — synthesizes problem statement/personas/JTBD/market, with no formal acceptance cycle (these are structured inputs, not standalone "accepted" artifacts).
- **Vision** (`--modo visao`) — generates and refines the product vision until human acceptance.
- **Strategy** (`--modo estrategia`) — generates the vision internally (same input used as the idea) and, once accepted, generates and refines the strategy from it.
- **PRD** (`--modo prd`) — generates and refines the PRD in isolation, with no prior discovery/vision/strategy; behavior equivalent to Product Owner's own `--modo prd` (raw idea → PRD) — the simplest path, preserved for compatibility. With `--prd-existente <file.md>`, it skips generation and loads the already-written PRD via `parse_prd_markdown`, going straight into validation/review/refinement — to refine an existing PRD, not recreate a new one from it.
- **Complete** (`--modo completo`) — chains discovery → vision → strategy → PRD in a single run, using each accepted artifact as context for the next, with human acceptance at every step. The recommended path for the Product Owner handoff.
- **`--publicar-confluence`** (`prd`/`completo`/`visao`/`estrategia` modes) — after explicit human acceptance of the artifact, asks for a title and publishes the page to Confluence Cloud (`create_confluence_page`), returning the created URL. Same pattern as Product Owner's own `--publicar-confluence`, extended beyond the PRD.
- **`--atualizar-confluence <URL or ID>`** (same modes, mutually exclusive with `--publicar-confluence`) — updates an already-existing page (`update_confluence_page`) instead of creating a new one, keeping the title and incrementing the version. No equivalent wired into Product Owner's CLI.
- **`--priorizar {moscow,rice,wsjf}`** (`prd`/`completo` modes, after the PRD is accepted) — prioritizes the functional requirements. `moscow` classifies automatically from language signals in the PRD's own text; `rice`/`wsjf` ask for each requirement's numbers interactively (GR-M4) and compute the score in pure Python. `--saida-priorizacao` exports the result, always in a file separate from the PRD.

## 9. Technical stack

- **Local LLM via Ollama (default)** — `mistral` for generation, `phi4` as an independent reviewer. Same infrastructure choice as Product Owner, deliberately reused instead of introducing a third provider without proven need.
- **NVIDIA NIM provider pilot via toggle** (`LLM_PROVIDER=ollama|nvidia`) — this agent is the chosen pilot for evaluating `build.nvidia.com` (OpenAI-compatible API) as an optional generator/reviewer alternative, preserving the two-independent-models principle (different families, mitigating *self-preference bias*). Ollama remains the unchanged default when `LLM_PROVIDER` is unset. Embedding is out of scope for this pilot.
- **Jira Cloud (REST API, read-only) / Confluence Cloud (REST API, read + new-page creation/update)** — same credentials as Product Owner (`JIRA_BASE_URL`/`JIRA_EMAIL`/`JIRA_API_TOKEN`, plus `CONFLUENCE_SPACE_KEY` to publish), reused via `httpx`; ADF→text (Jira), XHTML storage format→text (reading) and text→storage format (writing) conversion ported verbatim from Product Owner's respective `services/`.
- **No RAG over `knowledge/methodology/` at this phase** — small enough to fit directly in each skill's prompt; `retrieve_chunks` (mirroring Product Owner) is left for a future phase, if the knowledge volume grows. A distinct idea from the refinement institutional memory (section 5), already implemented.
- **`uv`** for dependencies — standalone project (own repository), with `ollama`, `httpx` and `python-dotenv` declared in `pyproject.toml`.
- **Python 3.12+**, `src/` layout.

## 10. Quality and test coverage

The test suite covers all skills and the four workflows, with Ollama/Jira/Confluence calls always mocked — fast, deterministic, with no external infrastructure dependency to run in CI. It includes explicit regressions for the agent's most critical guardrails: a test that verifies `extract_market_context`'s prompt explicitly forbids inventing competitors (GR-M1), a compatibility test confirming that `generate_prd(ideia)` with no context behaves like Product Owner's current `--modo prd`, and a test confirming that `refine_prd`/`refine_product_vision`/`refine_product_strategy` instruct preserving fields the user's answers don't address.

Evaluating the agent in production combines three layers that never replace one another (`docs/agent/evaluation.md`):

1. Automatic checklist (`validate_product_vision`/`validate_product_strategy`/`validate_prd`) — no LLM.
2. LLM-as-judge (`review_product_vision`/`review_product_strategy`/`review_prd`) — a different model from the generator.
3. Mandatory human review — the only act that actually approves an artifact.

## 11. What's still missing (deliberately deferred, not forgotten)

- **Kano prioritization** — **permanently** out of scope, not a phasing question: it structurally depends on customer satisfaction-survey data absent from this agent's input types. MoSCoW/RICE/WSJF are already implemented (`--priorizar`, section 8).
- **Formal business case (ROI/CAC/LTV)** — still out of scope (GR-M2): requires financial projections this agent cannot invent. The lightweight MVP-vs-future-scope grouping (`mvp_scope`/`future_scope`, section 5.1) has already been unblocked — it was the simplest part of what was deferred here, and the missing real consumer now exists.
- **Writing to Jira** — this agent only reads Jira tickets; creating or updating a ticket stays exclusive to Product Owner (`create_jira_story`/`update_jira_issue`), which already covers that case.
- **RAG over `knowledge/methodology/`** — deferred while the knowledge volume still fits directly in the prompt (see section 9). Distinct from the refinement-answer institutional memory (section 5), which already has a real consumer and has been implemented.
- **Resilience to local Ollama infrastructure failures** — same conscious decision as Product Owner: rerun manually instead of adding automatic retry, until there's evidence the complexity cost is worth it.

## 12. How to run it

See `README.md`/`README.pt.md` for the full installation walkthrough (Python 3.12+, `uv`, Ollama + models, `.env.example` → `.env`) and every usage example for `run.py` (`--modo descoberta`/`visao`/`estrategia`/`prd`/`completo`, `--arquivo`/`--texto`/`--jira`/`--confluence`/`--prd-existente`, `--refinar`, `--saida`, `--publicar-confluence`/`--atualizar-confluence`, `--priorizar`/`--saida-priorizacao`).

## 13. Conclusion

AQuA-QE Product Manager doesn't aim to replace the human Product Manager — it aims to eliminate the strategy vacuum that used to precede the PRD in the flow Product Owner already automates. Discovery, vision and strategy stop being steps skipped for lack of time and become, at minimum, attempted in a structured, traceable way before any requirement gets written. The GR-M1/GR-M2/GR-M3/GR-M4 guardrails exist because the riskiest step to automate with an LLM isn't the one where it errs visibly — it's the one where it gets a real fact right (or a plausible-looking prioritization score), but one not authorized by the source, and that slips past review unnoticed. The plain-text-artifact handoff with Product Owner keeps both agents auditable and independent, without requiring any implicit trust between them.

---

**Eduardo Felizardo Cândido**
Senior QA Automation Engineer | AI-driven Testing | Robot Framework & Python
