from ..services.llm_service import complete_json

_SYSTEM = (
    "Você identifica premissas técnicas (condições que se assume "
    "verdadeiras para a solução funcionar, ex.: infraestrutura "
    "disponível, equipamento existente, equipe treinada) citadas ou "
    "claramente implícitas num texto de requisitos. Nunca invente uma "
    "premissa que não decorra diretamente do texto — se não houver "
    "premissa identificável, responda com uma lista vazia."
)


def identify_technical_assumptions(texto: str) -> list[str]:
    """Identifica premissas técnicas citadas/implícitas no texto de entrada (nunca inventadas)."""
    prompt = f"Texto:\n{texto}\n\n" 'Responda apenas em JSON: {"premissas": ["..."]}'
    dados = complete_json(prompt, system=_SYSTEM)
    return dados.get("premissas", [])
