import os

from ..services.confluence_service import create_page


def create_confluence_page(texto: str, titulo: str) -> str:
    """Publica um texto Markdown já formatado (PRD, visão ou estratégia) como página nova no Confluence Cloud e retorna a URL da página criada."""
    space_key = os.environ["CONFLUENCE_SPACE_KEY"]
    base_url = os.environ["JIRA_BASE_URL"].rstrip("/")

    page_id = create_page(space_key, titulo, texto)
    return f"{base_url}/wiki/pages/viewpage.action?pageId={page_id}"
