# Jobs to Be Done (JTBD)

> Baseado na Teoria dos Jobs to Be Done, popularizada por Clayton Christensen (Harvard Business School) e formalizada por autores como Anthony Ulwick (Outcome-Driven Innovation) e Bob Moesta.

## O que é

Um framework para entender a motivação de compra/adoção de um produto: pessoas não "compram" produtos, elas os "contratam" para realizar um progresso específico ("job") em uma circunstância particular de suas vidas. O foco é a situação e o resultado desejado, não o produto em si.

## Estrutura de um Job to Be Done

Um JTBD bem formulado tem três componentes:

- **Situação (circumstance)** — o contexto específico em que a necessidade surge ("Quando ...").
- **Motivação (motivation/force)** — o que a pessoa está tentando alcançar ou evitar ("eu quero ...").
- **Resultado esperado (expected outcome)** — como a pessoa mede sucesso ao "contratar" uma solução ("para que ...").

Formato de sentença recomendado: *"Quando [situação], eu quero [motivação], para que [resultado esperado]."*

## Tipos de job

- **Job funcional** — a tarefa prática que a pessoa precisa realizar.
- **Job emocional** — como a pessoa quer se sentir (ou evitar sentir) ao realizar o job.
- **Job social** — como a pessoa quer ser percebida por outros ao realizar o job.

## Diferença entre JTBD e Persona

Uma persona descreve **quem** é o usuário (características, objetivos gerais, dores). Um JTBD descreve **o progresso que essa pessoa busca em uma circunstância específica**, independentemente de qual produto ela usa hoje para isso — dois usuários muito diferentes podem compartilhar o mesmo job, e a mesma persona pode ter múltiplos jobs em contextos diferentes.

## Relevância para este agente

`extract_jobs_to_be_done` estrutura os jobs identificados na fonte de entrada nesse formato de três partes, sempre rastreáveis a uma citação — nunca inferidos de um job "típico" da categoria de produto. Os jobs identificados alimentam `generate_product_vision` (o `statement` da visão deve endereçar o job principal) e `generate_prd` (requisitos funcionais devem ser rastreáveis a um job, não gerados soltos).
