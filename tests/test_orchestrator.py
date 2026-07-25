from aqua_qe_product_manager.orchestrator import product_manager


def test_handle_discovery_delegates_to_workflow(monkeypatch):
    chamada = {}

    def fake_generate_problem_discovery(texto):
        chamada["texto"] = texto
        return "discovery-fake"

    monkeypatch.setattr(
        product_manager, "generate_problem_discovery", fake_generate_problem_discovery
    )

    resultado = product_manager.handle_discovery("entrada")

    assert resultado == "discovery-fake"
    assert chamada["texto"] == "entrada"


def test_handle_vision_delegates_to_workflow(monkeypatch):
    chamada = {}

    def fake_generate_vision_draft(ideia, contexto=None):
        chamada["ideia"] = ideia
        chamada["contexto"] = contexto
        return "vision-fake"

    monkeypatch.setattr(product_manager, "generate_vision_draft", fake_generate_vision_draft)

    resultado = product_manager.handle_vision("uma ideia", {"chave": "valor"})

    assert resultado == "vision-fake"
    assert chamada["ideia"] == "uma ideia"
    assert chamada["contexto"] == {"chave": "valor"}


def test_handle_strategy_delegates_to_workflow(monkeypatch):
    chamada = {}

    def fake_generate_strategy_draft(vision, contexto=None):
        chamada["vision"] = vision
        chamada["contexto"] = contexto
        return "strategy-fake"

    monkeypatch.setattr(
        product_manager, "generate_strategy_draft", fake_generate_strategy_draft
    )

    resultado = product_manager.handle_strategy("vision-aceita")

    assert resultado == "strategy-fake"
    assert chamada["vision"] == "vision-aceita"
    assert chamada["contexto"] is None


def test_handle_prd_delegates_to_workflow(monkeypatch):
    chamada = {}

    def fake_generate_prd_draft(ideia, contexto=None):
        chamada["ideia"] = ideia
        chamada["contexto"] = contexto
        return "prd-fake"

    monkeypatch.setattr(product_manager, "generate_prd_draft", fake_generate_prd_draft)

    resultado = product_manager.handle_prd("uma ideia", {"chave": "valor"})

    assert resultado == "prd-fake"
    assert chamada["ideia"] == "uma ideia"
    assert chamada["contexto"] == {"chave": "valor"}


def test_handle_existing_prd_le_parseia_e_finaliza(monkeypatch):
    chamada = {}

    def fake_read_text_file(caminho):
        chamada["caminho"] = caminho
        return "# PRD"

    def fake_parse_prd_markdown(texto):
        chamada["texto_parseado"] = texto
        return "draft-parseado"

    def fake_finalize_prd(draft):
        chamada["draft_finalizado"] = draft
        return "prd-finalizado"

    monkeypatch.setattr(product_manager, "read_text_file", fake_read_text_file)
    monkeypatch.setattr(product_manager, "parse_prd_markdown", fake_parse_prd_markdown)
    monkeypatch.setattr(product_manager, "finalize_prd", fake_finalize_prd)

    resultado = product_manager.handle_existing_prd("prd.md")

    assert resultado == "prd-finalizado"
    assert chamada["caminho"] == "prd.md"
    assert chamada["texto_parseado"] == "# PRD"
    assert chamada["draft_finalizado"] == "draft-parseado"
