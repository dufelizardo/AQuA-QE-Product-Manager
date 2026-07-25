# Acceptance Patterns

> Como o CLI (`run.py`) conduz o aceite humano de cada artefato. Mesmo padrão do AQuA-QE Product Owner — aceitação é **sempre** perguntada explicitamente, nunca inferida ou automática (ver RULE-005 em `rules.md`), independentemente de o artefato ter passado por refinamento ou não.

## Ciclo padrão, por artefato (visão, estratégia, PRD)

1. `generate_*` produz o rascunho.
2. `validate_*` roda o checklist automático (`validation_checklist.md`). Se falhar, o CLI informa o motivo e não avança para revisão.
3. `review_*` (segundo LLM) avalia o rascunho validado.
   - **Aprovado, sem apontamentos** → segue para o passo 4.
   - **Reprovado, com apontamentos** → `generate_*_clarifying_questions` gera perguntas; o CLI as apresenta ao usuário via `input()`; as respostas alimentam `refine_*`; o artefato refinado volta ao passo 2 (revalidação).
4. O CLI pergunta explicitamente: aceitar como está / tentar mais uma rodada de refinamento / descartar. Nunca assume aceitação por padrão.
5. Só após resposta explícita de aceite o `status` do artefato é setado para `accepted` — esse `set` acontece no CLI, nunca dentro de `generate_*`/`refine_*`.

## Particularidade da descoberta

Os artefatos de descoberta (`ProblemStatement`, `list[Persona]`, `list[JobToBeDone]`, `MarketAnalysis`) não têm um ciclo de aceite formal isolado — são insumos estruturados que alimentam a visão/estratégia/PRD, não entregas terminais por si. Ainda assim, ao entrar no modo `--modo completo`, o CLI exibe a descoberta sintetizada ao usuário antes de prosseguir, dando a chance de corrigir a fonte (reeditar o texto de entrada) antes de gerar visão/estratégia/PRD sobre uma base incorreta.

## Limite de rodadas

Não há um limite artificial de rodadas de refinamento — mesma decisão do Product Owner: o usuário decide quando parar (aceitar ou descartar), o agente nunca força convergência.

## Descartar um artefato

Se o usuário escolhe descartar, o CLI encerra o modo atual sem persistir nada — nenhum arquivo é exportado, nenhum estado fica pendurado para a próxima execução (ver `memory.md`).
