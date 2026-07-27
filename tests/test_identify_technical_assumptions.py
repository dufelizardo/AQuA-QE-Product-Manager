from aqua_qe_product_manager.skills import identify_technical_assumptions as module


def test_identify_technical_assumptions_maps_json_to_list(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {"premissas": ["Internet disponivel nas unidades"]},
    )

    resultado = module.identify_technical_assumptions("texto qualquer")

    assert resultado == ["Internet disponivel nas unidades"]


def test_identify_technical_assumptions_returns_empty_list_when_none_identified(monkeypatch):
    monkeypatch.setattr(module, "complete_json", lambda prompt, system="": {"premissas": []})

    resultado = module.identify_technical_assumptions("texto sem premissa")

    assert resultado == []
