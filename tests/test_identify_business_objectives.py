from aqua_qe_product_manager.models import BusinessObjective
from aqua_qe_product_manager.skills import identify_business_objectives as module


def test_identify_business_objectives_maps_json_to_models(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {
            "objetivos": [{"objetivo": "Reduzir fila", "kpi": "30% de reducao"}]
        },
    )

    resultado = module.identify_business_objectives(
        "Reduzir fila em 30%", ["Redução na fila (30%)"]
    )

    assert resultado == [BusinessObjective(objective="Reduzir fila", kpi="30% de reducao")]


def test_identify_business_objectives_returns_empty_list_when_no_kpi_clear(monkeypatch):
    monkeypatch.setattr(module, "complete_json", lambda prompt, system="": {"objetivos": []})

    resultado = module.identify_business_objectives("objetivo vago", [])

    assert resultado == []
