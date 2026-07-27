from ..models import PRDDraft


def _lista_md(itens: list[str]) -> str:
    return "\n".join(f"- {item}" for item in itens) if itens else "(nenhum)"


def _lista_numerada_md(itens: list[str], prefixo: str) -> str:
    if not itens:
        return "(nenhum)"
    return "\n".join(f"- {prefixo}-{i + 1:03d}: {item}" for i, item in enumerate(itens))


def _lista_inline(itens: list[str]) -> str:
    """Junta os itens numa única linha (evita embutir uma lista já formatada dentro de um item de outra lista — Markdown aninhado inválido, ver issue #8)."""
    return "; ".join(itens) if itens else "(nenhum)"


def _personas_md(personas: list) -> str:
    if not personas:
        return "(nenhuma)"
    linhas = []
    for persona in personas:
        linhas += [
            f"### {persona.name}",
            "",
            f"- Descrição: {persona.description}",
            f"- Objetivos: {_lista_inline(persona.goals)}",
            f"- Pontos de dor: {_lista_inline(persona.pain_points)}",
            "",
        ]
    return "\n".join(linhas).rstrip()


def _jornadas_md(jornadas: list) -> str:
    if not jornadas:
        return "(nenhuma)"
    linhas = []
    for jornada in jornadas:
        linhas.append(f"### {jornada.name}")
        linhas.append("")
        linhas += [f"{i + 1}. {passo}" for i, passo in enumerate(jornada.steps)]
        linhas.append("")
    return "\n".join(linhas).rstrip()


def _objetivos_negocio_md(objetivos: list) -> str:
    if not objetivos:
        return "(nenhum)"
    return "\n".join(f"| {obj.objective} | {obj.kpi or '(sem KPI claro)'} |" for obj in objetivos)


def _glossario_md(termos: list) -> str:
    if not termos:
        return "(nenhum)"
    return "\n".join(f"- **{termo.term}**: {termo.definition}" for termo in termos)


def format_prd_markdown(draft: PRDDraft) -> str:
    """Formata o PRD em Markdown, seções conforme docs/standards/prd_standard.md.

    O texto resultante é diretamente consumível pelo AQuA-QE Product Owner
    via `--modo lote --arquivo` — as 9 seções originais que o Product Owner
    já sabe interpretar mantêm texto/ordem inalterados; as seções de
    profundidade abaixo são só adições.
    """
    return (
        "# PRD\n\n"
        f"## Contexto e problema\n{draft.context_problem}\n\n"
        f"## Objetivo do produto\n{draft.objective}\n\n"
        f"## Objetivos de Negócio (KPI)\n\n| Objetivo | KPI |\n|---|---|\n{_objetivos_negocio_md(draft.business_objectives)}\n\n"
        f"## Público-alvo\n{draft.target_audience}\n\n"
        f"## Personas\n\n{_personas_md(draft.personas)}\n\n"
        f"## Jornadas do Usuário\n\n{_jornadas_md(draft.user_journeys)}\n\n"
        f"## Escopo\n{draft.scope}\n\n"
        f"## Fora de escopo\n{draft.out_of_scope}\n\n"
        f"## Casos de Uso\n{_lista_md(draft.use_cases)}\n\n"
        f"## Requisitos funcionais\n{_lista_numerada_md(draft.functional_requirements, 'RF')}\n\n"
        f"## Requisitos não funcionais\n{_lista_numerada_md(draft.non_functional_requirements, 'RNF')}\n\n"
        f"## MVP\n{_lista_md(draft.mvp_scope)}\n\n"
        f"## Versão Futura\n{_lista_md(draft.future_scope)}\n\n"
        f"## Critérios de sucesso\n{_lista_md(draft.success_criteria)}\n\n"
        f"## Métricas de Produto Candidatas (sugeridas, a confirmar)\n{_lista_md(draft.candidate_product_metrics)}\n\n"
        f"## Riscos e premissas\n{_lista_md(draft.risks_assumptions)}\n\n"
        f"## Dependências\n{_lista_md(draft.dependencies)}\n\n"
        f"## Premissas Técnicas\n{_lista_md(draft.technical_assumptions)}\n\n"
        f"## Restrições\n{_lista_md(draft.constraints)}\n\n"
        f"## Glossário\n{_glossario_md(draft.glossary)}\n"
    )
