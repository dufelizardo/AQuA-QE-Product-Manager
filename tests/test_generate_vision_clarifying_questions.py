from aqua_qe_product_manager.models import ProductVision
from aqua_qe_product_manager.skills import generate_vision_clarifying_questions as module


def test_returns_empty_list_without_review_notes():
    vision = ProductVision(statement="s", target_audience="p", review_notes=[])

    assert module.generate_vision_clarifying_questions(vision) == []


def test_maps_json_response_to_question_list(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {"perguntas": ["Qual o publico-alvo especifico?"]},
    )
    vision = ProductVision(
        statement="s", target_audience="p", review_notes=["publico-alvo vago"]
    )

    resultado = module.generate_vision_clarifying_questions(vision)

    assert resultado == ["Qual o publico-alvo especifico?"]
