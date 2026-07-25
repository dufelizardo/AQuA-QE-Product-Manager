from aqua_qe_product_manager.models import ProductStrategy, StrategicGoal
from aqua_qe_product_manager.skills import generate_strategy_clarifying_questions as module


def test_returns_empty_list_without_review_notes():
    strategy = ProductStrategy(
        goals=[StrategicGoal(description="meta", metric="metrica")], review_notes=[]
    )

    assert module.generate_strategy_clarifying_questions(strategy) == []


def test_maps_json_response_to_question_list(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {"perguntas": ["Qual o alvo numerico da meta?"]},
    )
    strategy = ProductStrategy(
        goals=[StrategicGoal(description="meta", metric="metrica")],
        review_notes=["meta sem alvo definido"],
    )

    resultado = module.generate_strategy_clarifying_questions(strategy)

    assert resultado == ["Qual o alvo numerico da meta?"]
