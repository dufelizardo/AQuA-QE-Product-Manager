from aqua_qe_product_manager.models import ProductVision
from aqua_qe_product_manager.skills import refine_product_vision as module


def _vision() -> ProductVision:
    return ProductVision(
        statement="statement antigo",
        target_audience="publico antigo",
        differentiators=["diferencial antigo"],
        north_star_metric="metrica antiga",
    )


def test_refine_product_vision_rewrites_fields_from_answers(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {
            "statement": "statement novo",
            "publico_alvo": "publico novo",
            "diferenciais": ["diferencial novo"],
            "metrica_norte": "metrica nova",
        },
    )

    vision = module.refine_product_vision(
        _vision(), [{"pergunta": "qual o publico-alvo?", "resposta": "publico novo"}]
    )

    assert vision.statement == "statement novo"
    assert vision.target_audience == "publico novo"
    assert vision.differentiators == ["diferencial novo"]
    assert vision.north_star_metric == "metrica nova"


def test_refine_product_vision_preserves_fields_not_addressed_by_answers(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {"publico_alvo": "publico novo"},
    )

    vision = module.refine_product_vision(
        _vision(), [{"pergunta": "qual o publico-alvo?", "resposta": "publico novo"}]
    )

    assert vision.target_audience == "publico novo"
    assert vision.statement == "statement antigo"
    assert vision.differentiators == ["diferencial antigo"]
    assert vision.north_star_metric == "metrica antiga"


def test_refine_product_vision_prompt_instrui_a_preservar_detalhe_de_campos_nao_perguntados(
    monkeypatch,
):
    """Regressão análoga ao PRD: refine_product_vision reescreve a visão inteira a cada rodada —
    sem instrução explícita, o LLM tende a simplificar campos não relacionados às respostas."""
    captured = {}

    def fake_complete_json(prompt, system=""):
        captured["prompt"] = prompt
        captured["system"] = system
        return {}

    monkeypatch.setattr(module, "complete_json", fake_complete_json)

    module.refine_product_vision(_vision(), [{"pergunta": "p", "resposta": "r"}])

    assert "preserv" in captured["system"].lower() or "preserv" in captured["prompt"].lower()
