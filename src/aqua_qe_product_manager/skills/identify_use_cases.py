from ..services.llm_service import complete_json

_SYSTEM = (
    "Você identifica casos de uso de alto nível (ator + ação, ex.: "
    "'Paciente agenda consulta') a partir de um texto de requisitos. Só "
    "responda com casos de uso literalmente sustentados pelo escopo/"
    "requisitos descritos — nunca invente um ator ou ação que não "
    "decorra diretamente do texto. Se não houver caso de uso "
    "identificável, responda com uma lista vazia."
)


def identify_use_cases(texto: str) -> list[str]:
    """Identifica casos de uso (ator + ação) sustentados pelo texto de entrada (nunca inventados)."""
    prompt = f"Texto:\n{texto}\n\n" 'Responda apenas em JSON: {"casos_de_uso": ["..."]}'
    dados = complete_json(prompt, system=_SYSTEM)
    return dados.get("casos_de_uso", [])
