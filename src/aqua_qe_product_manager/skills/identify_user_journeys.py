from ..models import UserJourney
from ..services.llm_service import complete_json

_SYSTEM = (
    "Você identifica jornadas de usuário (passo a passo de como uma "
    "persona interage com o produto do início ao fim de um fluxo "
    "relevante) a partir de um texto de requisitos. Só responda com "
    "jornadas e passos literalmente sustentados pelo texto — nunca invente "
    "um passo que não decorra diretamente do escopo/requisitos descritos. "
    "Se não houver fluxo identificável, responda com uma lista vazia."
)


def identify_user_journeys(texto: str) -> list[UserJourney]:
    """Identifica jornadas de usuário sustentadas pelo texto de entrada (lista vazia se não houver base)."""
    prompt = (
        f"Texto:\n{texto}\n\n"
        'Responda apenas em JSON: {"jornadas": [{"nome": "...", '
        '"passos": ["..."], "trecho_fonte": "..."}]}'
    )
    dados = complete_json(prompt, system=_SYSTEM)
    return [
        UserJourney(
            name=item.get("nome", ""),
            steps=item.get("passos", []),
            source_reference=item.get("trecho_fonte", ""),
        )
        for item in dados.get("jornadas", [])
    ]
