from ..services.llm_service import complete_json

_SYSTEM = (
    "Você identifica dependências de sistemas externos (ex.: sistemas "
    "governamentais, meios de autenticação, notificação, pagamento) "
    "citados ou claramente inferíveis a partir de um texto de requisitos. "
    "Nunca assuma uma dependência que não tenha evidência no texto — se "
    "não houver dependência externa clara, responda com uma lista vazia."
)


def identify_external_dependencies(texto: str) -> list[str]:
    """Identifica dependências de sistemas externos citadas/inferíveis no texto (nunca assumidas sem evidência)."""
    prompt = (
        f"Texto:\n{texto}\n\n"
        'Responda apenas em JSON: {"dependencias": ["..."]}'
    )
    dados = complete_json(prompt, system=_SYSTEM)
    return dados.get("dependencias", [])
