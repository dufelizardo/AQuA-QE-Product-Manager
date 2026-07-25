from aqua_qe_product_manager.models import ArtifactStatus, ProductVision
from aqua_qe_product_manager.workflow import generate_product_vision as workflow_module


def _vision_valida() -> ProductVision:
    return ProductVision(statement="statement", target_audience="publico")


def test_finalize_vision_marca_pending_clarification_quando_validate_falha(monkeypatch):
    monkeypatch.setattr(workflow_module, "validate_product_vision", lambda vision: False)

    resultado = workflow_module.finalize_vision(ProductVision())

    assert resultado.status == ArtifactStatus.PENDING_CLARIFICATION


def test_finalize_vision_marca_pending_clarification_quando_review_reprova(monkeypatch):
    monkeypatch.setattr(workflow_module, "validate_product_vision", lambda vision: True)
    monkeypatch.setattr(
        workflow_module,
        "review_product_vision",
        lambda vision: {"aprovado": False, "problemas": ["publico-alvo vago"]},
    )

    resultado = workflow_module.finalize_vision(_vision_valida())

    assert resultado.status == ArtifactStatus.PENDING_CLARIFICATION
    assert resultado.review_notes == ["publico-alvo vago"]


def test_finalize_vision_marca_draft_validated_quando_review_aprova(monkeypatch):
    monkeypatch.setattr(workflow_module, "validate_product_vision", lambda vision: True)
    monkeypatch.setattr(
        workflow_module,
        "review_product_vision",
        lambda vision: {"aprovado": True, "problemas": []},
    )

    resultado = workflow_module.finalize_vision(_vision_valida())

    assert resultado.status == ArtifactStatus.DRAFT_VALIDATED


def test_generate_vision_draft_gera_e_finaliza(monkeypatch):
    monkeypatch.setattr(
        workflow_module, "generate_product_vision", lambda ideia, contexto=None: _vision_valida()
    )
    monkeypatch.setattr(workflow_module, "validate_product_vision", lambda vision: True)
    monkeypatch.setattr(
        workflow_module,
        "review_product_vision",
        lambda vision: {"aprovado": True, "problemas": []},
    )

    vision = workflow_module.generate_vision_draft("uma ideia qualquer")

    assert vision.status == ArtifactStatus.DRAFT_VALIDATED
    assert vision.statement == "statement"


def test_refine_vision_draft_refina_e_finaliza(monkeypatch):
    def fake_refine_product_vision(vision, respostas):
        vision.statement = "statement refinado"
        return vision

    monkeypatch.setattr(workflow_module, "refine_product_vision", fake_refine_product_vision)
    monkeypatch.setattr(workflow_module, "validate_product_vision", lambda vision: True)
    monkeypatch.setattr(
        workflow_module,
        "review_product_vision",
        lambda vision: {"aprovado": True, "problemas": []},
    )

    vision = workflow_module.refine_vision_draft(
        _vision_valida(),
        [{"pergunta": "qual o statement?", "resposta": "statement refinado"}],
    )

    assert vision.statement == "statement refinado"
    assert vision.status == ArtifactStatus.DRAFT_VALIDATED
