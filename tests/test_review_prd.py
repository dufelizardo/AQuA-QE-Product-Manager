from aqua_qe_product_manager.models import PRDDraft
from aqua_qe_product_manager.skills import review_prd as module


def test_review_prd_uses_review_model_and_maps_result(monkeypatch):
    captured = {}

    def fake_complete_json(prompt, system="", model=None):
        captured["model"] = model
        return {"aprovado": True, "problemas": []}

    monkeypatch.setattr(module, "complete_json", fake_complete_json)

    resultado = module.review_prd(PRDDraft(objective="o", scope="e"))

    assert resultado == {"aprovado": True, "problemas": []}
    assert captured["model"] == "phi4"


def test_review_prd_reports_disapproval(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="", model=None: {
            "aprovado": False,
            "problemas": ["escopo confuso"],
        },
    )

    resultado = module.review_prd(PRDDraft(objective="o", scope="e"))

    assert resultado["aprovado"] is False
    assert resultado["problemas"] == ["escopo confuso"]
