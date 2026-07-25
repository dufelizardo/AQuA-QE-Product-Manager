from aqua_qe_product_manager.models import PRDDraft
from aqua_qe_product_manager.skills.format_prd_markdown import format_prd_markdown
from aqua_qe_product_manager.skills.parse_prd_markdown import parse_prd_markdown


def _draft_completo() -> PRDDraft:
    return PRDDraft(
        context_problem="contexto do problema",
        objective="objetivo do produto",
        target_audience="publico-alvo",
        scope="o que o produto faz",
        out_of_scope="o que o produto nao faz",
        functional_requirements=["requisito 1", "requisito 2"],
        non_functional_requirements=["nao funcional 1"],
        success_criteria=["criterio 1", "criterio 2"],
        risks_assumptions=["risco 1"],
    )


def test_round_trip_preserva_todos_os_campos_de_conteudo():
    original = _draft_completo()

    reconstruido = parse_prd_markdown(format_prd_markdown(original))

    assert reconstruido.context_problem == original.context_problem
    assert reconstruido.objective == original.objective
    assert reconstruido.target_audience == original.target_audience
    assert reconstruido.scope == original.scope
    assert reconstruido.out_of_scope == original.out_of_scope
    assert reconstruido.functional_requirements == original.functional_requirements
    assert reconstruido.non_functional_requirements == original.non_functional_requirements
    assert reconstruido.success_criteria == original.success_criteria
    assert reconstruido.risks_assumptions == original.risks_assumptions


def test_round_trip_com_listas_vazias_placeholder_nenhum():
    original = PRDDraft(
        context_problem="contexto",
        objective="objetivo",
        scope="escopo",
        functional_requirements=["requisito 1"],
        success_criteria=["criterio 1"],
    )

    reconstruido = parse_prd_markdown(format_prd_markdown(original))

    assert reconstruido.non_functional_requirements == []
    assert reconstruido.risks_assumptions == []
    assert reconstruido.target_audience == ""
    assert reconstruido.out_of_scope == ""


def test_secao_ausente_fica_com_default_vazio_sem_lancar_erro():
    texto = "# PRD\n\n## Contexto e problema\nsó isso mesmo\n"

    draft = parse_prd_markdown(texto)

    assert draft.context_problem == "só isso mesmo"
    assert draft.objective == ""
    assert draft.functional_requirements == []
    assert draft.status.value == "pending_clarification"


def test_cabecalho_desconhecido_e_ignorado():
    texto = (
        "# PRD\n\n"
        "## Contexto e problema\ncontexto\n\n"
        "## Seção que não existe no padrão\nconteúdo qualquer\n"
    )

    draft = parse_prd_markdown(texto)

    assert draft.context_problem == "contexto"
