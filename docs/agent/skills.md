# Skills

> Documentação das skills implementadas em `../../src/aqua_qe_product_manager/skills/`, no formato definido em `../standards/skill_standard.md`. Ordem conforme `agent_manifest.yaml`.
>
> `identify_problem_statement`, `synthesize_personas`, `extract_jobs_to_be_done`, `extract_market_context`, `generate_product_vision`, `generate_vision_clarifying_questions`, `refine_product_vision`, `generate_product_strategy`, `generate_strategy_clarifying_questions`, `refine_product_strategy`, `generate_prd`, `generate_prd_clarifying_questions`, `refine_prd`, `identify_user_journeys`, `identify_business_objectives`, `identify_use_cases`, `identify_external_dependencies`, `identify_technical_assumptions`, `identify_constraints`, `identify_prd_glossary`, `identify_candidate_product_metrics` e `identify_mvp_scope` usam um LLM local via Ollama (`../../src/aqua_qe_product_manager/services/llm_service.py`, modelo configurável por `OLLAMA_MODEL`, padrão `mistral`). `validate_product_vision`, `validate_product_strategy`, `validate_prd`, `format_prd_markdown` e `parse_prd_markdown` são Python puro, sem LLM. `review_product_vision`, `review_product_strategy` e `review_prd` usam um segundo LLM, diferente do gerador (`OLLAMA_REVIEW_MODEL`, padrão `phi4`), como revisor independente (LLM-como-juiz). `read_text_file`, `read_jira_issue`, `read_confluence_page`, `parse_chat_transcript`, `format_chat_transcript` e `export_markdown` são Python puro, de I/O/formatação (`read_jira_issue`/`read_confluence_page` fazem chamada HTTP real ao Jira/Confluence Cloud via `services/jira_service.py`/`services/confluence_service.py`, não ao LLM). `create_confluence_page`/`update_confluence_page` também são I/O (chamada HTTP de escrita ao Confluence Cloud), sem LLM — as únicas skills deste agente que gravam em um sistema externo, e só são chamadas pelo CLI após aceitação humana explícita. `classify_moscow` usa o LLM gerador (categórica, segue GR-1). `validate_moscow_classification`, `compute_rice_score` e `compute_wsjf_score` são Python puro, sem LLM — os dois últimos nunca recebem um número estimado pelo agente (GR-M4).

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

## Re-derivação seletiva no ciclo de refinamento

Depois de `refine_prd` reescrever os 9 campos centrais, `workflow/generate_prd.py::refine_prd_draft` decide, campo de profundidade por campo de profundidade, se vale a pena re-rodar a skill correspondente — comparando quais campos centrais mudaram (diff antes/depois de `refine_prd`) contra o mapa `_DEPENDENCIAS_PROFUNDIDADE` abaixo. Isso é diferente do campo "Dependências" de cada skill acima (que documenta dependência de *dado de entrada*): aqui o assunto é *gatilho de re-execução* — quando um campo central listado abaixo muda, a skill é re-executada; quando não, o valor já existente no draft é preservado como estava.

O mapa é **heurístico** na maioria das linhas (a skill recebe o texto inteiro do PRD, não um campo isolado — não há como provar que o resultado mudaria só olhando o campo). Rótulos:
- **exata**: a skill literalmente só recebe esse(s) campo(s) como argumento, sem o texto completo do PRD.
- **semi-explícita**: o próprio prompt/system message da skill cita esse(s) campo(s) nominalmente.
- **heurística**: julgamento de produto, deliberadamente enviesado para incluir mais campos do que o estritamente necessário nas entradas de menor confiança — a regra de desempate é sempre "na dúvida, re-executa", nunca pular por engano.

| Campo de profundidade (skill) | Depende de (campos centrais) | Confiança |
|---|---|---|
| `personas` (`synthesize_personas`) | `context_problem`, `target_audience`, `scope` | heurística |
| `user_journeys` (`identify_user_journeys`) | `scope`, `functional_requirements` | semi-explícita |
| `business_objectives` (`identify_business_objectives`) | `objective`, `success_criteria` | exata |
| `use_cases` (`identify_use_cases`) | `scope`, `functional_requirements` | semi-explícita |
| `dependencies` (`identify_external_dependencies`) | `functional_requirements`, `non_functional_requirements` | heurística |
| `technical_assumptions` (`identify_technical_assumptions`) | `non_functional_requirements`, `risks_assumptions` | heurística |
| `constraints` (`identify_constraints`) | `non_functional_requirements`, `risks_assumptions`, `out_of_scope` | heurística |
| `glossary` (`identify_prd_glossary`) | `context_problem`, `scope`, `functional_requirements`, `non_functional_requirements` | heurística (baixa confiança, deliberadamente ampla) |
| `candidate_product_metrics` (`identify_candidate_product_metrics`) | `context_problem`, `objective`, `target_audience` | heurística |
| `mvp_scope`/`future_scope` (`identify_mvp_scope`) | `functional_requirements` (exata) + `scope`, `out_of_scope` (heurística) | mista |

Na **geração inicial** (`generate_prd_draft`), não há um "antes" para comparar — as 10 skills sempre rodam, sem exceção. `refine_prd_draft(..., forcar_rederivacao_completa=True)` ignora o mapa inteiro e força a re-derivação completa, como válvula de escape se o mapa heurístico errar em algum caso real. Ver issue [#10](https://github.com/dufelizardo/AQuA-QE-Product-Manager/issues/10).

## identify_user_journeys

- **Descrição**: identifica jornadas do usuário (passo a passo de um fluxo relevante, ex.: agendamento) sustentadas pelo texto de entrada. Nunca inventa um passo que não decorra do escopo/requisitos descritos.
- **Entrada**: `texto: str`.
- **Saída**: `list[UserJourney]`.
- **Efeitos colaterais**: chamada ao LLM local.
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: nenhuma.

## identify_business_objectives

- **Descrição**: reestrutura `objective`/`success_criteria` já aceitos em pares objetivo-de-negócio → KPI explícitos. Nunca inventa uma meta numérica que não decorra deles.
- **Entrada**: `objetivo: str`, `criterios_sucesso: list[str]`.
- **Saída**: `list[BusinessObjective]`.
- **Efeitos colaterais**: chamada ao LLM local.
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: consome `objective`/`success_criteria` de um `PRDDraft` já gerado.

## identify_use_cases

- **Descrição**: identifica casos de uso de alto nível (ator + ação, ex.: "Paciente agenda consulta") sustentados pelo escopo/requisitos descritos.
- **Entrada**: `texto: str`.
- **Saída**: `list[str]`.
- **Efeitos colaterais**: chamada ao LLM local.
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: nenhuma.

## identify_external_dependencies

- **Descrição**: identifica dependências de sistemas externos (ex.: sistemas governamentais, autenticação, notificação) citadas ou claramente inferíveis no texto. Nome distinto do `identify_dependencies` do AQuA-QE Product Owner, que trata de um conceito diferente (dependência requisito-a-requisito, não sistema externo).
- **Entrada**: `texto: str`.
- **Saída**: `list[str]`.
- **Efeitos colaterais**: chamada ao LLM local.
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: nenhuma.

## identify_technical_assumptions

- **Descrição**: identifica premissas técnicas (ex.: infraestrutura disponível, equipamento existente) citadas ou implícitas no texto.
- **Entrada**: `texto: str`.
- **Saída**: `list[str]`.
- **Efeitos colaterais**: chamada ao LLM local.
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: nenhuma.

## identify_constraints

- **Descrição**: identifica restrições do projeto (ex.: orçamento, prazo, legislação) citadas ou implícitas no texto.
- **Entrada**: `texto: str`.
- **Saída**: `list[str]`.
- **Efeitos colaterais**: chamada ao LLM local.
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: nenhuma.

## identify_prd_glossary

- **Descrição**: identifica termos de domínio específicos deste PRD (ex.: "Unidade", "Paciente") — distinto do glossário conceitual da plataforma (`knowledge/glossary/glossario.md`).
- **Entrada**: `texto: str`.
- **Saída**: `list[GlossaryTerm]`.
- **Efeitos colaterais**: chamada ao LLM local.
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: nenhuma.

## identify_candidate_product_metrics

- **Descrição**: sugere métricas de produto típicas do domínio descrito (ex.: MAU, DAU, taxa de abandono) — sempre como recomendação a confirmar, nunca como fato (GR-M5/RULE-M5). Único ponto do agente onde conhecimento geral do modelo é intencionalmente permitido, precisamente porque a saída nunca é apresentada como evidenciada.
- **Entrada**: `texto: str`.
- **Saída**: `list[str]`.
- **Efeitos colaterais**: chamada ao LLM local.
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: nenhuma.

## identify_mvp_scope

- **Descrição**: agrupa os requisitos funcionais já existentes em MVP vs. versão futura, com base em sinal de linguagem explícito no texto de origem — mecanismo mais leve e distinto do `--priorizar` (MoSCoW/RICE/WSJF), que classifica individualmente e exporta em arquivo separado.
- **Entrada**: `requisitos_funcionais: list[str]`, `texto: str`.
- **Saída**: `tuple[list[str], list[str]]` (mvp, versão futura).
- **Efeitos colaterais**: chamada ao LLM local.
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: consome `functional_requirements` de um `PRDDraft` já gerado.

## format_prd_markdown

- **Descrição**: formata o PRD em Markdown, mesma estrutura de `../standards/prd_standard.md` — o texto resultante é diretamente consumível pelo AQuA-QE Product Owner (`--modo lote --arquivo`). As seções de profundidade (personas, jornadas, objetivos com KPI, casos de uso, MVP/versão futura, dependências, premissas técnicas, restrições, glossário, métricas candidatas) são adições — as 9 seções originais mantêm texto/ordem. Requisitos funcionais/não funcionais são numerados (`RF-001`/`RNF-001`) só na exportação.
- **Entrada**: `draft: PRDDraft`.
- **Saída**: `str`.
- **Efeitos colaterais**: nenhum — Python puro.
- **Erros esperados**: nenhum.
- **Dependências**: consome um `PRDDraft` com `status == accepted`.

## parse_prd_markdown

- **Descrição**: inverso de `format_prd_markdown` — reconstrói um `PRDDraft` a partir de um Markdown já existente (mesma estrutura de seções), preservando a redação original campo a campo. Usado por `--modo prd --prd-existente` para carregar um PRD pronto e refiná-lo de verdade, em vez de o LLM reescrever tudo do zero a partir do texto. Seção ausente ou não reconhecida fica com o default vazio do dataclass — nunca lança exceção, nunca inventa conteúdo. Remove o prefixo `RF-XXX:`/`RNF-XXX:` ao reconstruir requisitos funcionais/não funcionais (a numeração é só de exportação). **Limitação conhecida**: as seções de profundidade adicionadas nesta leva (personas, jornadas, objetivos com KPI, casos de uso, dependências, premissas técnicas, restrições, glossário, métricas candidatas, MVP/versão futura) ainda não têm mapeamento em `_SECAO_PARA_CAMPO` — ao recarregar um PRD existente, essas seções voltam vazias/default, mesmo que o Markdown as contenha. Round-trip completo delas fica para um incremento futuro.
- **Entrada**: `texto: str`.
- **Saída**: `PRDDraft` (com `status` no default `pending_clarification` — ainda não validado/revisado nesta sessão).
- **Efeitos colaterais**: nenhum — Python puro, determinístico.
- **Erros esperados**: nenhum.
- **Dependências**: espelha exatamente o formato produzido por `format_prd_markdown` — mudança de estrutura em uma exige atualizar a outra.

## create_confluence_page

- **Descrição**: publica um texto Markdown já formatado (PRD, visão ou estratégia aceitos) como página **nova** no Confluence Cloud e retorna a URL da página criada. Recebe o texto pronto — quem formata (`format_prd_markdown`/`_formatar_visao_markdown`/`_formatar_estrategia_markdown`) é o chamador (`run.py`), não a skill; isso permite reaproveitá-la para os três artefatos sem triplicar código. Converte o Markdown para o storage format (XHTML) do Confluence internamente (`services/confluence_service.py`).
- **Entrada**: `texto: str`, `titulo: str`.
- **Saída**: `str` (URL da página criada).
- **Efeitos colaterais**: chamada HTTP `POST` ao Confluence Cloud (`CONFLUENCE_SPACE_KEY`, mesmas credenciais do Jira).
- **Erros esperados**: credencial ausente (`KeyError` em `os.environ`), espaço inexistente ou sem permissão (HTTP 4xx, propagado via `raise_for_status`).
- **Dependências**: chamada pelo CLI (`run.py --publicar-confluence`) só após aceitação humana explícita do artefato — nunca automaticamente.

## update_confluence_page

- **Descrição**: atualiza uma página **já existente** no Confluence Cloud (aceita a URL completa ou apenas o ID, mesma ergonomia de `read_confluence_page`) a partir de um texto Markdown já formatado, mantendo título e id — incrementa a versão da página automaticamente. Diferente do AQuA-QE Product Owner (que tem a skill equivalente, mas nunca a conectou a nenhum comando do seu CLI), aqui `--modo prd/completo/visao/estrategia --atualizar-confluence <id ou URL>` é um consumidor real.
- **Entrada**: `pagina: str` (URL completa ou ID), `texto: str`.
- **Saída**: `None`.
- **Efeitos colaterais**: uma chamada HTTP `GET` (busca título/versão atuais) seguida de `PUT` ao Confluence Cloud.
- **Erros esperados**: credencial ausente, página inexistente ou sem permissão (HTTP 4xx, propagado via `raise_for_status`).
- **Dependências**: chamada pelo CLI (`run.py --atualizar-confluence`) só após aceitação humana explícita do artefato — mutuamente exclusivo com `--publicar-confluence` na mesma execução.

### Bug conhecido: `_texto_para_storage` não cobre toda a sintaxe que `format_prd_markdown` passou a gerar

`_texto_para_storage` (`services/confluence_service.py`) é um conversor Markdown→XHTML minimalista, escrito só para o que o PRD original precisava: `#`/`##`/`###` (headings) e `- ` (listas simples). O enriquecimento do PRD (personas, jornadas, objetivos com KPI, glossário) passou a gerar construções que esse conversor nunca soube tratar, confirmado numa publicação real (`--atualizar-confluence` contra `.../pages/1179649/PRD+-+Mais+Sa+de+P+blica`):

- **Tabela Markdown** (seção "Objetivos de Negócio (KPI)", `| Objetivo | KPI |`/`|---|---|`) — vira parágrafos com os caracteres `|` literais, nunca uma tabela real do Confluence.
- **Negrito Markdown** (seção "Glossário", `**termo**: definição`) — vira asteriscos literais (`**PRD**: ...`), nunca `<strong>`.
- **Lista numerada** (seção "Jornadas do Usuário", `1. passo`/`2. passo`) — cada linha vira um `<p>` solto, perdendo a estrutura de lista ordenada.
- **Lista aninhada dentro de um item** (seção "Personas", `- Objetivos: {lista}`, quando a persona tem mais de um objetivo/ponto de dor) — os itens da sub-lista viram bullets soltos no mesmo nível de "Objetivos"/"Pontos de dor", perdendo a associação com o campo pai. Causa raiz em `_personas_md` (`format_prd_markdown.py`): embutir uma lista já formatada (`_lista_md`) dentro de um único item de outra lista não produz Markdown aninhado válido.

Nenhum desses quatro é um erro de dado (GR-1 continua intacto — o conteúdo é rastreável à fonte) — é puramente a camada de conversão para Confluence não ter acompanhado a riqueza nova do PRD. `_texto_para_storage` é a mesma função portada para o AQuA-QE Solution Architect; o mesmo problema é esperado lá para qualquer seção que use tabela/negrito/lista numerada/lista aninhada.

## classify_moscow

- **Descrição**: classifica cada requisito funcional do PRD aceito em MoSCoW (Must/Should/Could/Won't), com base exclusivamente em sinais de linguagem explícitos no texto de origem (ex.: "essencial" → must, "seria bom ter" → could). Nunca inventa uma categoria sem sinal claro — nesse caso, a categoria fica vazia (GR-M4/RULE-M3 tratam especificamente do risco numérico de RICE/WSJF; esta skill segue GR-1 normalmente, por ser categórica).
- **Entrada**: `requisitos: list[str]`, `texto_fonte: str` (o PRD formatado completo).
- **Saída**: `list[PrioritizedRequirement]`.
- **Efeitos colaterais**: chamada ao LLM local.
- **Erros esperados**: resposta do LLM não é JSON válido (`ValueError`).
- **Dependências**: consome `draft.functional_requirements` de um PRD já aceito.

## validate_moscow_classification

- **Descrição**: confere que a classificação devolvida corresponde 1:1 aos requisitos originais (mesmo texto, mesma ordem) e que toda categoria é uma das 4 válidas ou vazia. Se falhar, `workflow/prioritize_requirements.py` aplica o fallback seguro (todas as categorias vazias) em vez de propagar uma classificação inconsistente.
- **Entrada**: `itens: list[PrioritizedRequirement]`, `requisitos_originais: list[str]`.
- **Saída**: `bool`.
- **Efeitos colaterais**: nenhum — Python puro, sem LLM.
- **Erros esperados**: nenhum.
- **Dependências**: consome a saída de `classify_moscow`.

## compute_rice_score

- **Descrição**: calcula o score RICE = (Reach × Impact × Confidence) / Effort. Puro Python — os quatro valores vêm sempre do usuário via `input()` no CLI, nunca estimados pelo agente (GR-M4).
- **Entrada**: `reach: float`, `impact: float`, `confidence: float`, `effort: float`.
- **Saída**: `float`.
- **Efeitos colaterais**: nenhum.
- **Erros esperados**: `ZeroDivisionError` se `effort` for zero (propagado, não capturado — o CLI já pede um número válido antes de chamar).
- **Dependências**: chamada pelo CLI (`run.py --priorizar rice`) após coleta interativa dos valores.

## compute_wsjf_score

- **Descrição**: calcula o score WSJF = (Business Value + Time Criticality + Risk Reduction) / Job Size. Puro Python — os quatro valores vêm sempre do usuário via `input()` no CLI, nunca estimados pelo agente (GR-M4).
- **Entrada**: `business_value: float`, `time_criticality: float`, `risk_reduction: float`, `job_size: float`.
- **Saída**: `float`.
- **Efeitos colaterais**: nenhum.
- **Erros esperados**: `ZeroDivisionError` se `job_size` for zero (propagado, não capturado).
- **Dependências**: chamada pelo CLI (`run.py --priorizar wsjf`) após coleta interativa dos valores.

## export_markdown

- **Descrição**: exporta um texto Markdown (PRD, visão ou estratégia formatados) para o caminho informado.
- **Entrada**: `texto: str`, `caminho: str`.
- **Saída**: `None`.
- **Efeitos colaterais**: escrita de arquivo em disco.
- **Erros esperados**: caminho inválido ou sem permissão de escrita.
- **Dependências**: consome a saída de `format_prd_markdown` ou de formatadores equivalentes de visão/estratégia.
