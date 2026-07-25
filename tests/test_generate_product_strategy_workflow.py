from aqua_qe_product_manager.models import ArtifactStatus, ProductStrategy, StrategicGoal
from aqua_qe_product_manager.workflow import generate_product_strategy as workflow_module


def _strategy_valida() -> ProductStrategy:
    return ProductStrategy(goals=[StrategicGoal(description="meta", metric="metrica")])


def test_finalize_strategy_marca_pending_clarification_quando_validate_falha(monkeypatch):
    monkeypatch.setattr(workflow_module, "validate_product_strategy", lambda strategy: False)

    resultado = workflow_module.finalize_strategy(ProductStrategy())

    assert resultado.status == ArtifactStatus.PENDING_CLARIFICATION


def test_finalize_strategy_marca_pending_clarification_quando_review_reprova(monkeypatch):
    monkeypatch.setattr(workflow_module, "validate_product_strategy", lambda strategy: True)
    monkeypatch.setattr(
        workflow_module,
        "review_product_strategy",
        lambda strategy: {"aprovado": False, "problemas": ["meta vaga"]},
    )

    resultado = workflow_module.finalize_strategy(_strategy_valida())

    assert resultado.status == ArtifactStatus.PENDING_CLARIFICATION
    assert resultado.review_notes == ["meta vaga"]


def test_finalize_strategy_marca_draft_validated_quando_review_aprova(monkeypatch):
    monkeypatch.setattr(workflow_module, "validate_product_strategy", lambda strategy: True)
    monkeypatch.setattr(
        workflow_module,
        "review_product_strategy",
        lambda strategy: {"aprovado": True, "problemas": []},
    )

    resultado = workflow_module.finalize_strategy(_strategy_valida())

    assert resultado.status == ArtifactStatus.DRAFT_VALIDATED


def test_generate_strategy_draft_gera_e_finaliza(monkeypatch):
    monkeypatch.setattr(
        workflow_module,
        "generate_product_strategy",
        lambda vision, contexto=None: _strategy_valida(),
    )
    monkeypatch.setattr(workflow_module, "validate_product_strategy", lambda strategy: True)
    monkeypatch.setattr(
        workflow_module,
        "review_product_strategy",
        lambda strategy: {"aprovado": True, "problemas": []},
    )

    strategy = workflow_module.generate_strategy_draft(object())

    assert strategy.status == ArtifactStatus.DRAFT_VALIDATED
    assert strategy.goals[0].description == "meta"


def test_refine_strategy_draft_refina_e_finaliza(monkeypatch):
    def fake_refine_product_strategy(strategy, respostas):
        strategy.time_horizon = "12 meses"
        return strategy

    monkeypatch.setattr(
        workflow_module, "refine_product_strategy", fake_refine_product_strategy
    )
    monkeypatch.setattr(workflow_module, "validate_product_strategy", lambda strategy: True)
    monkeypatch.setattr(
        workflow_module,
        "review_product_strategy",
        lambda strategy: {"aprovado": True, "problemas": []},
    )

    strategy = workflow_module.refine_strategy_draft(
        _strategy_valida(), [{"pergunta": "qual o horizonte?", "resposta": "12 meses"}]
    )

    assert strategy.time_horizon == "12 meses"
    assert strategy.status == ArtifactStatus.DRAFT_VALIDATED
