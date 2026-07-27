from aqua_qe_product_manager.models import GlossaryTerm
from aqua_qe_product_manager.skills import identify_prd_glossary as module


def test_identify_prd_glossary_maps_json_to_models(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {
            "termos": [{"termo": "Unidade", "definicao": "Unidade de saude municipal"}]
        },
    )

    resultado = module.identify_prd_glossary("texto qualquer")

    assert resultado == [GlossaryTerm(term="Unidade", definition="Unidade de saude municipal")]


def test_identify_prd_glossary_returns_empty_list_when_no_term_relevant(monkeypatch):
    monkeypatch.setattr(module, "complete_json", lambda prompt, system="": {"termos": []})

    resultado = module.identify_prd_glossary("texto sem termo")

    assert resultado == []
