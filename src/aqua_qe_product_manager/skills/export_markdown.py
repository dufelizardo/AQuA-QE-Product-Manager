def export_markdown(texto: str, caminho: str) -> None:
    """Exporta um texto Markdown (PRD, visão ou estratégia formatados) para o caminho informado."""
    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write(texto)
