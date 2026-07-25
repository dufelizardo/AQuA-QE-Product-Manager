from aqua_qe_product_manager.models import Competitor
from aqua_qe_product_manager.skills import extract_market_context as module


def test_extract_market_context_prompt_proibe_inventar_concorrente():
    """Regressão GR-M1 (docs/agent/guardrails.md): extract_market_context nunca pode preencher
    concorrentes/tendências com conhecimento geral do modelo — só o que estiver literalmente
    citado no texto de entrada. Este é o guardrail mais importante deste agente."""
    system = module._SYSTEM.lower()

    assert "nunca" in system
    assert "concorrente" in system
    assert "conhecimento geral" in system or "não esteja citado" in module._SYSTEM


def test_extract_market_context_maps_json_to_model_with_one_competitor(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {
            "concorrentes": [
                {
                    "nome": "Concorrente X",
                    "pontos_fortes": ["marca forte"],
                    "pontos_fracos": ["app lento"],
                    "trecho_fonte": "citado no texto",
                }
            ],
            "tendencias": ["consolidacao do setor"],
            "contexto_mercado": "mercado em crescimento",
        },
    )

    resultado = module.extract_market_context("texto qualquer")

    assert resultado.competitors == [
        Competitor(
            name="Concorrente X",
            strengths=["marca forte"],
            weaknesses=["app lento"],
            source_reference="citado no texto",
        )
    ]
    assert resultado.trends == ["consolidacao do setor"]
    assert resultado.market_context == "mercado em crescimento"


def test_extract_market_context_returns_empty_when_source_has_no_competitors(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {
            "concorrentes": [],
            "tendencias": [],
            "contexto_mercado": "",
        },
    )

    resultado = module.extract_market_context("texto sem concorrentes citados")

    assert resultado.competitors == []
    assert resultado.trends == []
    assert resultado.market_context == ""
