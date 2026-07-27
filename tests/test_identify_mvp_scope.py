from aqua_qe_product_manager.skills import identify_mvp_scope as module


def test_identify_mvp_scope_splits_requirements_into_mvp_and_future(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {
            "mvp": ["Cadastro", "Agendamento"],
            "versao_futura": ["Notificacoes"],
        },
    )

    mvp, futuro = module.identify_mvp_scope(
        ["Cadastro", "Agendamento", "Notificacoes"], "texto qualquer"
    )

    assert mvp == ["Cadastro", "Agendamento"]
    assert futuro == ["Notificacoes"]


def test_identify_mvp_scope_defaults_to_all_mvp_when_no_signal(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {"mvp": ["Cadastro"], "versao_futura": []},
    )

    mvp, futuro = module.identify_mvp_scope(["Cadastro"], "texto sem sinal de fase")

    assert mvp == ["Cadastro"]
    assert futuro == []
