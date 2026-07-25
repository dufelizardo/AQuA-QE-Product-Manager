# Skills

> Documentação das skills implementadas em `../../src/aqua_qe_product_manager/skills/`, no formato definido em `../standards/skill_standard.md`. Ordem conforme `agent_manifest.yaml`.
>
> `identify_problem_statement`, `synthesize_personas`, `extract_jobs_to_be_done`, `extract_market_context`, `generate_product_vision`, `generate_vision_clarifying_questions`, `refine_product_vision`, `generate_product_strategy`, `generate_strategy_clarifying_questions`, `refine_product_strategy`, `generate_prd`, `generate_prd_clarifying_questions` e `refine_prd` usam um LLM local via Ollama (`../../src/aqua_qe_product_manager/services/llm_service.py`, modelo configurável por `OLLAMA_MODEL`, padrão `mistral`). `validate_product_vision`, `validate_product_strategy`, `validate_prd` e `format_prd_markdown` são Python puro, sem LLM. `review_product_vision`, `review_product_strategy` e `review_prd` usam um segundo LLM, diferente do gerador (`OLLAMA_REVIEW_MODEL`, padrão `phi4`), como revisor independente (LLM-como-juiz). `read_text_file`, `read_jira_issue`, `read_confluence_page`, `parse_chat_transcript`, `format_chat_transcript` e `export_markdown` são Python puro, de I/O/formatação (`read_jira_issue`/`read_confluence_page` fazem chamada HTTP real ao Jira/Confluence Cloud via `services/jira_service.py`/`services/confluence_service.py`, não ao LLM).

## read_text_file

- **Descrição**: lê um arquivo de texto (`.txt`/`.md`) do disco e retorna seu conteúdo como string.
- **Entrada**: `caminho: str`.
- **Saída**: `str`.
- **Efeitos colaterais**: leitura de arquivo em disco.
- **Erros esperados**: arquivo inexistente ou sem permissão de leitura.
- **Dependências**: nenhuma.

## read_jira_issue

- **Descrição**: busca um ticket do Jira Cloud (resumo + descrição) e retorna como texto simples, convertendo do Atlassian Document Format (ADF). Apenas leitura — este agente nunca escreve de volta no Jira (isso é responsabilidade exclusiva do AQuA-QE Product Owner).
- **Entrada**: `issue_key: str` (ex.: `"PROJ-123"`).
- **Saída**: `str`.
- **Efeitos colaterais**: chamada HTTP `GET` ao Jira Cloud (`JIRA_BASE_URL`, autenticação Basic com `JIRA_EMAIL`/`JIRA_API_TOKEN`).
- **Erros esperados**: credencial ausente (`KeyError` em `os.environ`), ticket inexistente ou sem permissão (HTTP 4xx, propagado via `raise_for_status`).
- **Dependências**: nenhuma.

## read_confluence_page

- **Descrição**: busca uma página do Confluence Cloud (aceita a URL completa ou apenas o ID) e retorna título + corpo como texto simples, convertendo do storage format (XHTML). Apenas leitura — publicar/atualizar página no Confluence não está no escopo desta fase.
- **Entrada**: `pagina: str` (URL completa ou ID).
- **Saída**: `str`.
- **Efeitos colaterais**: chamada HTTP `GET` ao Confluence Cloud (mesmas credenciais do Jira: `JIRA_BASE_URL`/`JIRA_EMAIL`/`JIRA_API_TOKEN`).
- **Erros esperados**: credencial ausente, página inexistente ou sem permissão (HTTP 4xx, propagado via `raise_for_status`).
- **Dependências**: nenhuma.

## parse_chat_transcript

- **Descrição**: separa uma transcrição de chat em mensagens por remetente (ex.: "PM: ...", "Stakeholder: ..."). Puro Python (regex), sem LLM. Texto sem remetentes identificáveis volta inalterado como uma única mensagem.
- **Entrada**: `texto: str`.
- **Saída**: `list[ChatMessage]`.
- **Efeitos colaterais**: nenhum.
- **Erros esperados**: nenhum — sempre retorna ao menos uma mensagem (fallback seguro).
- **Dependências**: nenhuma.

## format_chat_transcript

- **Descrição**: reconstrói uma transcrição normalizada ("Remetente: mensagem" por parágrafo) a partir das mensagens. Texto sem remetente identificável retorna inalterado.
- **Entrada**: `mensagens: list[ChatMessage]`.
- **Saída**: `str`.
- **Efeitos colaterais**: nenhum.
- **Erros esperados**: nenhum.
- **Dependências**: consome a saída de `parse_chat_transcript`.

## identify_problem_statement

- **Descrição**: sintetiza um problem statement (problema, usuários afetados, impacto, evidência) a partir do texto de entrada. Nunca inventa evidência não citada.
- **Entrada**: `texto: str`.
- **Saída**: `ProblemStatement` (campos vazios quando não identificáveis).
- **Efeitos colaterais**: chamada ao LLM local (`llm_service`).
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: nenhuma.

## synthesize_personas

- **Descrição**: sintetiza personas (nome, descrição, objetivos, pontos de dor) a partir do texto de entrada. Nunca inventa uma persona não sustentada pelo texto.
- **Entrada**: `texto: str`.
- **Saída**: `list[Persona]`.
- **Efeitos colaterais**: chamada ao LLM local.
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: nenhuma.

## extract_jobs_to_be_done

- **Descrição**: extrai jobs-to-be-done (situação/motivação/resultado esperado) a partir do texto de entrada, conforme `../../knowledge/methodology/jtbd.md`.
- **Entrada**: `texto: str`.
- **Saída**: `list[JobToBeDone]`.
- **Efeitos colaterais**: chamada ao LLM local.
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: nenhuma.

## extract_market_context

- **Descrição**: estrutura contexto de mercado (concorrentes, tendências) **exclusivamente** a partir do texto de entrada — nunca do conhecimento geral do modelo sobre o mercado (GR-M1/RULE-M1, o guardrail mais crítico deste agente). Retorna listas vazias, não concorrentes inventados, quando o texto não citar nenhum.
- **Entrada**: `texto: str`.
- **Saída**: `MarketAnalysis`.
- **Efeitos colaterais**: chamada ao LLM local.
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: nenhuma.

## generate_product_vision

- **Descrição**: gera a visão de produto (statement, público-alvo, diferenciais, métrica norte) a partir de uma ideia e, opcionalmente, do contexto de descoberta já sintetizado.
- **Entrada**: `ideia: str`, `contexto: dict` (pode incluir `problem_statement`, `personas`, `market_analysis`).
- **Saída**: `ProductVision`.
- **Efeitos colaterais**: chamada ao LLM local.
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: consome, quando disponível, a saída de `identify_problem_statement`/`synthesize_personas`/`extract_market_context`.

## validate_product_vision

- **Descrição**: valida se a visão tem `statement` e `target_audience` preenchidos (checklist automático, equivalente a `validate_story`/`validate_prd` no Product Owner).
- **Entrada**: `vision: ProductVision`.
- **Saída**: `bool`.
- **Efeitos colaterais**: nenhum — Python puro, sem LLM.
- **Erros esperados**: nenhum.
- **Dependências**: consome a saída de `generate_product_vision`.

## review_product_vision

- **Descrição**: revisa a visão com um segundo LLM, diferente do gerador, avaliando clareza e coerência.
- **Entrada**: `vision: ProductVision`.
- **Saída**: `dict` no formato `{"aprovado": bool, "problemas": list[str]}`.
- **Efeitos colaterais**: chamada ao LLM local de revisão (`OLLAMA_REVIEW_MODEL`, padrão `phi4`).
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: consome a saída de `generate_product_vision`, após `validate_product_vision` aprovar.

## generate_vision_clarifying_questions

- **Descrição**: gera perguntas de esclarecimento a partir dos apontamentos da revisão da visão. Retorna lista vazia se `vision.review_notes` estiver vazio.
- **Entrada**: `vision: ProductVision`.
- **Saída**: `list[str]`.
- **Efeitos colaterais**: chamada ao LLM local.
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: consome `vision.review_notes`, produzido por `review_product_vision`.

## refine_product_vision

- **Descrição**: reescreve a visão usando as respostas do usuário às perguntas de esclarecimento.
- **Entrada**: `vision: ProductVision`, `respostas: list[dict]` (cada item com `pergunta`/`resposta`).
- **Saída**: `ProductVision`.
- **Efeitos colaterais**: chamada ao LLM local.
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: chamada pelo ciclo de refinamento do CLI, reaplicando `validate_product_vision`/`review_product_vision` em seguida.

## generate_product_strategy

- **Descrição**: gera a estratégia de produto (metas, temas de roadmap, horizonte de tempo) a partir da visão já aceita.
- **Entrada**: `vision: ProductVision`, `contexto: dict`.
- **Saída**: `ProductStrategy`.
- **Efeitos colaterais**: chamada ao LLM local.
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: consome uma `ProductVision` com `status == accepted`.

## validate_product_strategy

- **Descrição**: valida se a estratégia tem ao menos uma meta com descrição e métrica preenchidas.
- **Entrada**: `strategy: ProductStrategy`.
- **Saída**: `bool`.
- **Efeitos colaterais**: nenhum — Python puro.
- **Erros esperados**: nenhum.
- **Dependências**: consome a saída de `generate_product_strategy`.

## review_product_strategy

- **Descrição**: revisa a estratégia com o segundo LLM, avaliando coerência com a visão aceita.
- **Entrada**: `strategy: ProductStrategy`.
- **Saída**: `dict` no formato `{"aprovado": bool, "problemas": list[str]}`.
- **Efeitos colaterais**: chamada ao LLM local de revisão.
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: consome a saída de `generate_product_strategy`, após `validate_product_strategy` aprovar.

## generate_strategy_clarifying_questions

- **Descrição**: gera perguntas de esclarecimento a partir dos apontamentos da revisão da estratégia.
- **Entrada**: `strategy: ProductStrategy`.
- **Saída**: `list[str]`.
- **Efeitos colaterais**: chamada ao LLM local.
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: consome `strategy.review_notes`.

## refine_product_strategy

- **Descrição**: reescreve a estratégia usando as respostas do usuário.
- **Entrada**: `strategy: ProductStrategy`, `respostas: list[dict]`.
- **Saída**: `ProductStrategy`.
- **Efeitos colaterais**: chamada ao LLM local.
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: chamada pelo ciclo de refinamento do CLI.

## generate_prd

- **Descrição**: gera um PRD completo a partir de uma ideia crua e, opcionalmente, de um `contexto` agregando descoberta/visão/estratégia já aceitas. Sem `contexto`, comporta-se como a geração de PRD equivalente no AQuA-QE Product Owner (ideia → PRD).
- **Entrada**: `ideia: str`, `contexto: dict | None`.
- **Saída**: `PRDDraft`.
- **Efeitos colaterais**: chamada ao LLM local.
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: consome, quando disponíveis, `ProblemStatement`/`list[Persona]`/`MarketAnalysis`/`ProductVision`/`ProductStrategy` já aceitos na mesma sessão.

## validate_prd

- **Descrição**: valida se o PRD tem contexto/objetivo/escopo preenchidos e ao menos um requisito funcional e um critério de sucesso (checklist automático, mesmo padrão do Product Owner).
- **Entrada**: `draft: PRDDraft`.
- **Saída**: `bool`.
- **Efeitos colaterais**: nenhum — Python puro.
- **Erros esperados**: nenhum.
- **Dependências**: consome a saída de `generate_prd`.

## review_prd

- **Descrição**: revisa o PRD com o segundo LLM, avaliando clareza, completude e coerência com descoberta/visão/estratégia quando existirem.
- **Entrada**: `draft: PRDDraft`.
- **Saída**: `dict` no formato `{"aprovado": bool, "problemas": list[str]}`.
- **Efeitos colaterais**: chamada ao LLM local de revisão.
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: consome a saída de `generate_prd`, após `validate_prd` aprovar.

## generate_prd_clarifying_questions

- **Descrição**: gera perguntas de esclarecimento a partir dos apontamentos da revisão do PRD.
- **Entrada**: `draft: PRDDraft`.
- **Saída**: `list[str]`.
- **Efeitos colaterais**: chamada ao LLM local.
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: consome `draft.review_notes`.

## refine_prd

- **Descrição**: reescreve os campos do PRD usando as respostas às perguntas de esclarecimento. Normaliza campos que o LLM às vezes devolve como lista em vez de string (mesmo fix aplicado no AQuA-QE Product Owner após um bug real).
- **Entrada**: `draft: PRDDraft`, `respostas: list[dict]`.
- **Saída**: `PRDDraft`.
- **Efeitos colaterais**: chamada ao LLM local.
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: chamada pelo ciclo de refinamento do CLI.

## format_prd_markdown

- **Descrição**: formata o PRD em Markdown, mesma estrutura de `../standards/prd_standard.md` — o texto resultante é diretamente consumível pelo AQuA-QE Product Owner (`--modo lote --arquivo`).
- **Entrada**: `draft: PRDDraft`.
- **Saída**: `str`.
- **Efeitos colaterais**: nenhum — Python puro.
- **Erros esperados**: nenhum.
- **Dependências**: consome um `PRDDraft` com `status == accepted`.

## export_markdown

- **Descrição**: exporta um texto Markdown (PRD, visão ou estratégia formatados) para o caminho informado.
- **Entrada**: `texto: str`, `caminho: str`.
- **Saída**: `None`.
- **Efeitos colaterais**: escrita de arquivo em disco.
- **Erros esperados**: caminho inválido ou sem permissão de escrita.
- **Dependências**: consome a saída de `format_prd_markdown` ou de formatadores equivalentes de visão/estratégia.
