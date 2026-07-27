from aqua_qe_product_manager.skills import identify_candidate_product_metrics as module


def test_identify_candidate_product_metrics_maps_json_to_list(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {"metricas_candidatas": ["MAU", "Taxa de abandono"]},
    )

    resultado = module.identify_candidate_product_metrics("texto qualquer")

    assert resultado == ["MAU", "Taxa de abandono"]


def test_identify_candidate_product_metrics_returns_empty_list(monkeypatch):
    monkeypatch.setattr(
        module, "complete_json", lambda prompt, system="": {"metricas_candidatas": []}
    )

    resultado = module.identify_candidate_product_metrics("texto qualquer")

    assert resultado == []
