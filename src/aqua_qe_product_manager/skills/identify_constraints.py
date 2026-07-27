from ..services.llm_service import complete_json

_SYSTEM = (
    "Você identifica restrições do projeto (ex.: orçamento, prazo, "
    "infraestrutura disponível, legislação aplicável) citadas ou "
    "claramente implícitas num texto de requisitos. Nunca invente uma "
    "restrição que não decorra diretamente do texto — se não houver "
    "restrição identificável, responda com uma lista vazia."
)


def identify_constraints(texto: str) -> list[str]:
    """Identifica restrições do projeto citadas/implícitas no texto de entrada (nunca inventadas)."""
    prompt = f"Texto:\n{texto}\n\n" 'Responda apenas em JSON: {"restricoes": ["..."]}'
    dados = complete_json(prompt, system=_SYSTEM)
    return dados.get("restricoes", [])
