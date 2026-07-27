# System Design

> Estrutura conforme `../standards/system_design_standard.md`.

## Visão geral da arquitetura

O agente é um pipeline de skills orquestrado sequencialmente, com dois pontos de checagem antes de qualquer saída ser considerada válida: validação automática (checklist Python puro) e revisão humana obrigatória. Não há aprovação automática — ver `guardrails.md`.

```
Entrada (.txt/Markdown/chat/Jira/Confluence)
   → read_text_file / parse_chat_transcript+format_chat_transcript (chat) / read_jira_issue / read_confluence_page
   → identify_problem_statement / synthesize_personas / extract_jobs_to_be_done / extract_market_context (descoberta, opcional)
   → generate_product_vision → validate_product_vision → review_product_vision
      → [se reprovado] generate_vision_clarifying_questions → resposta humana → refine_product_vision → revalidar
      → aceite humano explícito
   → generate_product_strategy (usa a visão aceita) → validate/review/refine → aceite humano explícito
   → generate_prd (usa descoberta + visão + estratégia, quando existirem)
   → identify_user_journeys / identify_business_objectives / identify_use_cases /
     identify_external_dependencies / identify_technical_assumptions / identify_constraints /
     identify_prd_glossary / identify_candidate_product_metrics / identify_mvp_scope
     (enriquecimento de profundidade, reaproveita personas da descoberta quando existirem)
   → validate_prd → review_prd
      → [se reprovado] generate_prd_clarifying_questions → resposta humana → refine_prd
        → re-deriva o enriquecimento a partir do PRD já refinado → revalidar
      → aceite humano explícito
   → format_prd_markdown → export_markdown
   → [opcional] create_confluence_page / update_confluence_page (--publicar-confluence / --atualizar-confluence, após confirmação humana explícita)
   → [opcional] classify_moscow ou compute_rice_score/compute_wsjf_score (--priorizar, arquivo separado do PRD)
   → (fora deste agente) AQuA-QE Product Owner consome o PRD via --modo lote --arquivo
```

Caminho alternativo, só para PRD (`--modo prd --prd-existente arquivo.md`): `parse_prd_markdown` substitui `generate_prd` — carrega um PRD já pronto como `PRDDraft`, preservando a redação original campo a campo, e segue direto para `validate_prd → review_prd → [refine] → aceite`, sem reescrita não solicitada pelo LLM.

## Componentes

- **Orquestrador/Agente** — decide a sequência de skills a chamar e quando interromper o fluxo por ambiguidade (ver `agent_design.md`). Implementado em `../../src/aqua_qe_product_manager/orchestrator/product_manager.py`.
- **Workflows** — orquestração da sequência de skills por artefato (descoberta, visão, estratégia, PRD), implementados em `../../src/aqua_qe_product_manager/workflow/`.
- **Skills** — funções descritas em `skills.md`, implementadas em `../../src/aqua_qe_product_manager/skills/`.
- **Modelos de dados** — estruturas (`ProblemStatement`, `Persona`, `JobToBeDone`, `MarketAnalysis`/`Competitor`, `ProductVision`, `ProductStrategy`/`StrategicGoal`, `PRDDraft`, `UserJourney`, `BusinessObjective`, `GlossaryTerm`, `PrioritizedRequirement`/`PriorityInputs`) implementadas em `../../src/aqua_qe_product_manager/models/`, conforme `output_schema.md`. `PRDDraft` tem 9 campos centrais (byte-compatíveis com o Markdown que o Product Owner já sabe interpretar) e 10 campos de profundidade (seção 5.1 do `WHITEPAPER.md`). `PrioritizedRequirement` fica deliberadamente fora de `PRDDraft` — nunca altera o contrato de handoff byte-idêntico ao Product Owner.
- **Fontes de conhecimento** — `knowledge/methodology/` (JTBD, North Star Framework), consumidas diretamente pelos prompts das skills (sem RAG nesta fase — volume pequeno o suficiente para caber direto no contexto, ver `context_engineering.md`).
- **Integrações externas** — `services/jira_service.py` e `services/confluence_service.py` (Jira Cloud e Confluence Cloud REST API, mesmas credenciais). Jira é somente leitura (escrita/criação de tickets continua exclusiva do AQuA-QE Product Owner). Confluence tem duas operações de escrita — `create_page`/`create_confluence_page` (página nova) e `update_page`/`update_confluence_page` (página existente, mantendo título e incrementando versão) — ambas disponíveis para PRD, Visão e Estratégia.
- **Interfaces externas** — entrada: arquivo `.txt`/Markdown, texto de chat, ticket Jira Cloud ou página Confluence Cloud; saída: arquivo Markdown exportado (`export_markdown`/`format_prd_markdown`/formatadores de visão/estratégia), consumido pelo AQuA-QE Product Owner como entrada normal (só o PRD), e/ou uma página nova ou atualizada no Confluence Cloud (`create_confluence_page`/`update_confluence_page`, opcional, sempre após aceite humano do artefato).

## Fluxo de dados

1. A entrada é normalizada em texto (`read_text_file` para arquivo; `parse_chat_transcript`/`format_chat_transcript` para chat; `read_jira_issue`/`read_confluence_page` para Jira/Confluence — apenas leitura, este agente nunca escreve de volta nesses sistemas).
2. Descoberta é sintetizada quando o texto contiver informação suficiente (`identify_problem_statement`, `synthesize_personas`, `extract_jobs_to_be_done`, `extract_market_context`) — cada uma pode retornar vazia sem bloquear o restante do pipeline.
3. Visão de produto é gerada, validada, revisada e (se necessário) refinada com respostas do usuário, até aceite humano explícito.
4. Estratégia de produto é gerada a partir da visão aceita, mesmo ciclo.
5. PRD é gerado incorporando descoberta/visão/estratégia (quando existirem na mesma sessão) ou só a partir da ideia crua (quando não existirem), em seguida enriquecido com personas/jornadas/objetivos com KPI/casos de uso/dependências/premissas técnicas/restrições/glossário/métricas candidatas/MVP-versão futura — mesmo ciclo de validação/revisão/refinamento/aceite; o enriquecimento é re-derivado após qualquer refinamento, para não ficar obsoleto.
6. O PRD (e, nos modos isolados, Visão/Estratégia) aceito é formatado e exportado (`export_markdown`) e, opcionalmente, publicado como página nova (`create_confluence_page`, `--publicar-confluence`) ou usado para atualizar uma página já existente (`update_confluence_page`, `--atualizar-confluence`) no Confluence Cloud — sempre sob uma segunda confirmação humana explícita, distinta do aceite do artefato, e nunca os dois ao mesmo tempo.
7. Opcionalmente, só para PRD, os requisitos funcionais são priorizados (`--priorizar moscow/rice/wsjf`) — MoSCoW classifica automaticamente a partir de sinais de linguagem do próprio PRD; RICE/WSJF pedem os números interativamente ao usuário (nunca estimados pelo agente, GR-M4) e calculam o score em Python puro. Sempre exportado num arquivo separado do PRD (`--saida-priorizacao`).
8. A aprovação final de cada artefato é sempre um passo humano, fora da responsabilidade do agente.

## Modos de operação

- **Descoberta** — sintetiza problem statement/personas/JTBD/mercado, sem ciclo de aceite formal (são inputs estruturados, não artefatos "aceitos" isoladamente).
- **Visão** — gera e refina a visão de produto até aceite humano. Aceita `--publicar-confluence`/`--atualizar-confluence`.
- **Estratégia** — gera e refina a estratégia de produto a partir da visão aceita. Aceita `--publicar-confluence`/`--atualizar-confluence`.
- **PRD** — gera e refina o PRD, o artefato terminal desta fase, pronto para o handoff ao AQuA-QE Product Owner. Com `--prd-existente`, carrega um PRD `.md` já pronto (`parse_prd_markdown`) em vez de gerar um novo, e aplica o mesmo ciclo de validação/revisão/refinamento a partir dele. Aceita `--publicar-confluence`/`--atualizar-confluence` e `--priorizar moscow/rice/wsjf`.
- **Completo** — encadeia os quatro modos acima numa execução só, com aceite humano em cada etapa. Também aceita `--publicar-confluence`/`--atualizar-confluence`, aplicado à etapa final de PRD.

## Restrições técnicas

- Mesmos modelos de LLM do AQuA-QE Product Owner (`mistral` gerador, `phi4` revisor), via Ollama local — reaproveitamento deliberado, sem introduzir um terceiro provedor sem necessidade comprovada.
- Sem RAG/embeddings nesta fase — `knowledge/methodology/` é pequeno o suficiente para caber direto no prompt; `retrieve_chunks` fica para uma fase futura, se o volume de conhecimento crescer (mesma decisão de "não construir antecipadamente sem consumidor" já aplicada no Product Owner).

## Observabilidade

- Cada execução deve registrar: fonte de entrada, descoberta sintetizada, decisões de visão/estratégia/PRD, resultado do checklist automático em cada etapa e se houve interrupção por ambiguidade ou por falta de dado de mercado/financeiro — necessário para auditar rastreabilidade (ver `guardrails.md`) e para os casos de teste de `evaluation.md`.
