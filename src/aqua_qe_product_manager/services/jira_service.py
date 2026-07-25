import os

import httpx


def _credenciais() -> tuple[str, str, str]:
    base_url = os.environ["JIRA_BASE_URL"].rstrip("/")
    email = os.environ["JIRA_EMAIL"]
    token = os.environ["JIRA_API_TOKEN"]
    return base_url, email, token


def _adf_para_texto(node: dict | None) -> str:
    """Extrai texto simples de um nó no formato Atlassian Document Format (ADF)."""
    if not node:
        return ""
    if node.get("type") == "text":
        return node.get("text", "")

    partes = [_adf_para_texto(filho) for filho in node.get("content", [])]
    texto = " ".join(parte for parte in partes if parte)
    if node.get("type") in ("paragraph", "heading"):
        return texto + "\n"
    return texto


def get_issue_text(issue_key: str) -> str:
    """Busca um ticket no Jira Cloud e retorna resumo + descrição como texto simples."""
    base_url, email, token = _credenciais()

    resposta = httpx.get(
        f"{base_url}/rest/api/3/issue/{issue_key}",
        auth=(email, token),
        params={"fields": "summary,description"},
        timeout=30,
    )
    resposta.raise_for_status()
    campos = resposta.json()["fields"]

    resumo = campos.get("summary", "")
    descricao = _adf_para_texto(campos.get("description"))
    return f"{resumo}\n\n{descricao}".strip()
