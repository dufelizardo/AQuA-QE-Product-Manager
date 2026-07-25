from aqua_qe_product_manager.skills.export_markdown import export_markdown


def test_export_markdown_writes_text_to_file(tmp_path):
    caminho = tmp_path / "prd.md"

    export_markdown("# PRD\n\nconteudo", str(caminho))

    assert caminho.read_text(encoding="utf-8") == "# PRD\n\nconteudo"


def test_export_markdown_overwrites_existing_file(tmp_path):
    caminho = tmp_path / "prd.md"
    caminho.write_text("conteudo antigo", encoding="utf-8")

    export_markdown("conteudo novo", str(caminho))

    assert caminho.read_text(encoding="utf-8") == "conteudo novo"
