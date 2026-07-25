from aqua_qe_product_manager.skills import generate_product_vision as module


def test_generate_product_vision_maps_json_to_model(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {
            "statement": "ser a forma mais simples de investir em CDB",
            "publico_alvo": "investidores iniciantes",
            "diferenciais": ["simplicidade", "taxas baixas"],
            "metrica_norte": "volume investido por usuario ativo",
        },
    )

    vision = module.generate_product_vision("uma ideia")

    assert vision.statement == "ser a forma mais simples de investir em CDB"
    assert vision.target_audience == "investidores iniciantes"
    assert vision.differentiators == ["simplicidade", "taxas baixas"]
    assert vision.north_star_metric == "volume investido por usuario ativo"


def test_generate_product_vision_defaults_to_empty_when_llm_omits_fields(monkeypatch):
    monkeypatch.setattr(module, "complete_json", lambda prompt, system="": {})

    vision = module.generate_product_vision("uma ideia")

    assert vision.statement == ""
    assert vision.target_audience == ""
    assert vision.differentiators == []
    assert vision.north_star_metric == ""


def test_generate_product_vision_aceita_contexto_de_descoberta(monkeypatch):
    captured = {}

    def fake_complete_json(prompt, system=""):
        captured["prompt"] = prompt
        return {"statement": "s", "publico_alvo": "p"}

    monkeypatch.setattr(module, "complete_json", fake_complete_json)

    contexto = {"problem_statement": "problema identificado"}
    module.generate_product_vision("uma ideia", contexto)

    assert "problema identificado" in captured["prompt"]
