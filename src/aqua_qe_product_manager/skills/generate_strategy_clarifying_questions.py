from ..models import ProductStrategy
from ..services.llm_service import complete_json

_SYSTEM = (
    "Você transforma apontamentos de revisão de uma estratégia de produto "
    "em perguntas diretas e acionáveis para quem propôs a ideia responder. "
    "Cada pergunta deve buscar exatamente a informação que falta para "
    "resolver um apontamento, sem repetir a crítica literalmente."
)


def generate_strategy_clarifying_questions(strategy: ProductStrategy) -> list[str]:
    """Gera perguntas de esclarecimento a partir dos apontamentos da revisão da estratégia."""
    if not strategy.review_notes:
        return []

    prompt = (
        f"Metas: {strategy.goals}\n\n"
        f"Apontamentos do revisor: {strategy.review_notes}\n\n"
        "Para cada apontamento, gere uma pergunta direta que obtenha a "
        "informação necessária para resolvê-lo.\n"
        'Responda apenas em JSON: {"perguntas": ["...", "..."]}'
    )
    dados = complete_json(prompt, system=_SYSTEM)
    return [str(pergunta) for pergunta in dados.get("perguntas", [])]
