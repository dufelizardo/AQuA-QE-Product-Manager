from aqua_qe_product_manager.models import ProductVision
from aqua_qe_product_manager.skills import review_product_vision as module


def test_review_product_vision_uses_review_model_and_maps_result(monkeypatch):
    captured = {}

    def fake_complete_json(prompt, system="", model=None):
        captured["model"] = model
        return {"aprovado": True, "problemas": []}

    monkeypatch.setattr(module, "complete_json", fake_complete_json)

    resultado = module.review_product_vision(
        ProductVision(statement="s", target_audience="p")
    )

    assert resultado == {"aprovado": True, "problemas": []}
    assert captured["model"] == "phi4"


def test_review_product_vision_reports_disapproval(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "aprovado": False,
            "problemas": ["metrica norte sem relacao com o statement"],
        },
    )

    resultado = module.review_product_vision(
        ProductVision(statement="s", target_audience="p")
    )

    assert resultado["aprovado"] is False
    assert resultado["problemas"] == ["metrica norte sem relacao com o statement"]


def test_review_product_vision_uses_env_override_for_review_model(monkeypatch):
    captured = {}

    def fake_complete_json(prompt, system="", model=None):
        captured["model"] = model
        return {"aprovado": True, "problemas": []}

    monkeypatch.setattr(module, "complete_json", fake_complete_json)
    monkeypatch.setenv("OLLAMA_REVIEW_MODEL", "outro-modelo")

    module.review_product_vision(ProductVision(statement="s", target_audience="p"))

    assert captured["model"] == "outro-modelo"
