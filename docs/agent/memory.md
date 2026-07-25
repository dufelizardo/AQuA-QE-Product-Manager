# Memory

> Estrutura conforme `../standards/memory_standard.md`.

## Configuração desta fase

```yaml
memory:
  vector: false
  rag: false
  knowledge_graph: false
```

Sem memória vetorial, RAG ou grafo de conhecimento na Fase 1 — mesma decisão do AQuA-QE Product Owner: não construir infraestrutura de recuperação antes de haver um consumidor real que a justifique. `knowledge/methodology/` é pequeno o suficiente para caber direto no prompt de cada skill (ver `context_engineering.md`).

## Estado dentro de uma execução

O agente mantém estado apenas durante a execução de uma sessão do CLI (`run.py`): descoberta sintetizada, visão aceita, estratégia aceita e o PRD em construção, passados adiante como `contexto` entre workflows (`--modo completo`). Não há persistência entre execuções — cada rodada do CLI começa do zero, a menos que o usuário forneça artefatos já produzidos anteriormente (ex.: reexecutar `--modo prd` apontando para uma visão/estratégia já exportadas).

## Persistência de artefatos

Os únicos artefatos persistidos em disco são as saídas exportadas via `export_markdown`/`format_prd_markdown` — arquivos Markdown comuns, sem formato proprietário, para que o handoff ao AQuA-QE Product Owner (ou a retomada manual de uma sessão) não dependa de nenhum estado interno do agente.

## Evolução futura

Se o volume de `knowledge/methodology/` crescer a ponto de não caber mais direto no contexto do prompt, ou se surgir necessidade real de retomar sessões entre execuções, essa decisão é revisitada — não antes, mesmo padrão adotado no Product Owner (ver `WHITEPAPER.md`, seção sobre decisões deliberadamente adiadas).
