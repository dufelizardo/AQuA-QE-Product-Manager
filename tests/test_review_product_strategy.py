from aqua_qe_product_manager.models import ProductStrategy, StrategicGoal
from aqua_qe_product_manager.skills import review_product_strategy as module


def test_review_product_strategy_uses_review_model_and_maps_result(monkeypatch):
    captured = {}

    def fake_complete_json(prompt, system="", model=None):
        captured["model"] = model
        return {"aprovado": True, "problemas": []}

    monkeypatch.setattr(module, "complete_json", fake_complete_json)

    strategy = ProductStrategy(goals=[StrategicGoal(description="meta", metric="metrica")])
    resultado = module.review_product_strategy(strategy)

    assert resultado == {"aprovado": True, "problemas": []}
    assert captured["model"] == "phi4"


def test_review_product_strategy_reports_disapproval(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "aprovado": False,
            "problemas": ["meta sem relacao clara com a visao"],
        },
    )

    strategy = ProductStrategy(goals=[StrategicGoal(description="meta", metric="metrica")])
    resultado = module.review_product_strategy(strategy)

    assert resultado["aprovado"] is False
    assert resultado["problemas"] == ["meta sem relacao clara com a visao"]
