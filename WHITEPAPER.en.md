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

Five guardrails govern the agent's behavior (`docs/agent/guardrails.md`):

- **GR-1 — Never invent.** Inherited from Product Owner: no discovery, vision, strategy or PRD field is generated without traceable origin in the input source. Fields that can't be identified stay empty, which triggers `pending_clarification`.
- **GR-M1 — Never invent market data.** `extract_market_context` never lists a competitor or trend that isn't literally cited in the input text, even when the model recognizes the market described and "knows" who the real competitors are.
- **GR-M2 — Never invent financial metrics.** No ROI, CAC, LTV projection or financial metric is generated without explicit basis in the source.
- **GR-M3 — Never invent a vision/strategy target.** The vision's `north_star_metric` and each strategy goal's `target`/`timeframe` stay empty when unsupported by the source — never filled with a "typical for the industry" value.
- **Cross-cutting guardrail — No automatic approval.** No skill/workflow ever sets `ArtifactStatus.ACCEPTED`. Approval of Vision, Strategy and PRD is always an explicit human act in the CLI, with or without the interactive refinement cycle.

GR-M1/GR-M2/GR-M3 are what sets this agent apart from Product Owner: GR-1 protects against inventing what the source *should* contain but doesn't mention; GR-M1-M3 protect against the opposite, subtler risk — the model filling a gap with knowledge that is *real*, but not authorized by the source, which looks more "correct" on the surface and is therefore more dangerous to miss in review.

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
   → (outside this agent) AQuA-QE Product Owner consumes the PRD via --modo lote --arquivo
```

Code layers (`src/aqua_qe_product_manager/`):

- **`models/`** — data structures: `ProblemStatement`, `Persona`, `JobToBeDone`, `MarketAnalysis`/`Competitor`, `ProductVision`, `ProductStrategy`/`StrategicGoal`, `PRDDraft` and the `ArtifactStatus` enum (`draft_validated` / `pending_clarification` / `accepted`).
- **`skills/`** — 24 functions, each with a single side effect and a single responsibility (see section 5).
- **`workflow/`** — orchestrates the skill sequence per artifact: `generate_problem_discovery.py` (no generate/finalize/refine trio — discovery has no formal acceptance cycle), `generate_product_vision.py`, `generate_product_strategy.py`, `generate_prd.py` (the latter three following the `generate_x_draft`/`finalize_x`/`refine_x_draft` trio).
- **`orchestrator/product_manager.py`** — four thin entry points, one per mode (`handle_discovery`/`handle_vision`/`handle_strategy`/`handle_prd`), each delegating to its corresponding workflow.
- **`services/`** — `llm_service` (Ollama, generation/review) and `jira_service`/`confluence_service` (Jira Cloud/Confluence Cloud REST API, **read-only** — writing/creating stays exclusive to Product Owner).

`PRDDraft` has the exact same fields as Product Owner's `PRDDraft` — not by coincidence, but by design: it's the compatibility contract that enables the handoff (section 7) with zero code changes on Product Owner's side. Rich artifacts (discovery, vision, strategy) are **input that enriches the generation** of those same fields, not new sections in the exported PRD.

## 5. The 24 skills

Skills with no LLM (pure Python, deterministic):

- `validate_product_vision`, `validate_product_strategy`, `validate_prd` — structural checklist.
- `format_prd_markdown` — formats the PRD as Markdown, byte-compatible with the input Product Owner expects.
- `read_text_file`, `read_jira_issue`, `read_confluence_page`, `parse_chat_transcript`/`format_chat_transcript`, `export_markdown` — input I/O and normalization. `read_jira_issue`/`read_confluence_page` make a real HTTP call (Jira/Confluence Cloud REST API), **read-only** — never writing back.

Skills with a generator LLM (`OLLAMA_MODEL`, default `mistral`):

- `identify_problem_statement`, `synthesize_personas`, `extract_jobs_to_be_done`, `extract_market_context` (discovery).
- `generate_product_vision`, `generate_vision_clarifying_questions`, `refine_product_vision` (vision).
- `generate_product_strategy`, `generate_strategy_clarifying_questions`, `refine_product_strategy` (strategy).
- `generate_prd`, `generate_prd_clarifying_questions`, `refine_prd` (PRD).

Skills with an independent reviewer LLM (`OLLAMA_REVIEW_MODEL`, default `phi4` — deliberately a different model from the generator, to mitigate *self-preference bias*):

- `review_product_vision`, `review_product_strategy`, `review_prd`.

Full input/output/error breakdown of each skill in `docs/agent/skills.md`.

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
- **PRD** (`--modo prd`) — generates and refines the PRD in isolation, with no prior discovery/vision/strategy; behavior equivalent to Product Owner's own `--modo prd` (raw idea → PRD) — the simplest path, preserved for compatibility.
- **Complete** (`--modo completo`) — chains discovery → vision → strategy → PRD in a single run, using each accepted artifact as context for the next, with human acceptance at every step. The recommended path for the Product Owner handoff.

## 9. Technical stack

- **Local LLM via Ollama** — `mistral` for generation, `phi4` as an independent reviewer. Same infrastructure choice as Product Owner, deliberately reused instead of introducing a third provider without proven need.
- **Jira Cloud / Confluence Cloud (REST API, read-only)** — same credentials as Product Owner (`JIRA_BASE_URL`/`JIRA_EMAIL`/`JIRA_API_TOKEN`), reused via `httpx`; ADF→text (Jira) and XHTML storage format→text (Confluence) conversion ported verbatim from Product Owner's respective `services/`.
- **No RAG/embeddings at this phase** — `knowledge/methodology/` is small enough to fit directly in each skill's prompt; `retrieve_chunks` is left for a future phase, if the knowledge volume grows.
- **`uv`** for dependencies — standalone project (own repository), with `ollama`, `httpx` and `python-dotenv` declared in `pyproject.toml`.
- **Python 3.12+**, `src/` layout.

## 10. Quality and test coverage

The test suite covers all 24 skills and the four workflows, with Ollama calls always mocked — fast, deterministic, with no external infrastructure dependency to run in CI. It includes explicit regressions for the agent's most critical guardrails: a test that verifies `extract_market_context`'s prompt explicitly forbids inventing competitors (GR-M1), a compatibility test confirming that `generate_prd(ideia)` with no context behaves like Product Owner's current `--modo prd`, and a test confirming that `refine_prd`/`refine_product_vision`/`refine_product_strategy` instruct preserving fields the user's answers don't address.

Evaluating the agent in production combines three layers that never replace one another (`docs/agent/evaluation.md`):

1. Automatic checklist (`validate_product_vision`/`validate_product_strategy`/`validate_prd`) — no LLM.
2. LLM-as-judge (`review_product_vision`/`review_product_strategy`/`review_prd`) — a different model from the generator.
3. Mandatory human review — the only act that actually approves an artifact.

## 11. What's still missing (deliberately deferred, not forgotten)

- **Formal prioritization** (RICE/MoSCoW/Kano/WSJF) — evaluated and deferred to a future Phase 2, once there's a real backlog large enough to justify it.
- **Formal MVP scope and business case** — same decision: deferred until there's a real consumer for those artifacts.
- **Writing/creating in Jira/Confluence** — this agent only reads from those systems (`--jira`/`--confluence`); publishing the PRD as a new page or updating a ticket stays exclusive to Product Owner (`create_confluence_page`/`update_jira_issue`), which already covers that case.
- **RAG over `knowledge/methodology/`** — deferred while the knowledge volume still fits directly in the prompt (see section 9).
- **Resilience to local Ollama infrastructure failures** — same conscious decision as Product Owner: rerun manually instead of adding automatic retry, until there's evidence the complexity cost is worth it.

## 12. How to run it

See `README.md`/`README.pt.md` for the full installation walkthrough (Python 3.12+, `uv`, Ollama + models, `.env.example` → `.env`) and every usage example for `run.py` (`--modo descoberta`/`visao`/`estrategia`/`prd`/`completo`, `--arquivo`/`--texto`, `--refinar`, `--saida`).

## 13. Conclusion

AQuA-QE Product Manager doesn't aim to replace the human Product Manager — it aims to eliminate the strategy vacuum that used to precede the PRD in the flow Product Owner already automates. Discovery, vision and strategy stop being steps skipped for lack of time and become, at minimum, attempted in a structured, traceable way before any requirement gets written. The GR-M1/GR-M2/GR-M3 guardrails exist because the riskiest step to automate with an LLM isn't the one where it errs visibly — it's the one where it gets a real fact right, but one not authorized by the source, and that slips past review unnoticed. The plain-text-artifact handoff with Product Owner keeps both agents auditable and independent, without requiring any implicit trust between them.

---

**Eduardo Felizardo Cândido**
Senior QA Automation Engineer | AI-driven Testing | Robot Framework & Python
