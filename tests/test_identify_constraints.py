from aqua_qe_product_manager.skills import identify_constraints as module


def test_identify_constraints_maps_json_to_list(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {"restricoes": ["Orcamento limitado"]},
    )

    resultado = module.identify_constraints("texto qualquer")

    assert resultado == ["Orcamento limitado"]


def test_identify_constraints_returns_empty_list_when_none_identified(monkeypatch):
    monkeypatch.setattr(module, "complete_json", lambda prompt, system="": {"restricoes": []})

    resultado = module.identify_constraints("texto sem restricao")

    assert resultado == []
