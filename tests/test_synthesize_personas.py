from aqua_qe_product_manager.models import Persona
from aqua_qe_product_manager.skills import synthesize_personas as module


def test_synthesize_personas_maps_json_to_models(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {
            "personas": [
                {
                    "nome": "Ana",
                    "descricao": "investidora iniciante",
                    "objetivos": ["investir com seguranca"],
                    "pontos_de_dor": ["falta de conhecimento"],
                    "trecho_fonte": "trecho 1",
                }
            ]
        },
    )

    resultado = module.synthesize_personas("texto qualquer")

    assert resultado == [
        Persona(
            name="Ana",
            description="investidora iniciante",
            goals=["investir com seguranca"],
            pain_points=["falta de conhecimento"],
            source_reference="trecho 1",
        )
    ]


def test_synthesize_personas_returns_empty_list_when_none_described(monkeypatch):
    monkeypatch.setattr(module, "complete_json", lambda prompt, system="": {"personas": []})

    resultado = module.synthesize_personas("texto sem personas")

    assert resultado == []
