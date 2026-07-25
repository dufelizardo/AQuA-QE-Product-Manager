from aqua_qe_product_manager.models import PrioritizedRequirement
from aqua_qe_product_manager.workflow import prioritize_requirements as workflow_module


def test_classify_moscow_draft_retorna_classificacao_quando_valida(monkeypatch):
    classificacao = [
        PrioritizedRequirement(requirement="A", moscow="must"),
        PrioritizedRequirement(requirement="B", moscow="could"),
    ]
    monkeypatch.setattr(workflow_module, "classify_moscow", lambda requisitos, texto: classificacao)
    monkeypatch.setattr(workflow_module, "validate_moscow_classification", lambda itens, req: True)

    resultado = workflow_module.classify_moscow_draft(["A", "B"], "texto do PRD")

    assert resultado == classificacao


def test_classify_moscow_draft_aplica_fallback_seguro_quando_invalida(monkeypatch):
    classificacao_inconsistente = [PrioritizedRequirement(requirement="Outra coisa", moscow="must")]
    monkeypatch.setattr(
        workflow_module, "classify_moscow", lambda requisitos, texto: classificacao_inconsistente
    )
    monkeypatch.setattr(workflow_module, "validate_moscow_classification", lambda itens, req: False)

    resultado = workflow_module.classify_moscow_draft(["A", "B"], "texto do PRD")

    assert resultado == [
        PrioritizedRequirement(requirement="A"),
        PrioritizedRequirement(requirement="B"),
    ]
    assert all(item.moscow == "" for item in resultado)
