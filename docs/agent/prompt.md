# Prompt

> Estrutura conforme `../standards/prompt_standard.md`. Cada skill geradora/revisora tem seu próprio `_SYSTEM`, definido no módulo correspondente em `../../src/aqua_qe_product_manager/skills/`. Este documento resume a instrução de sistema de cada uma — o texto completo, exato, vive no código (fonte única da verdade).

## Skills de descoberta

- **`identify_problem_statement`** — instrui o modelo a extrair problema/usuários afetados/impacto/evidência apenas do texto fornecido; campos não identificáveis devem voltar vazios, nunca inferidos.
- **`synthesize_personas`** — instrui a listar apenas personas sustentadas pelo texto; proíbe adicionar uma persona "típica" do domínio que não esteja no texto.
- **`extract_jobs_to_be_done`** — instrui o formato "Quando [situação], eu quero [motivação], para que [resultado]", com um resumo do JTBD de `knowledge/methodology/jtbd.md`; proíbe inventar jobs não sustentados pelo texto.
- **`extract_market_context`** — o `_SYSTEM` mais crítico deste agente: proíbe explicitamente listar qualquer concorrente ou tendência de mercado que não esteja citado literalmente no texto de entrada, mesmo que o modelo "reconheça" o mercado descrito e "saiba" quem são os concorrentes reais (GR-M1). Instrui a retornar `competitors: []`/`trends: []` quando o texto não citar nenhum.

## Skills de visão

- **`generate_product_vision`** — instrui a gerar `statement`/`target_audience`/`differentiators` a partir da ideia e do `contexto` de descoberta; proíbe inventar `north_star_metric` sem base no texto (GR-M3) — campo vazio é a resposta correta na ausência de dado.
- **`review_product_vision`** — instrui o segundo modelo (`OLLAMA_REVIEW_MODEL`) a avaliar clareza, coerência com a descoberta e ausência de dado inventado, retornando `{"aprovado": bool, "problemas": [...]}`.
- **`generate_vision_clarifying_questions`** — instrui a converter cada item de `review_notes` em uma pergunta objetiva ao usuário.
- **`refine_product_vision`** — instrui a incorporar as respostas do usuário preservando, sem reescrever, os campos que as respostas não abordam (mesmo cuidado do `refine_prd.py` do Product Owner, após o bug de erosão de conteúdo).

## Skills de estratégia

- **`generate_product_strategy`** — instrui a gerar metas (`goals`) coerentes com a visão já aceita; cada meta deve ter métrica e prazo apenas quando informados/inferíveis do contexto, nunca inventados (GR-M3).
- **`review_product_strategy`** — mesmo padrão de `review_product_vision`, avaliando também a coerência entre a estratégia e a visão aceita.
- **`generate_strategy_clarifying_questions`** / **`refine_product_strategy`** — mesmo padrão do par equivalente de visão.

## Skills de PRD

- **`generate_prd`** — instrui a gerar os campos do `PRDDraft` (mesmo schema do Product Owner) a partir da ideia e, quando presente, do `contexto` agregando descoberta/visão/estratégia; sem `contexto`, comporta-se como a geração de PRD equivalente do Product Owner (compatibilidade do caminho simples).
- **`review_prd`** — mesmo padrão de revisão por segundo modelo, avaliando também coerência com visão/estratégia quando existirem.
- **`generate_prd_clarifying_questions`** / **`refine_prd`** — mesmo padrão de refinamento com preservação de campo, incluindo a normalização `_como_texto` para campos que o modelo às vezes retorna como lista.

## Convenção de erro

Toda skill geradora/revisora levanta `ValueError` quando a resposta do LLM não é um JSON válido — nunca tenta "adivinhar" uma estrutura a partir de texto malformado (mesmo padrão do Product Owner).
