from aqua_qe_product_manager.skills import identify_use_cases as module


def test_identify_use_cases_maps_json_to_list(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {"casos_de_uso": ["Paciente agenda consulta"]},
    )

    resultado = module.identify_use_cases("texto qualquer")

    assert resultado == ["Paciente agenda consulta"]


def test_identify_use_cases_returns_empty_list_when_none_identified(monkeypatch):
    monkeypatch.setattr(module, "complete_json", lambda prompt, system="": {"casos_de_uso": []})

    resultado = module.identify_use_cases("texto sem caso de uso")

    assert resultado == []
