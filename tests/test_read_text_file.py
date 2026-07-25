from aqua_qe_product_manager.skills.read_text_file import read_text_file


def test_read_text_file_returns_full_content(tmp_path):
    caminho = tmp_path / "entrada.txt"
    caminho.write_text("conteudo de teste\nsegunda linha", encoding="utf-8")

    resultado = read_text_file(str(caminho))

    assert resultado == "conteudo de teste\nsegunda linha"


def test_read_text_file_handles_utf8_accented_characters(tmp_path):
    caminho = tmp_path / "entrada.md"
    caminho.write_text("visão, estratégia, público-alvo", encoding="utf-8")

    resultado = read_text_file(str(caminho))

    assert resultado == "visão, estratégia, público-alvo"
