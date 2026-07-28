# Memory

> Estrutura conforme `../standards/memory_standard.md`.

## Configuração desta fase

```yaml
memory:
  vector: true
  rag: true
  knowledge_graph: false
```

`vector`/`rag` passaram de `false` para `true` com a issue [#9](https://github.com/dufelizardo/AQuA-QE-Product-Manager/issues/9): memória institucional de respostas de ciclos de refinamento (`services/embedding_service.py` + `services/rag_service.py`, collection Qdrant embarcada `refinement_answer_memory`) — cada resposta que o humano dá numa pergunta de esclarecimento (visão, estratégia ou PRD) é gravada e, num ciclo futuro, sugerida (nunca aplicada automaticamente) se uma pergunta parecida aparecer. Antes disso, este agente não tinha nenhuma infraestrutura de embedding — a mesma decisão do AQuA-QE Product Owner (não construir infraestrutura de recuperação antes de haver um consumidor real que a justifique) segue valendo para o restante: `knowledge/methodology/` continua sem RAG, pequeno o suficiente para caber direto no prompt de cada skill (ver `context_engineering.md`) — ideia distinta, ainda sem consumidor real.

## Estado dentro de uma execução

O agente mantém estado apenas durante a execução de uma sessão do CLI (`run.py`): descoberta sintetizada, visão aceita, estratégia aceita e o PRD em construção, passados adiante como `contexto` entre workflows (`--modo completo`). Não há persistência entre execuções — cada rodada do CLI começa do zero, a menos que o usuário forneça artefatos já produzidos anteriormente (ex.: reexecutar `--modo prd` apontando para uma visão/estratégia já exportadas).

## Persistência de artefatos

Os únicos artefatos persistidos em disco são as saídas exportadas via `export_markdown`/`format_prd_markdown` — arquivos Markdown comuns, sem formato proprietário, para que o handoff ao AQuA-QE Product Owner (ou a retomada manual de uma sessão) não dependa de nenhum estado interno do agente.

## Evolução futura

Se o volume de `knowledge/methodology/` crescer a ponto de não caber mais direto no contexto do prompt, ou se surgir necessidade real de retomar sessões entre execuções, essa decisão (RAG sobre `knowledge/methodology/`, ainda `false` em termos de consumidor real) é revisitada — não antes, mesmo padrão adotado no Product Owner (ver `WHITEPAPER.md`, seção sobre decisões deliberadamente adiadas). A memória institucional de refinamento (acima) já passou por essa revisão, com o consumidor real da issue #9.
