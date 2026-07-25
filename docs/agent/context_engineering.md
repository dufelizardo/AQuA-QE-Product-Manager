# Context Engineering

> Estrutura conforme `../standards/context_engineering_standard.md`.

## Estratégia geral

Sem RAG nesta fase (ver `memory.md`) — o contexto de cada chamada ao LLM é montado diretamente, por concatenação, a partir de três fontes: o texto de entrada do usuário, o(s) artefato(s) já aceitos relevantes para aquela etapa (visão aceita ao gerar estratégia; descoberta+visão+estratégia ao gerar PRD) e, quando aplicável, o conteúdo relevante de `knowledge/methodology/`.

## Composição do prompt por skill

- **Skills de descoberta** (`identify_problem_statement`, `synthesize_personas`, `extract_jobs_to_be_done`, `extract_market_context`) — recebem apenas o texto de entrada bruto. Nenhum conhecimento prévio é injetado além da instrução de sistema (`_SYSTEM`), para não influenciar a extração com viés externo.
- **`generate_product_vision`/`generate_product_strategy`/`generate_prd`** — recebem a ideia/texto de entrada mais o `contexto` estruturado (dataclasses de descoberta/visão/estratégia já aceitas, serializadas para o prompt). Campos vazios em `contexto` não são preenchidos artificialmente — a ausência de dado é visível para o LLM, que deve responder com o mesmo campo vazio em vez de inferir.
- **`extract_jobs_to_be_done`** — inclui um resumo do North Star Framework/JTBD de `knowledge/methodology/jtbd.md` na instrução de sistema, para orientar o formato "Quando ... eu quero ... para que ...", sem influenciar o conteúdo extraído.
- **Skills de revisão** (`review_product_vision`, `review_product_strategy`, `review_prd`) — recebem apenas o artefato gerado, sem o texto de entrada original, para forçar uma avaliação baseada no artefato em si (mesmo padrão do revisor do Product Owner).
- **Skills de refinamento** (`refine_product_vision`, `refine_product_strategy`, `refine_prd`) — recebem o artefato atual completo mais as perguntas/respostas de esclarecimento, com instrução explícita de preservar campos não relacionados às respostas (mesmo fix aplicado ao `refine_prd.py` do Product Owner após o bug de erosão de conteúdo encontrado nesta linha de trabalho).

## Limites de tamanho

`knowledge/methodology/` é deliberadamente pequeno (2 arquivos, JTBD e North Star Framework) para caber inteiro no contexto de qualquer chamada sem truncamento. Se isso deixar de ser verdade, a estratégia de contexto precisa ser revisitada antes de qualquer nova skill ser adicionada (ver `memory.md`, seção "Evolução futura").

## O que nunca entra no contexto

Conhecimento de mercado/financeiro do próprio LLM não é — e não pode ser — "injetado" via engenharia de contexto para compensar uma fonte pobre; isso violaria GR-M1/GR-M2 (ver `guardrails.md`). A ausência de dado no texto de entrada deve permanecer ausência no prompt, não ser preenchida por nenhuma camada intermediária.
