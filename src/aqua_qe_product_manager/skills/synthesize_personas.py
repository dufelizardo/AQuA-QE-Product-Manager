from ..models import Persona
from ..services.llm_service import complete_json

_SYSTEM = (
    "Você sintetiza personas a partir de um texto de entrada. Só responda "
    "com personas literalmente sustentadas pelo texto. Nunca adicione uma "
    "persona 'típica' do domínio que não esteja descrita nele — se o texto "
    "não descrever nenhuma persona, responda com uma lista vazia."
)


def synthesize_personas(texto: str) -> list[Persona]:
    """Sintetiza personas a partir do texto de entrada, conforme knowledge/templates/persona.md."""
    prompt = (
        f"Texto:\n{texto}\n\n"
        "Identifique as personas descritas no texto.\n"
        'Responda apenas em JSON: {"personas": [{"nome": "...", "descricao": "...", '
        '"objetivos": ["..."], "pontos_de_dor": ["..."], "trecho_fonte": "..."}]}'
    )
    dados = complete_json(prompt, system=_SYSTEM)
    return [
        Persona(
            name=item.get("nome") or "",
            description=item.get("descricao") or "",
            goals=item.get("objetivos") or [],
            pain_points=item.get("pontos_de_dor") or [],
            source_reference=item.get("trecho_fonte") or "",
        )
        for item in dados.get("personas", [])
    ]
