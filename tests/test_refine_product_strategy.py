from aqua_qe_product_manager.models import ProductStrategy, StrategicGoal
from aqua_qe_product_manager.skills import refine_product_strategy as module


def _strategy() -> ProductStrategy:
    return ProductStrategy(
        goals=[StrategicGoal(description="meta antiga", metric="metrica antiga")],
        roadmap_themes=["tema antigo"],
        time_horizon="6 meses",
    )


def test_refine_product_strategy_rewrites_fields_from_answers(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {
            "metas": [
                {
                    "descricao": "meta nova",
                    "metrica": "metrica nova",
                    "alvo": "R$ 10 milhoes",
                    "prazo": "12 meses",
                }
            ],
            "temas_roadmap": ["tema novo"],
            "horizonte_tempo": "12 meses",
        },
    )

    strategy = module.refine_product_strategy(
        _strategy(), [{"pergunta": "qual o alvo da meta?", "resposta": "R$ 10 milhoes"}]
    )

    assert strategy.goals == [
        StrategicGoal(
            description="meta nova",
            metric="metrica nova",
            target="R$ 10 milhoes",
            timeframe="12 meses",
        )
    ]
    assert strategy.roadmap_themes == ["tema novo"]
    assert strategy.time_horizon == "12 meses"


def test_refine_product_strategy_preserves_fields_not_addressed_by_answers(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {"horizonte_tempo": "12 meses"},
    )

    strategy = module.refine_product_strategy(
        _strategy(), [{"pergunta": "qual o horizonte?", "resposta": "12 meses"}]
    )

    assert strategy.time_horizon == "12 meses"
    assert strategy.goals == [StrategicGoal(description="meta antiga", metric="metrica antiga")]
    assert strategy.roadmap_themes == ["tema antigo"]


def test_refine_product_strategy_prompt_instrui_a_preservar_detalhe_de_campos_nao_perguntados(
    monkeypatch,
):
    """Regressão análoga ao PRD/visão: refine_product_strategy reescreve a estratégia inteira a
    cada rodada — sem instrução explícita, o LLM tende a simplificar campos não relacionados
    às respostas daquela rodada."""
    captured = {}

    def fake_complete_json(prompt, system=""):
        captured["prompt"] = prompt
        captured["system"] = system
        return {}

    monkeypatch.setattr(module, "complete_json", fake_complete_json)

    module.refine_product_strategy(_strategy(), [{"pergunta": "p", "resposta": "r"}])

    assert "preserv" in captured["system"].lower() or "preserv" in captured["prompt"].lower()
