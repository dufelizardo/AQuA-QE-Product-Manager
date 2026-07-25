import os

from ..models import ProductStrategy
from ..services.llm_service import complete_json

_SYSTEM = (
    "Você é um revisor crítico de estratégias de produto, independente de "
    "quem as gerou. Avalie se as metas são específicas, mensuráveis e "
    "coerentes com a visão de produto que as originou. Aponte problemas "
    "reais; nunca aprove uma meta vaga ou uma métrica sem relação clara "
    "com a visão."
)

_DEFAULT_REVIEW_MODEL = "phi4"


def review_product_strategy(strategy: ProductStrategy) -> dict:
    """Revisa a estratégia de produto com um LLM diferente do gerador, apontando problemas de clareza e coerência."""
    modelo = os.getenv("OLLAMA_REVIEW_MODEL", _DEFAULT_REVIEW_MODEL)
    prompt = (
        f"Metas: {strategy.goals}\n"
        f"Temas de roadmap: {strategy.roadmap_themes}\n"
        f"Horizonte de tempo: {strategy.time_horizon}\n\n"
        'Responda apenas em JSON: {"aprovado": true ou false, "problemas": ["..."]}'
    )
    dados = complete_json(prompt, system=_SYSTEM, model=modelo)
    return {
        "aprovado": bool(dados.get("aprovado", False)),
        "problemas": dados.get("problemas", []),
    }
