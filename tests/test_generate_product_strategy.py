from aqua_qe_product_manager.models import ProductVision, StrategicGoal
from aqua_qe_product_manager.skills import generate_product_strategy as module


def _vision_aceita() -> ProductVision:
    return ProductVision(
        statement="ser a forma mais simples de investir em CDB",
        target_audience="investidores iniciantes",
        differentiators=["simplicidade"],
        north_star_metric="volume investido por usuario ativo",
    )


def test_generate_product_strategy_maps_json_to_model(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {
            "metas": [
                {
                    "descricao": "aumentar volume investido",
                    "metrica": "volume investido",
                    "alvo": "R$ 10 milhoes",
                    "prazo": "12 meses",
                }
            ],
            "temas_roadmap": ["onboarding simplificado"],
            "horizonte_tempo": "1 ano",
        },
    )

    strategy = module.generate_product_strategy(_vision_aceita())

    assert strategy.goals == [
        StrategicGoal(
            description="aumentar volume investido",
            metric="volume investido",
            target="R$ 10 milhoes",
            timeframe="12 meses",
        )
    ]
    assert strategy.roadmap_themes == ["onboarding simplificado"]
    assert strategy.time_horizon == "1 ano"


def test_generate_product_strategy_defaults_to_empty_when_llm_omits_fields(monkeypatch):
    monkeypatch.setattr(module, "complete_json", lambda prompt, system="": {})

    strategy = module.generate_product_strategy(_vision_aceita())

    assert strategy.goals == []
    assert strategy.roadmap_themes == []
    assert strategy.time_horizon == ""


def test_generate_product_strategy_prompt_inclui_dados_da_visao(monkeypatch):
    captured = {}

    def fake_complete_json(prompt, system=""):
        captured["prompt"] = prompt
        return {}

    monkeypatch.setattr(module, "complete_json", fake_complete_json)

    module.generate_product_strategy(_vision_aceita())

    assert "ser a forma mais simples de investir em CDB" in captured["prompt"]
    assert "investidores iniciantes" in captured["prompt"]
