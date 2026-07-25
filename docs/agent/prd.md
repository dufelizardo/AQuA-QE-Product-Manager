# PRD — AQuA-QE Product Manager

> Estrutura conforme `../standards/prd_standard.md`.

## Contexto e problema

O AQuA-QE Product Owner já resolve bem a **execução**: transformar um PRD em Épicos, User Stories e Critérios de Aceitação, com rastreabilidade e revisão humana obrigatória. Mas falta a etapa anterior — a **estratégia**: decidir o que construir e por quê, antes de um PRD existir. Hoje isso continua sendo feito manualmente (ou informalmente, direto na cabeça de quem propõe a ideia), sem estrutura, sem registro de personas/JTBD/contexto de mercado, e sem um ciclo de validação equivalente ao que já existe do lado da execução.

## Objetivo do produto

Estruturar ideias e problemas de negócio informais em artefatos de descoberta e estratégia (problem statement, personas, jobs-to-be-done, contexto de mercado, visão de produto, estratégia de produto) e, a partir deles, gerar um PRD validado — com a mesma rastreabilidade à fonte, validação automática e revisão humana obrigatória que já são padrão no AQuA-QE Product Owner —, pronto para ser entregue a esse agente como entrada.

## Público-alvo / personas

- **Product Manager** — usa o agente para estruturar descoberta e estratégia antes de escrever um PRD formal.
- **Product Owner** — recebe o PRD gerado por este agente como entrada do seu próprio `--modo lote`, sem precisar rodar o próprio `--modo prd` de novo.
- **Fundador/stakeholder de negócio** — usa o agente para transformar uma ideia informal em um PRD estruturado, mesmo sem um Product Manager dedicado.

## Escopo

- Ler fontes de entrada em arquivo de texto (`.txt`), Markdown ou chat.
- Sintetizar problem statement, personas e jobs-to-be-done a partir do que o usuário efetivamente forneceu — nunca a partir de pesquisa não realizada.
- Estruturar contexto de mercado (concorrentes, tendências) só a partir do que o usuário citou explicitamente — nunca do conhecimento geral do modelo sobre o mercado.
- Gerar e refinar visão de produto e estratégia de produto, com o mesmo ciclo humano-no-loop (gerar → validar → revisar por segundo LLM → perguntas de esclarecimento → refinar → aceite humano explícito) usado no PRD.
- Gerar e refinar um PRD, incorporando descoberta/visão/estratégia quando disponíveis, ou funcionando só a partir de uma ideia crua quando não estiverem.
- Exportar o PRD final em Markdown, no mesmo formato que o AQuA-QE Product Owner já consome como entrada (`prd_standard.md` compartilhado).
- Priorizar os requisitos funcionais do PRD aceito em MoSCoW (automático, a partir de sinal de linguagem no texto) ou RICE/WSJF (números sempre coletados do usuário, nunca estimados — GR-M4), exportado sempre num arquivo separado do PRD.

## Fora de escopo

- Realizar pesquisa de mercado, entrevistas com clientes ou qualquer atividade de coleta de dados do mundo real — o agente só estrutura o que já foi coletado e informado pelo usuário.
- Priorização Kano — **permanentemente** fora de escopo (não uma questão de fase): depende estruturalmente de dados de pesquisa de satisfação de cliente que não existem no tipo de entrada deste agente (ideia informal/PRD/chat), em nenhuma fase futura.
- Definição formal de escopo de MVP e business case (ROI/CAC/LTV) — avaliados e deliberadamente adiados para uma fase futura (ver `WHITEPAPER.md`, seção "O que ainda falta").
- Comunicação entre times e gestão de stakeholders — são atividades interpessoais, não de geração de documento.
- Transformar o PRD em Épicos/User Stories — isso é responsabilidade do AQuA-QE Product Owner, que recebe o PRD como entrada.
- Aprovar definitivamente qualquer artefato sem revisão humana (ver `guardrails.md`).

## Requisitos funcionais

1. Ler e interpretar entradas em arquivo de texto (`.txt`), Markdown e chat.
2. Sintetizar problem statement, personas e jobs-to-be-done a partir do texto de entrada.
3. Estruturar contexto de mercado (concorrentes, tendências) exclusivamente a partir do texto de entrada.
4. Gerar visão de produto (`generate_product_vision`), validar, revisar por um segundo LLM, e refinar com respostas do usuário.
5. Gerar estratégia de produto (`generate_product_strategy`) a partir da visão aceita, com o mesmo ciclo.
6. Gerar um PRD (`generate_prd`), incorporando descoberta/visão/estratégia quando existirem no contexto da sessão.
7. Quando a fonte for ambígua ou incompleta, parar e solicitar esclarecimento em vez de gerar uma suposição não sinalizada (ver `guardrails.md`).
8. Exportar o PRD validado em Markdown, compatível com a entrada esperada pelo AQuA-QE Product Owner.
9. Priorizar os requisitos funcionais do PRD aceito, em MoSCoW (`classify_moscow`) ou RICE/WSJF (`compute_rice_score`/`compute_wsjf_score`, números sempre coletados do usuário), exportando o resultado num arquivo separado do PRD.

## Requisitos não funcionais

- **Rastreabilidade** — todo elemento gerado (problem statement, persona, JTBD, concorrente, meta estratégica) deve ser rastreável à fonte de entrada.
- **Nenhuma invenção de dado de mercado, financeiro ou de priorização RICE/WSJF** — ver GR-M1/GR-M2/GR-M4 em `guardrails.md`, os guardrails mais críticos deste agente.
- **Nenhuma aprovação automática** — toda saída é um rascunho validado, sujeito a aceite humano explícito.
- **Compatibilidade de formato com o AQuA-QE Product Owner** — o PRD exportado usa exatamente os mesmos campos que o `PRDDraft` do Product Owner já sabe interpretar.

## Métricas de sucesso

- Redução do tempo entre "ideia informal" e "PRD pronto para virar Épicos".
- Taxa de aceitação sem retrabalho — % de PRDs gerados aceitos sem edição substancial na revisão humana.
- % de PRDs gerados por este agente que o AQuA-QE Product Owner processa sem erro no `--modo lote`.

## Riscos e premissas

- Premissa: o usuário fornece informação suficiente sobre mercado/concorrentes quando quer que ela apareça no PRD; na ausência dela, o agente não deve inventar para "parecer mais completo".
- Risco: um Product Manager humano tende a esperar que o agente "saiba" o mercado — a comunicação do produto precisa deixar claro que o agente não pesquisa, só estrutura o que é informado.
- Risco: o mesmo revisor local (`phi4`) usado no AQuA-QE Product Owner mostrou, nesta mesma sessão de trabalho, um padrão real de não convergência em ciclos de refinamento longos (PRD levou 7 rodadas sem aprovar de fato) — o mesmo padrão pode se repetir aqui, e o aceite humano explícito existe justamente para não bloquear o fluxo por isso.
