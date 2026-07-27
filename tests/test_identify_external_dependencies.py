from aqua_qe_product_manager.skills import identify_external_dependencies as module


def test_identify_external_dependencies_maps_json_to_list(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {"dependencias": ["SUS", "CNES"]},
    )

    resultado = module.identify_external_dependencies("texto qualquer")

    assert resultado == ["SUS", "CNES"]


def test_identify_external_dependencies_returns_empty_list_when_none_identified(monkeypatch):
    monkeypatch.setattr(module, "complete_json", lambda prompt, system="": {"dependencias": []})

    resultado = module.identify_external_dependencies("texto sem dependencia")

    assert resultado == []
