from aqua_qe_product_manager.skills import generate_prd as module


def _fake_complete_json(escopo, fora_de_escopo):
    def fake(prompt, system=""):
        return {
            "contexto_problema": "contexto",
            "objetivo": "objetivo",
            "publico_alvo": "publico",
            "escopo": escopo,
            "fora_de_escopo": fora_de_escopo,
            "requisitos_funcionais": ["req 1"],
            "requisitos_nao_funcionais": ["req nf 1"],
            "criterios_sucesso": ["criterio 1"],
            "riscos_premissas": ["risco 1"],
        }

    return fake


def test_generate_prd_com_escopo_como_string(monkeypatch):
    monkeypatch.setattr(
        module, "complete_json", _fake_complete_json("faz X", "não faz Y")
    )

    draft = module.generate_prd("uma ideia")

    assert draft.scope == "faz X"
    assert draft.out_of_scope == "não faz Y"


def test_generate_prd_com_escopo_como_lista_normaliza_para_string(monkeypatch):
    """O LLM às vezes devolve escopo/fora_de_escopo como lista JSON em vez de string; deve virar texto, nunca repr de lista."""
    monkeypatch.setattr(
        module,
        "complete_json",
        _fake_complete_json(["faz X", "faz Z"], ["não faz Y"]),
    )

    draft = module.generate_prd("uma ideia")

    assert draft.scope == "faz X; faz Z"
    assert draft.out_of_scope == "não faz Y"
    assert "[" not in draft.scope


def test_generate_prd_sem_contexto_ideia_crua(monkeypatch):
    """Compatibilidade: generate_prd(ideia) sem contexto (ou contexto=None) deve continuar
    funcionando exatamente como a geração de PRD a partir de uma ideia crua do
    AQuA-QE Product Owner — o parâmetro contexto é totalmente opcional."""
    monkeypatch.setattr(
        module,
        "complete_json",
        lambda prompt, system="": {
            "contexto_problema": "contexto",
            "objetivo": "objetivo",
            "publico_alvo": "publico",
            "escopo": "escopo",
            "fora_de_escopo": "fora de escopo",
            "requisitos_funcionais": ["req 1"],
            "requisitos_nao_funcionais": ["req nf 1"],
            "criterios_sucesso": ["criterio 1"],
            "riscos_premissas": ["risco 1"],
        },
    )

    draft_sem_argumento = module.generate_prd("uma ideia crua")
    draft_com_none = module.generate_prd("uma ideia crua", None)

    for draft in (draft_sem_argumento, draft_com_none):
        assert draft.context_problem == "contexto"
        assert draft.objective == "objetivo"
        assert draft.scope == "escopo"
        assert draft.functional_requirements == ["req 1"]
        assert draft.success_criteria == ["criterio 1"]


def test_generate_prd_defaults_to_empty_when_llm_omits_fields(monkeypatch):
    monkeypatch.setattr(module, "complete_json", lambda prompt, system="": {})

    draft = module.generate_prd("uma ideia")

    assert draft.objective == ""
    assert draft.functional_requirements == []


def test_generate_prd_aceita_contexto_de_descoberta_visao_estrategia(monkeypatch):
    captured = {}

    def fake_complete_json(prompt, system=""):
        captured["prompt"] = prompt
        return {}

    monkeypatch.setattr(module, "complete_json", fake_complete_json)

    contexto = {"vision_statement": "visao aceita do produto"}
    module.generate_prd("uma ideia", contexto)

    assert "visao aceita do produto" in captured["prompt"]
