# AQuA-QE Product Manager — Whitepaper

> Also available in [English](WHITEPAPER.en.md).

> Agente de descoberta e estratégia de produto que sintetiza problem statement, personas, jobs to be done, contexto de mercado, visão de produto, estratégia de produto e PRD a partir de uma ideia informal ou transcrição de chat — com rastreabilidade obrigatória à fonte, validação automática e revisão humana no centro do ciclo, produzindo um PRD que serve de entrada direta ao agente irmão AQuA-QE Product Owner.

Repositório: [github.com/dufelizardo/AQuA-QE-Product-Manager](https://github.com/dufelizardo/AQuA-QE-Product-Manager)

---

## 1. Resumo executivo

O AQuA-QE Product Owner já cobre bem a parte de **execução**: transforma um PRD em Epics, User Stories e Critérios de Aceitação, com ciclo humano-no-loop completo. Faltava a parte de **estratégia** — decidir o quê construir e por quê, antes de qualquer PRD existir. Um PRD gerado a partir de uma ideia crua, sem descoberta prévia (personas, jobs to be done, problema real), sem visão e estratégia de produto formalizadas, carrega esse vácuo adiante: Épicos e User Stories bem estruturados, mas potencialmente resolvendo o problema errado.

O AQuA-QE Product Manager preenche essa lacuna como um agente novo e independente, não como uma extensão acoplada ao Product Owner. A partir de uma ideia informal ou de uma transcrição de conversa, ele sintetiza um problem statement, personas, jobs to be done e contexto de mercado — sempre que a fonte sustentar essa síntese —, gera uma visão de produto, deriva uma estratégia de produto a partir dela e, por fim, gera o PRD, incorporando tudo o que foi aceito nas etapas anteriores. Cada artefato passa pelo mesmo padrão de qualidade: validação automática, revisão por um segundo LLM independente e aceite humano sempre perguntado explicitamente — nunca automático.

O diferencial mais crítico deste agente, sem equivalente direto no Product Owner, é o guardrail contra invenção de dado de mercado e financeiro: um LLM tende a preencher lacunas de "conhecimento de mercado" com informação real, mas não citada pelo usuário — nomes de concorrentes, tamanho de mercado, projeções. Este agente trata isso como o erro mais grave que pode cometer, e o proíbe explicitamente em nível de prompt e de arquitetura, mesmo quando o modelo "sabe" a resposta certa.

## 2. Fundamentação metodológica

Nenhum critério usado pelo agente foi inventado. Cada um está documentado em `knowledge/methodology/` e é referenciado diretamente pelas skills e guardrails do agente:

| Framework | Papel no agente |
|---|---|
| **Jobs to Be Done** (`jtbd.md`) | Estrutura `extract_jobs_to_be_done` no formato "Quando ..., eu quero ..., para que ..." e orienta o `statement` da visão a endereçar um job real, não uma feature. |
| **North Star Framework** (`north_star_framework.md`) | Orienta o campo `north_star_metric` da visão — uma métrica de valor para o cliente, não uma métrica de vaidade ou de negócio pura. |
| **BABOK** (`babok.md`) | O modelo BACCM (Need/Stakeholder/Value/Solution/Change/Context) fornece o vocabulário estrutural da descoberta e da visão. |
| **ISO/IEC/IEEE 29148** (`iso29148.md`) | Referência para qualidade e completude dos requisitos funcionais/não funcionais do PRD. |

Esses documentos não são decoração: `generate_product_vision` referencia o North Star Framework diretamente no prompt para orientar (sem forçar) o formato da métrica-alvo, e `validate_prd`/`review_prd` aplicam os critérios de "requisito bem escrito" da ISO 29148.

## 3. Princípios de design (guardrails)

Cinco guardrails governam o comportamento do agente (`docs/agent/guardrails.md`):

- **GR-1 — Nunca inventar.** Herdado do Product Owner: nenhum campo de descoberta, visão, estratégia ou PRD é gerado sem origem rastreável na fonte de entrada. Campos não identificáveis ficam vazios, o que aciona `pending_clarification`.
- **GR-M1 — Nunca inventar dado de mercado.** `extract_market_context` nunca lista um concorrente ou tendência que não esteja citado literalmente no texto de entrada, mesmo que o modelo reconheça o mercado descrito e "saiba" quem são concorrentes reais dele.
- **GR-M2 — Nunca inventar métrica financeira.** Nenhuma projeção de ROI, CAC, LTV ou métrica financeira é gerada sem base explícita na fonte.
- **GR-M3 — Nunca inventar meta de visão/estratégia.** `north_star_metric` (visão) e `target`/`timeframe` de cada meta (estratégia) ficam vazios quando não sustentados pela fonte — nunca preenchidos com um valor "típico do setor".
- **Guardrail transversal — Sem aprovação automática.** Nenhuma skill/workflow define `ArtifactStatus.ACCEPTED`. A aprovação de Visão, Estratégia e PRD é sempre um ato humano explícito no CLI, com ou sem o ciclo de refinamento interativo.

GR-M1/GR-M2/GR-M3 são o que distingue este agente do Product Owner: GR-1 protege contra inventar o que a fonte *deveria* conter, mas não menciona; GR-M1-M3 protegem contra o risco oposto e mais sutil — o modelo preencher uma lacuna com conhecimento *real*, mas não autorizado pela fonte, o que parece mais "certo" superficialmente e por isso é mais perigoso de passar despercebido em revisão.

## 4. Arquitetura

```
Entrada (.txt/Markdown/chat)
   → read_text_file / parse_chat_transcript+format_chat_transcript (só chat)
   → identify_problem_statement / synthesize_personas / extract_jobs_to_be_done / extract_market_context (descoberta, opcional)
   → generate_product_vision  (LLM gerador — mistral)
   → validate_product_vision  (checklist Python puro)
   → review_product_vision    (LLM revisor independente — phi4)
   → [se reprovado] generate_vision_clarifying_questions → resposta humana → refine_product_vision → revalidar
   → aceite humano explícito
   → generate_product_strategy (usa a visão aceita) → validate/review/refine → aceite humano explícito
   → generate_prd (usa descoberta + visão + estratégia, quando existirem) → validate/review/refine → aceite humano explícito
   → format_prd_markdown → export_markdown
   → (fora deste agente) AQuA-QE Product Owner consome o PRD via --modo lote --arquivo
```

Camadas do código (`src/aqua_qe_product_manager/`):

- **`models/`** — estruturas de dados: `ProblemStatement`, `Persona`, `JobToBeDone`, `MarketAnalysis`/`Competitor`, `ProductVision`, `ProductStrategy`/`StrategicGoal`, `PRDDraft` e o enum `ArtifactStatus` (`draft_validated` / `pending_clarification` / `accepted`).
- **`skills/`** — 24 funções, cada uma com um único efeito colateral e uma única responsabilidade (ver seção 5).
- **`workflow/`** — orquestração da sequência de skills por artefato: `generate_problem_discovery.py` (sem trio generate/finalize/refine — descoberta não tem ciclo de aceite formal), `generate_product_vision.py`, `generate_product_strategy.py`, `generate_prd.py` (os três últimos seguindo o trio `generate_x_draft`/`finalize_x`/`refine_x_draft`).
- **`orchestrator/product_manager.py`** — quatro pontos de entrada finos, um por modo (`handle_discovery`/`handle_vision`/`handle_strategy`/`handle_prd`), cada um delegando ao workflow correspondente.
- **`services/`** — uma única integração externa nesta fase: `llm_service` (Ollama).

`PRDDraft` tem exatamente os mesmos campos do `PRDDraft` do Product Owner — não por coincidência, mas por design: é o contrato de compatibilidade que permite o handoff (seção 7) sem nenhuma mudança de código no lado do Product Owner. Artefatos ricos (descoberta, visão, estratégia) são **input que enriquece a geração** desses mesmos campos, não seções novas no PRD exportado.

## 5. As 24 skills

Skills sem LLM (Python puro, determinísticas):

- `validate_product_vision`, `validate_product_strategy`, `validate_prd` — checklist estrutural.
- `format_prd_markdown` — formata o PRD em Markdown, byte-compatível com a entrada esperada pelo Product Owner.
- `read_text_file`, `parse_chat_transcript`/`format_chat_transcript`, `export_markdown` — I/O e normalização de entrada.

Skills com LLM gerador (`OLLAMA_MODEL`, padrão `mistral`):

- `identify_problem_statement`, `synthesize_personas`, `extract_jobs_to_be_done`, `extract_market_context` (descoberta).
- `generate_product_vision`, `generate_vision_clarifying_questions`, `refine_product_vision` (visão).
- `generate_product_strategy`, `generate_strategy_clarifying_questions`, `refine_product_strategy` (estratégia).
- `generate_prd`, `generate_prd_clarifying_questions`, `refine_prd` (PRD).

Skills com LLM revisor independente (`OLLAMA_REVIEW_MODEL`, padrão `phi4` — deliberadamente um modelo diferente do gerador, para mitigar *self-preference bias*):

- `review_product_vision`, `review_product_strategy`, `review_prd`.

Detalhamento completo de entrada/saída/erros de cada skill em `docs/agent/skills.md`.

## 6. O ciclo de refinamento interativo (herdado do Product Owner)

O mesmo padrão que diferencia o Product Owner se repete aqui, por artefato (visão, estratégia, PRD):

1. `review_*` reprova e produz `review_notes` — apontamentos concretos.
2. `generate_*_clarifying_questions` transforma cada apontamento em uma pergunta objetiva.
3. O CLI (`run.py --refinar`) apresenta as perguntas no terminal; um humano real responde.
4. `refine_*` reescreve os campos usando as respostas como contexto real, preservando explicitamente os campos que as respostas não abordam — mesmo cuidado aplicado ao `refine_prd` do Product Owner após um bug real de erosão de conteúdo encontrado em produção.
5. O ciclo revalida e repete se necessário.
6. Um prompt pergunta explicitamente se o usuário **aceita** o artefato — só esse aceite muda o status para `accepted`, com ou sem `--refinar`.

## 7. O handoff para o AQuA-QE Product Owner

Os dois agentes são **independentes** — repositórios separados, sem runtime compartilhado, sem chamada direta entre um e outro. A única ponte é um artefato de texto:

```bash
# Aqui: gera e exporta o PRD
uv run python run.py --modo completo --arquivo ideia.txt --refinar --saida prd.md

# No Product Owner: consome o PRD, pulando o próprio --modo prd
# (este agente já rodou seu próprio ciclo validate/review/refine)
uv run python run.py --modo lote --arquivo prd.md --saida saida_epic/
```

Essa separação preserva a característica determinística/auditável de cada agente — nenhum dos dois delega decisão em tempo real ao outro, e nenhuma mudança de código foi necessária no Product Owner: ele já aceita arquivo `.md` como entrada.

## 8. Modos de operação

- **Descoberta** (`--modo descoberta`) — sintetiza problem statement/personas/JTBD/mercado, sem ciclo de aceite formal (são insumos estruturados, não artefatos "aceitos" isoladamente).
- **Visão** (`--modo visao`) — gera e refina a visão de produto até aceite humano.
- **Estratégia** (`--modo estrategia`) — gera a visão internamente (mesma entrada como ideia) e, uma vez aceita, gera e refina a estratégia a partir dela.
- **PRD** (`--modo prd`) — gera e refina o PRD isoladamente, sem descoberta/visão/estratégia prévias; comportamento equivalente ao `--modo prd` do Product Owner (ideia crua → PRD) — o caminho mais simples, preservado por compatibilidade.
- **Completo** (`--modo completo`) — encadeia descoberta → visão → estratégia → PRD numa execução só, usando cada artefato aceito como contexto para o próximo, com aceite humano em cada etapa. O caminho recomendado para o handoff ao Product Owner.

## 9. Stack técnico

- **LLM local via Ollama** — `mistral` para geração, `phi4` como revisor independente. Mesma escolha de infraestrutura do Product Owner, deliberadamente reaproveitada em vez de introduzir um terceiro provedor sem necessidade comprovada.
- **Sem RAG/embeddings nesta fase** — `knowledge/methodology/` é pequeno o suficiente para caber direto no prompt de cada skill; `retrieve_chunks` fica para uma fase futura, se o volume de conhecimento crescer.
- **`uv`** para dependências — projeto standalone (repositório próprio), com `ollama`, `httpx` e `python-dotenv` declarados em `pyproject.toml`.
- **Python 3.12+**, `src/` layout.

## 10. Qualidade e cobertura de testes

A suíte de testes cobre todas as 24 skills e os quatro workflows, com chamadas a Ollama sempre mockadas — rápidos, determinísticos, sem dependência de infraestrutura externa para rodar em CI. Inclui regressões explícitas para os guardrails mais críticos do agente: um teste que verifica que o prompt de `extract_market_context` proíbe explicitamente inventar concorrentes (GR-M1), um teste de compatibilidade que confirma que `generate_prd(ideia)` sem contexto se comporta como o `--modo prd` atual do Product Owner, e um teste que confirma que `refine_prd`/`refine_product_vision`/`refine_product_strategy` instruem a preservar campos não abordados pelas respostas do usuário.

A avaliação do agente em produção combina três camadas que nunca se substituem (`docs/agent/evaluation.md`):

1. Checklist automático (`validate_product_vision`/`validate_product_strategy`/`validate_prd`) — sem LLM.
2. LLM-como-juiz (`review_product_vision`/`review_product_strategy`/`review_prd`) — modelo diferente do gerador.
3. Revisão humana obrigatória — único ato que efetivamente aprova um artefato.

## 11. O que ainda falta (deliberadamente adiado, não esquecido)

- **Priorização formal** (RICE/MoSCoW/Kano/WSJF) — avaliada e adiada para uma Fase 2, quando houver um backlog real grande o suficiente para justificá-la.
- **MVP scope formal e business case** — mesma decisão: adiados até haver um consumidor real desses artefatos.
- **Integração com Jira/Confluence** — o Product Owner já cobre a leitura/escrita nesses sistemas; este agente, nesta fase, trabalha só com arquivo de texto/chat como entrada.
- **RAG sobre `knowledge/methodology/`** — adiado enquanto o volume de conhecimento couber direto no prompt (ver seção 9).
- **Resiliência a falhas de infraestrutura do Ollama local** — mesma decisão consciente do Product Owner: reexecutar manualmente em vez de adicionar retry automático, até haver evidência de que o custo de complexidade compensa.

## 12. Como executar

Ver `README.md`/`README.pt.md` para o passo a passo completo de instalação (Python 3.12+, `uv`, Ollama + modelos, `.env.example` → `.env`) e todos os exemplos de uso do `run.py` (`--modo descoberta`/`visao`/`estrategia`/`prd`/`completo`, `--arquivo`/`--texto`, `--refinar`, `--saida`).

## 13. Conclusão

O AQuA-QE Product Manager não busca substituir o Product Manager humano — busca eliminar o vácuo de estratégia que precedia o PRD no fluxo já automatizado pelo Product Owner. Descoberta, visão e estratégia deixam de ser etapas puladas por falta de tempo e passam a ser, no mínimo, tentadas de forma estruturada e rastreável antes de qualquer requisito ser escrito. Os guardrails GR-M1/GR-M2/GR-M3 existem porque a etapa mais arriscada de automatizar com um LLM não é a que ele erra visivelmente — é a que ele acerta um dado real, mas não autorizado pela fonte, e isso passa despercebido em revisão. O handoff por artefato de texto simples com o Product Owner mantém os dois agentes auditáveis e independentes, sem exigir nenhuma confiança implícita entre eles.

---

**Eduardo Felizardo Cândido**
Senior QA Automation Engineer | AI-driven Testing | Robot Framework & Python
