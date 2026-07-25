from aqua_qe_product_manager.skills import identify_problem_statement as module


def test_identify_problem_statement_maps_json_to_model(monkeypatch):
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {
            "problema": "clientes nao conseguem agendar consulta",
            "usuarios_afetados": "pacientes",
            "impacto": "perda de receita",
            "evidencia": "reclamacoes no suporte",
            "trecho_fonte": "trecho do texto",
        },
    )

    resultado = module.identify_problem_statement("texto qualquer")

    assert resultado.problem == "clientes nao conseguem agendar consulta"
    assert resultado.affected_users == "pacientes"
    assert resultado.impact == "perda de receita"
    assert resultado.evidence == "reclamacoes no suporte"
    assert resultado.source_reference == "trecho do texto"


def test_identify_problem_statement_defaults_to_empty_when_llm_omits_fields(monkeypatch):
    monkeypatch.setattr(module, "complete_json", lambda prompt, system="": {})

    resultado = module.identify_problem_statement("texto qualquer")

    assert resultado.problem == ""
    assert resultado.affected_users == ""
    assert resultado.impact == ""
    assert resultado.evidence == ""
    assert resultado.source_reference == ""
