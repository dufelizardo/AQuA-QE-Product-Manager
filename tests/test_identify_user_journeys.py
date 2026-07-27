from aqua_qe_product_manager.models import UserJourney
from aqua_qe_product_manager.skills import identify_user_journeys as module


def test_identify_user_journeys_maps_json_to_models(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {
            "jornadas": [
                {
                    "nome": "Agendamento",
                    "passos": ["Cadastro", "Escolhe unidade", "Agenda consulta"],
                    "trecho_fonte": "trecho 1",
                }
            ]
        },
    )

    resultado = module.identify_user_journeys("texto qualquer")

    assert resultado == [
        UserJourney(
            name="Agendamento",
            steps=["Cadastro", "Escolhe unidade", "Agenda consulta"],
            source_reference="trecho 1",
        )
    ]


def test_identify_user_journeys_returns_empty_list_when_no_flow_described(monkeypatch):
    monkeypatch.setattr(module, "complete_json", lambda prompt, system="": {"jornadas": []})

    resultado = module.identify_user_journeys("texto sem jornada")

    assert resultado == []
