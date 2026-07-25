from aqua_qe_product_manager.models import PrioritizedRequirement
from aqua_qe_product_manager.skills import classify_moscow as module


def test_classify_moscow_maps_json_to_models(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {
            "classificacoes": [
                {
                    "requisito": "Login com CPF",
                    "categoria": "must",
                    "justificativa": "texto diz 'essencial para o lançamento'",
                },
                {"requisito": "Tema escuro", "categoria": "", "justificativa": ""},
            ]
        },
    )

    resultado = module.classify_moscow(["Login com CPF", "Tema escuro"], "texto do PRD")

    assert resultado == [
        PrioritizedRequirement(
            requirement="Login com CPF",
            moscow="must",
            moscow_justification="texto diz 'essencial para o lançamento'",
        ),
        PrioritizedRequirement(requirement="Tema escuro", moscow="", moscow_justification=""),
    ]


def test_classify_moscow_lowercases_category(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {
            "classificacoes": [{"requisito": "X", "categoria": "MUST", "justificativa": "y"}]
        },
    )

    resultado = module.classify_moscow(["X"], "texto")

    assert resultado[0].moscow == "must"


def test_classify_moscow_returns_empty_list_when_none_returned(monkeypatch):
    monkeypatch.setattr(module, "complete_json", lambda prompt, system="": {"classificacoes": []})

    resultado = module.classify_moscow(["X"], "texto")

    assert resultado == []


def test_classify_moscow_prompt_instrui_a_nunca_inventar_categoria(monkeypatch):
    capturado = {}

    def fake_complete_json(prompt, system=""):
        capturado["system"] = system
        return {"classificacoes": []}

    monkeypatch.setattr(module, "complete_json", fake_complete_json)

    module.classify_moscow(["X"], "texto")

    assert "nunca" in capturado["system"].lower()
    assert "invente" in capturado["system"].lower()
