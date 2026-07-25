import re

from ..services.confluence_service import update_page


def update_confluence_page(pagina: str, texto: str) -> None:
    """Atualiza uma página existente no Confluence Cloud (aceita a URL completa ou apenas o ID) a partir de um texto Markdown já formatado (PRD, visão ou estratégia)."""
    match = re.search(r"/pages/(\d+)", pagina)
    page_id = match.group(1) if match else pagina
    update_page(page_id, texto)
