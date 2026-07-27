from aqua_qe_product_manager.models import (
    BusinessObjective,
    GlossaryTerm,
    PRDDraft,
    Persona,
    UserJourney,
)
from aqua_qe_product_manager.skills.format_prd_markdown import format_prd_markdown


def test_format_prd_markdown_includes_all_original_sections():
    draft = PRDDraft(
        context_problem="contexto do problema",
        objective="objetivo do produto",
        target_audience="publico alvo",
        scope="escopo",
        out_of_scope="fora de escopo",
        functional_requirements=["requisito funcional 1"],
        non_functional_requirements=["requisito nao funcional 1"],
        success_criteria=["criterio de sucesso 1"],
        risks_assumptions=["risco 1"],
    )

    texto = format_prd_markdown(draft)

    assert "# PRD" in texto
    assert "## Contexto e problema" in texto
    assert "contexto do problema" in texto
    assert "## Objetivo do produto" in texto
    assert "objetivo do produto" in texto
    assert "## Público-alvo" in texto
    assert "## Escopo" in texto
    assert "## Fora de escopo" in texto
    assert "## Requisitos funcionais" in texto
    assert "RF-001: requisito funcional 1" in texto
    assert "## Requisitos não funcionais" in texto
    assert "RNF-001: requisito nao funcional 1" in texto
    assert "## Critérios de sucesso" in texto
    assert "## Riscos e premissas" in texto
    assert "risco 1" in texto


def test_format_prd_markdown_includes_depth_sections():
    draft = PRDDraft(
        context_problem="c",
        objective="o",
        scope="e",
        personas=[
            Persona(name="Paciente", description="usa o app", goals=["marcar consulta"])
        ],
        user_journeys=[UserJourney(name="Agendamento", steps=["Cadastro", "Agenda"])],
        business_objectives=[BusinessObjective(objective="Reduzir fila", kpi="30%")],
        use_cases=["Paciente agenda consulta"],
        dependencies=["SUS"],
        technical_assumptions=["Internet disponivel"],
        constraints=["Orcamento limitado"],
        glossary=[GlossaryTerm(term="Unidade", definition="Unidade de saude")],
        candidate_product_metrics=["MAU"],
        mvp_scope=["Cadastro"],
        future_scope=["Notificacoes"],
    )

    texto = format_prd_markdown(draft)

    assert "## Personas" in texto
    assert "### Paciente" in texto
    assert "## Jornadas do Usuário" in texto
    assert "### Agendamento" in texto
    assert "1. Cadastro" in texto
    assert "## Objetivos de Negócio (KPI)" in texto
    assert "| Reduzir fila | 30% |" in texto
    assert "## Casos de Uso" in texto
    assert "Paciente agenda consulta" in texto
    assert "## Dependências" in texto
    assert "SUS" in texto
    assert "## Premissas Técnicas" in texto
    assert "Internet disponivel" in texto
    assert "## Restrições" in texto
    assert "Orcamento limitado" in texto
    assert "## Glossário" in texto
    assert "**Unidade**: Unidade de saude" in texto
    assert "## Métricas de Produto Candidatas (sugeridas, a confirmar)" in texto
    assert "MAU" in texto
    assert "## MVP" in texto
    assert "## Versão Futura" in texto
    assert "Notificacoes" in texto


def test_format_prd_markdown_handles_empty_lists():
    draft = PRDDraft(context_problem="c", objective="o", scope="e")

    texto = format_prd_markdown(draft)

    assert "(nenhum)" in texto
    assert "(nenhuma)" in texto
