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

Seis guardrails governam o comportamento do agente (`docs/agent/guardrails.md`):

- **GR-1 — Nunca inventar.** Herdado do Product Owner: nenhum campo de descoberta, visão, estratégia ou PRD é gerado sem origem rastreável na fonte de entrada. Campos não identificáveis ficam vazios, o que aciona `pending_clarification`.
- **GR-M1 — Nunca inventar dado de mercado.** `extract_market_context` nunca lista um concorrente ou tendência que não esteja citado literalmente no texto de entrada, mesmo que o modelo reconheça o mercado descrito e "saiba" quem são concorrentes reais dele.
- **GR-M2 — Nunca inventar métrica financeira.** Nenhuma projeção de ROI, CAC, LTV ou métrica financeira é gerada sem base explícita na fonte.
- **GR-M3 — Nunca inventar meta de visão/estratégia.** `north_star_metric` (visão) e `target`/`timeframe` de cada meta (estratégia) ficam vazios quando não sustentados pela fonte — nunca preenchidos com um valor "típico do setor".
- **GR-M4 — Nunca estimar número de priorização (RICE/WSJF).** Reach, impact, confidence, effort, business value, time criticality, risk reduction e job size vêm sempre de `input()` do usuário no CLI; `compute_rice_score`/`compute_wsjf_score` são Python puro, sem chamada ao LLM.
- **Guardrail transversal — Sem aprovação automática.** Nenhuma skill/workflow define `ArtifactStatus.ACCEPTED`. A aprovação de Visão, Estratégia e PRD é sempre um ato humano explícito no CLI, com ou sem o ciclo de refinamento interativo.

GR-M1/GR-M2/GR-M3/GR-M4 são o que distingue este agente do Product Owner: GR-1 protege contra inventar o que a fonte *deveria* conter, mas não menciona; GR-M1-M4 protegem contra o risco oposto e mais sutil — o modelo (ou, no caso do RICE/WSJF, o próprio agente) preencher uma lacuna com um número que *parece* plausível, mas não foi autorizado pela fonte nem pelo usuário, o que é mais perigoso de passar despercebido em revisão do que um erro óbvio.

## 4. Arquitetura

```
Entrada (.txt/Markdown/chat/Jira/Confluence)
   → read_text_file / parse_chat_transcript+format_chat_transcript (só chat) / read_jira_issue / read_confluence_page (só leitura)
   → identify_problem_statement / synthesize_personas / extract_jobs_to_be_done / extract_market_context (descoberta, opcional)
   → generate_product_vision  (LLM gerador — mistral)
   → validate_product_vision  (checklist Python puro)
   → review_product_vision    (LLM revisor independente — phi4)
   → [se reprovado] generate_vision_clarifying_questions → resposta humana → refine_product_vision → revalidar
   → aceite humano explícito
   → generate_product_strategy (usa a visão aceita) → validate/review/refine → aceite humano explícito
   → generate_prd (usa descoberta + visão + estratégia, quando existirem) → validate/review/refine → aceite humano explícito
   → format_prd_markdown → export_markdown
   → [opcional] create_confluence_page / update_confluence_page (--publicar-confluence / --atualizar-confluence, após confirmação humana explícita)
   → [opcional] classify_moscow ou compute_rice_score/compute_wsjf_score (--priorizar, arquivo separado do PRD)
   → (fora deste agente) AQuA-QE Product Owner consome o PRD via --modo lote --arquivo
```

Camadas do código (`src/aqua_qe_product_manager/`):

- **`models/`** — estruturas de dados: `ProblemStatement`, `Persona`, `JobToBeDone`, `MarketAnalysis`/`Competitor`, `ProductVision`, `ProductStrategy`/`StrategicGoal`, `PRDDraft`, `PrioritizedRequirement`/`PriorityInputs` (deliberadamente fora de `PRDDraft`, nunca altera o contrato de handoff) e o enum `ArtifactStatus` (`draft_validated` / `pending_clarification` / `accepted`).
- **`skills/`** — cada uma com um único efeito colateral e uma única responsabilidade (ver seção 5).
- **`workflow/`** — orquestração da sequência de skills por artefato: `generate_problem_discovery.py` (sem trio generate/finalize/refine — descoberta não tem ciclo de aceite formal), `generate_product_vision.py`, `generate_product_strategy.py`, `generate_prd.py` (os três últimos seguindo o trio `generate_x_draft`/`finalize_x`/`refine_x_draft`).
- **`orchestrator/product_manager.py`** — quatro pontos de entrada finos, um por modo (`handle_discovery`/`handle_vision`/`handle_strategy`/`handle_prd`), cada um delegando ao workflow correspondente.
- **`services/`** — `llm_service` (Ollama, geração/revisão), `jira_service` (Jira Cloud REST API, **apenas leitura**) e `confluence_service` (Confluence Cloud REST API, leitura + criação de página nova + atualização de página existente — as únicas escritas externas deste agente, usadas por `--publicar-confluence`/`--atualizar-confluence`).

`PRDDraft` tem exatamente os mesmos campos do `PRDDraft` do Product Owner — não por coincidência, mas por design: é o contrato de compatibilidade que permite o handoff (seção 7) sem nenhuma mudança de código no lado do Product Owner. Artefatos ricos (descoberta, visão, estratégia) são **input que enriquece a geração** desses mesmos campos, não seções novas no PRD exportado.

## 5. As skills

Skills sem LLM (Python puro, determinísticas):

- `validate_product_vision`, `validate_product_strategy`, `validate_prd` — checklist estrutural.
- `format_prd_markdown` — formata o PRD em Markdown, byte-compatível com a entrada esperada pelo Product Owner.
- `parse_prd_markdown` — o inverso: reconstrói um `PRDDraft` a partir de um PRD `.md` já existente, preservando a redação original campo a campo (`--modo prd --prd-existente`), em vez de o LLM reescrever tudo do zero a partir do texto.
- `read_text_file`, `read_jira_issue`, `read_confluence_page`, `parse_chat_transcript`/`format_chat_transcript`, `export_markdown` — I/O e normalização de entrada. `read_jira_issue`/`read_confluence_page` fazem chamada HTTP real (Jira/Confluence Cloud REST API), **apenas leitura** — nunca escrevem de volta.
- `create_confluence_page`/`update_confluence_page` — as únicas skills deste agente que escrevem num sistema externo: publicam o PRD/visão/estratégia aceitos como página **nova** ou atualizam uma página **já existente** no Confluence Cloud (`--publicar-confluence`/`--atualizar-confluence`, mutuamente exclusivos), sempre após confirmação humana explícita e distinta do aceite do artefato. Diferente do Product Owner, que tem a skill de atualização mas nunca a conectou a nenhum comando do próprio CLI — aqui ela tem um consumidor real.
- `validate_moscow_classification` — confere que a classificação MoSCoW corresponde 1:1 aos requisitos originais; se falhar, aciona o fallback seguro (categoria vazia para todos).
- `compute_rice_score`/`compute_wsjf_score` — calculam o score RICE/WSJF a partir de números **sempre** coletados do usuário (GR-M4), nunca do LLM.

Skills com LLM gerador (`OLLAMA_MODEL`, padrão `mistral`):

- `identify_problem_statement`, `synthesize_personas`, `extract_jobs_to_be_done`, `extract_market_context` (descoberta).
- `generate_product_vision`, `generate_vision_clarifying_questions`, `refine_product_vision` (visão).
- `generate_product_strategy`, `generate_strategy_clarifying_questions`, `refine_product_strategy` (estratégia).
- `generate_prd`, `generate_prd_clarifying_questions`, `refine_prd` (PRD — 9 campos centrais).
- `identify_user_journeys`, `identify_business_objectives`, `identify_use_cases`, `identify_external_dependencies`, `identify_technical_assumptions`, `identify_constraints`, `identify_prd_glossary`, `identify_candidate_product_metrics`, `identify_mvp_scope` (PRD — 10 campos de profundidade, seção 5.1).
- `classify_moscow` — classifica os requisitos funcionais do PRD aceito em MoSCoW, a partir de sinal de linguagem explícito no texto (categórico, segue GR-1 normalmente — o risco de invenção numérica de RICE/WSJF não se aplica aqui).

Skills com LLM revisor independente (`OLLAMA_REVIEW_MODEL`, padrão `phi4` — deliberadamente um modelo diferente do gerador, para mitigar *self-preference bias*):

- `review_product_vision`, `review_product_strategy`, `review_prd`.

Detalhamento completo de entrada/saída/erros de cada skill em `docs/agent/skills.md`.

### 5.1 Profundidade do PRD

Uma revisão de um PRD real gerado por este agente (por um Product Manager sênior) apontou 12 lacunas de profundidade frente a um PRD maduro de mercado. A causa raiz da maioria: infraestrutura que já existia (personas, sintetizadas na descoberta) mas nunca chegava ao PRD, e conceitos (jornada, casos de uso, dependências, premissas, restrições, glossário, KPIs, numeração RF/RNF) que simplesmente não tinham skill/campo nenhum. As 9 skills de `identify_*` acima cobrem essas lacunas, todas sob a mesma disciplina GR-1 (nunca inventar, vazio se não sustentado pela fonte) — com uma única exceção deliberada: `identify_candidate_product_metrics` (GR-M5) sugere métricas típicas de mercado para o domínio descrito, sempre em campo próprio e claramente rotulada como sugestão a confirmar, nunca misturada com `success_criteria` (que continua evidence-only). O agrupamento MVP vs. versão futura (`identify_mvp_scope`) é a versão **leve** do item "MVP scope formal e business case", que estava deliberadamente adiado (seção 11) até existir um consumidor real — o próprio Product Manager que revisou o PRD é esse consumidor.

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
- **PRD** (`--modo prd`) — gera e refina o PRD isoladamente, sem descoberta/visão/estratégia prévias; comportamento equivalente ao `--modo prd` do Product Owner (ideia crua → PRD) — o caminho mais simples, preservado por compatibilidade. Com `--prd-existente <arquivo.md>`, pula a geração e carrega o PRD já pronto via `parse_prd_markdown`, indo direto para validação/revisão/refinamento — para refinar um PRD que já existe, não recriar um novo a partir dele.
- **Completo** (`--modo completo`) — encadeia descoberta → visão → estratégia → PRD numa execução só, usando cada artefato aceito como contexto para o próximo, com aceite humano em cada etapa. O caminho recomendado para o handoff ao Product Owner.
- **`--publicar-confluence`** (modos `prd`/`completo`/`visao`/`estrategia`) — após aceitação humana explícita do artefato, pergunta o título e publica a página no Confluence Cloud (`create_confluence_page`), retornando a URL criada. Mesmo padrão do `--publicar-confluence` do Product Owner, estendido para além do PRD.
- **`--atualizar-confluence <URL ou ID>`** (mesmos modos, mutuamente exclusivo com `--publicar-confluence`) — atualiza uma página já existente (`update_confluence_page`) em vez de criar uma nova, mantendo título e incrementando a versão. Sem equivalente no Product Owner conectado ao CLI.
- **`--priorizar {moscow,rice,wsjf}`** (modos `prd`/`completo`, depois do PRD aceito) — prioriza os requisitos funcionais. `moscow` classifica automaticamente a partir de sinal de linguagem no texto do PRD; `rice`/`wsjf` pedem os números de cada requisito interativamente (GR-M4) e calculam o score em Python puro. `--saida-priorizacao` exporta o resultado, sempre num arquivo separado do PRD.

## 9. Stack técnico

- **LLM local via Ollama** — `mistral` para geração, `phi4` como revisor independente. Mesma escolha de infraestrutura do Product Owner, deliberadamente reaproveitada em vez de introduzir um terceiro provedor sem necessidade comprovada.
- **Jira Cloud (REST API, leitura) / Confluence Cloud (REST API, leitura + criação/atualização de página)** — mesmas credenciais do Product Owner (`JIRA_BASE_URL`/`JIRA_EMAIL`/`JIRA_API_TOKEN`, mais `CONFLUENCE_SPACE_KEY` para publicar), reaproveitadas via `httpx`; conversão ADF→texto (Jira), storage format XHTML→texto (leitura) e texto→storage format (escrita) portadas verbatim dos respectivos `services/` do Product Owner.
- **Sem RAG/embeddings nesta fase** — `knowledge/methodology/` é pequeno o suficiente para caber direto no prompt de cada skill; `retrieve_chunks` fica para uma fase futura, se o volume de conhecimento crescer.
- **`uv`** para dependências — projeto standalone (repositório próprio), com `ollama`, `httpx` e `python-dotenv` declarados em `pyproject.toml`.
- **Python 3.12+**, `src/` layout.

## 10. Qualidade e cobertura de testes

A suíte de testes cobre todas as skills e os quatro workflows, com chamadas a Ollama sempre mockadas — rápidos, determinísticos, sem dependência de infraestrutura externa para rodar em CI. Inclui regressões explícitas para os guardrails mais críticos do agente: um teste que verifica que o prompt de `extract_market_context` proíbe explicitamente inventar concorrentes (GR-M1), um teste de compatibilidade que confirma que `generate_prd(ideia)` sem contexto se comporta como o `--modo prd` atual do Product Owner, e um teste que confirma que `refine_prd`/`refine_product_vision`/`refine_product_strategy` instruem a preservar campos não abordados pelas respostas do usuário.

A avaliação do agente em produção combina três camadas que nunca se substituem (`docs/agent/evaluation.md`):

1. Checklist automático (`validate_product_vision`/`validate_product_strategy`/`validate_prd`) — sem LLM.
2. LLM-como-juiz (`review_product_vision`/`review_product_strategy`/`review_prd`) — modelo diferente do gerador.
3. Revisão humana obrigatória — único ato que efetivamente aprova um artefato.

## 11. O que ainda falta (deliberadamente adiado, não esquecido)

- **Priorização Kano** — **permanentemente** fora de escopo, não uma questão de fase: depende estruturalmente de dados de pesquisa de satisfação de cliente ausentes do tipo de entrada deste agente. MoSCoW/RICE/WSJF já estão implementados (`--priorizar`, seção 8).
- **Business case formal (ROI/CAC/LTV)** — continua fora de escopo (GR-M2): exige projeção financeira que este agente não pode inventar. O agrupamento leve MVP vs. versão futura (`mvp_scope`/`future_scope`, seção 5.1) já foi desbloqueado — era a parte mais simples do que estava adiado aqui, e o consumidor real que faltava já existe.
- **Escrita no Jira** — este agente só lê tickets Jira; criar ou atualizar um ticket continua exclusivo do Product Owner (`create_jira_story`/`update_jira_issue`), que já cobre esse caso.
- **RAG sobre `knowledge/methodology/`** — adiado enquanto o volume de conhecimento couber direto no prompt (ver seção 9).
- **Resiliência a falhas de infraestrutura do Ollama local** — mesma decisão consciente do Product Owner: reexecutar manualmente em vez de adicionar retry automático, até haver evidência de que o custo de complexidade compensa.

## 12. Como executar

Ver `README.md`/`README.pt.md` para o passo a passo completo de instalação (Python 3.12+, `uv`, Ollama + modelos, `.env.example` → `.env`) e todos os exemplos de uso do `run.py` (`--modo descoberta`/`visao`/`estrategia`/`prd`/`completo`, `--arquivo`/`--texto`/`--jira`/`--confluence`/`--prd-existente`, `--refinar`, `--saida`, `--publicar-confluence`/`--atualizar-confluence`, `--priorizar`/`--saida-priorizacao`).

## 13. Conclusão

O AQuA-QE Product Manager não busca substituir o Product Manager humano — busca eliminar o vácuo de estratégia que precedia o PRD no fluxo já automatizado pelo Product Owner. Descoberta, visão e estratégia deixam de ser etapas puladas por falta de tempo e passam a ser, no mínimo, tentadas de forma estruturada e rastreável antes de qualquer requisito ser escrito. Os guardrails GR-M1/GR-M2/GR-M3/GR-M4 existem porque a etapa mais arriscada de automatizar com um LLM não é a que ele erra visivelmente — é a que ele acerta um dado real (ou plausível, no caso de um score de priorização), mas não autorizado pela fonte, e isso passa despercebido em revisão. O handoff por artefato de texto simples com o Product Owner mantém os dois agentes auditáveis e independentes, sem exigir nenhuma confiança implícita entre eles.

---

**Eduardo Felizardo Cândido**
Senior QA Automation Engineer | AI-driven Testing | Robot Framework & Python
