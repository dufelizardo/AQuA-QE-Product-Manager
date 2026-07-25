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
   → generate_prd (usa descoberta + visão + estratégia, quando existirem) → validate_prd → review_prd
      → [se reprovado] generate_prd_clarifying_questions → resposta humana → refine_prd → revalidar
      → aceite humano explícito
   → format_prd_markdown → export_markdown
   → [opcional] create_confluence_page (--publicar-confluence, após confirmação humana explícita)
   → (fora deste agente) AQuA-QE Product Owner consome o PRD via --modo lote --arquivo
```

Caminho alternativo, só para PRD (`--modo prd --prd-existente arquivo.md`): `parse_prd_markdown` substitui `generate_prd` — carrega um PRD já pronto como `PRDDraft`, preservando a redação original campo a campo, e segue direto para `validate_prd → review_prd → [refine] → aceite`, sem reescrita não solicitada pelo LLM.

## Componentes

- **Orquestrador/Agente** — decide a sequência de skills a chamar e quando interromper o fluxo por ambiguidade (ver `agent_design.md`). Implementado em `../../src/aqua_qe_product_manager/orchestrator/product_manager.py`.
- **Workflows** — orquestração da sequência de skills por artefato (descoberta, visão, estratégia, PRD), implementados em `../../src/aqua_qe_product_manager/workflow/`.
- **Skills** — funções descritas em `skills.md`, implementadas em `../../src/aqua_qe_product_manager/skills/`.
- **Modelos de dados** — estruturas (`ProblemStatement`, `Persona`, `JobToBeDone`, `MarketAnalysis`/`Competitor`, `ProductVision`, `ProductStrategy`/`StrategicGoal`, `PRDDraft`) implementadas em `../../src/aqua_qe_product_manager/models/`, conforme `output_schema.md`.
- **Fontes de conhecimento** — `knowledge/methodology/` (JTBD, North Star Framework), consumidas diretamente pelos prompts das skills (sem RAG nesta fase — volume pequeno o suficiente para caber direto no contexto, ver `context_engineering.md`).
- **Integrações externas** — `services/jira_service.py` e `services/confluence_service.py` (Jira Cloud e Confluence Cloud REST API, mesmas credenciais). Jira é somente leitura (escrita/criação de tickets continua exclusiva do AQuA-QE Product Owner). Confluence tem uma única operação de escrita — `create_page`/`create_confluence_page`, criar página nova — sem atualização de página existente (mesma decisão do Product Owner de não replicar código sem consumidor no CLI).
- **Interfaces externas** — entrada: arquivo `.txt`/Markdown, texto de chat, ticket Jira Cloud ou página Confluence Cloud; saída: arquivo Markdown exportado (`export_markdown`/`format_prd_markdown`), consumido pelo AQuA-QE Product Owner como entrada normal, e/ou uma página nova no Confluence Cloud (`create_confluence_page`, opcional, após aceite humano do PRD).

## Fluxo de dados

1. A entrada é normalizada em texto (`read_text_file` para arquivo; `parse_chat_transcript`/`format_chat_transcript` para chat; `read_jira_issue`/`read_confluence_page` para Jira/Confluence — apenas leitura, este agente nunca escreve de volta nesses sistemas).
2. Descoberta é sintetizada quando o texto contiver informação suficiente (`identify_problem_statement`, `synthesize_personas`, `extract_jobs_to_be_done`, `extract_market_context`) — cada uma pode retornar vazia sem bloquear o restante do pipeline.
3. Visão de produto é gerada, validada, revisada e (se necessário) refinada com respostas do usuário, até aceite humano explícito.
4. Estratégia de produto é gerada a partir da visão aceita, mesmo ciclo.
5. PRD é gerado incorporando descoberta/visão/estratégia (quando existirem na mesma sessão) ou só a partir da ideia crua (quando não existirem) — mesmo ciclo de validação/revisão/refinamento/aceite.
6. O PRD aceito é formatado (`format_prd_markdown`) e exportado (`export_markdown`) e, opcionalmente, publicado como página nova no Confluence Cloud (`create_confluence_page`, `--publicar-confluence`) — sempre sob uma segunda confirmação humana explícita, distinta do aceite do PRD.
7. A aprovação final de cada artefato é sempre um passo humano, fora da responsabilidade do agente.

## Modos de operação

- **Descoberta** — sintetiza problem statement/personas/JTBD/mercado, sem ciclo de aceite formal (são inputs estruturados, não artefatos "aceitos" isoladamente).
- **Visão** — gera e refina a visão de produto até aceite humano.
- **Estratégia** — gera e refina a estratégia de produto a partir da visão aceita.
- **PRD** — gera e refina o PRD, o artefato terminal desta fase, pronto para o handoff ao AQuA-QE Product Owner. Com `--prd-existente`, carrega um PRD `.md` já pronto (`parse_prd_markdown`) em vez de gerar um novo, e aplica o mesmo ciclo de validação/revisão/refinamento a partir dele. Com `--publicar-confluence`, após o aceite, oferece publicar o PRD como página nova no Confluence.
- **Completo** — encadeia os quatro modos acima numa execução só, com aceite humano em cada etapa. Também aceita `--publicar-confluence`, aplicado à etapa final de PRD.

## Restrições técnicas

- Mesmos modelos de LLM do AQuA-QE Product Owner (`mistral` gerador, `phi4` revisor), via Ollama local — reaproveitamento deliberado, sem introduzir um terceiro provedor sem necessidade comprovada.
- Sem RAG/embeddings nesta fase — `knowledge/methodology/` é pequeno o suficiente para caber direto no prompt; `retrieve_chunks` fica para uma fase futura, se o volume de conhecimento crescer (mesma decisão de "não construir antecipadamente sem consumidor" já aplicada no Product Owner).

## Observabilidade

- Cada execução deve registrar: fonte de entrada, descoberta sintetizada, decisões de visão/estratégia/PRD, resultado do checklist automático em cada etapa e se houve interrupção por ambiguidade ou por falta de dado de mercado/financeiro — necessário para auditar rastreabilidade (ver `guardrails.md`) e para os casos de teste de `evaluation.md`.
