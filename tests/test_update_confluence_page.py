from aqua_qe_product_manager.skills import update_confluence_page as module


def test_extracts_page_id_from_full_url(monkeypatch):
    captured = {}

    def fake_update_page(page_id, texto):
        captured.update(page_id=page_id, texto=texto)

    monkeypatch.setattr(module, "update_page", fake_update_page)

    url = (
        "https://edufelizardo.atlassian.net/wiki/spaces/~70121c6abcd6/"
        "pages/163841/Sistema+de+Agendamento"
    )
    module.update_confluence_page(url, "texto atualizado")

    assert captured["page_id"] == "163841"
    assert captured["texto"] == "texto atualizado"


def test_accepts_plain_page_id(monkeypatch):
    captured = {}
    monkeypatch.setattr(
        module,
        "update_page",
        lambda page_id, texto: captured.update(page_id=page_id, texto=texto),
    )

    module.update_confluence_page("163841", "texto atualizado")

    assert captured["page_id"] == "163841"
