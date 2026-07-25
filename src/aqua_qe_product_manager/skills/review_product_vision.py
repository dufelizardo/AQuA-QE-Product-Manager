import os

from ..models import ProductVision
from ..services.llm_service import complete_json

_SYSTEM = (
    "Você é um revisor crítico de visões de produto, independente de quem "
    "as gerou. Avalie se o statement é claro, se o público-alvo é "
    "específico e se os diferenciais/métrica norte são coerentes com eles. "
    "Aponte problemas reais; nunca aprove uma visão vaga ou uma métrica "
    "sem relação clara com o statement."
)

_DEFAULT_REVIEW_MODEL = "phi4"


def review_product_vision(vision: ProductVision) -> dict:
    """Revisa a visão de produto com um LLM diferente do gerador, apontando problemas de clareza e coerência."""
    modelo = os.getenv("OLLAMA_REVIEW_MODEL", _DEFAULT_REVIEW_MODEL)
    prompt = (
        f"Statement: {vision.statement}\n"
        f"Público-alvo: {vision.target_audience}\n"
        f"Diferenciais: {vision.differentiators}\n"
        f"Métrica norte: {vision.north_star_metric}\n\n"
        'Responda apenas em JSON: {"aprovado": true ou false, "problemas": ["..."]}'
    )
    dados = complete_json(prompt, system=_SYSTEM, model=modelo)
    return {
        "aprovado": bool(dados.get("aprovado", False)),
        "problemas": dados.get("problemas", []),
    }
