from aqua_qe_product_manager.models import JobToBeDone
from aqua_qe_product_manager.skills import extract_jobs_to_be_done as module


def test_extract_jobs_to_be_done_maps_json_to_models(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {
            "jobs": [
                {
                    "situacao": "quando preciso investir uma sobra de caixa",
                    "motivacao": "quero rentabilizar sem risco",
                    "resultado_esperado": "ter o dinheiro disponivel quando precisar",
                    "trecho_fonte": "trecho 1",
                }
            ]
        },
    )

    resultado = module.extract_jobs_to_be_done("texto qualquer")

    assert resultado == [
        JobToBeDone(
            situation="quando preciso investir uma sobra de caixa",
            motivation="quero rentabilizar sem risco",
            expected_outcome="ter o dinheiro disponivel quando precisar",
            source_reference="trecho 1",
        )
    ]


def test_extract_jobs_to_be_done_returns_empty_list_when_none_found(monkeypatch):
    monkeypatch.setattr(module, "complete_json", lambda prompt, system="": {"jobs": []})

    resultado = module.extract_jobs_to_be_done("texto sem jobs")

    assert resultado == []
