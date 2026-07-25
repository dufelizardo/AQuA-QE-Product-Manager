from ..models import ProductStrategy, ProductVision, StrategicGoal
from ..services.llm_service import complete_json

_SYSTEM = (
    "Você escreve a estratégia de produto (metas, temas de roadmap, "
    "horizonte de tempo) a partir de uma visão de produto já aceita e, "
    "opcionalmente, de contexto adicional. Cada meta deve ser coerente com "
    "o público-alvo e os diferenciais da visão. Baseie-se apenas na visão "
    "e no contexto informados; nunca invente uma métrica-alvo, prazo ou "
    "projeção que não decorra diretamente deles — deixe esses campos "
    "vazios quando não sustentados. Responda sempre em português."
)


def generate_product_strategy(
    vision: ProductVision, contexto: dict | None = None
) -> ProductStrategy:
    """Gera a estratégia de produto a partir da visão já aceita."""
    contexto = contexto or {}
    prompt = (
        f"Visão aceita — statement: {vision.statement}\n"
        f"Público-alvo: {vision.target_audience}\n"
        f"Diferenciais: {vision.differentiators}\n"
        f"Métrica norte: {vision.north_star_metric}\n\n"
        f"Contexto adicional (pode estar vazio): {contexto}\n\n"
        "Escreva a estratégia de produto com os seguintes campos:\n"
        "- metas: lista de metas, cada uma com descricao, metrica, alvo e prazo "
        "(alvo/prazo vazios se não houver base)\n"
        "- temas_roadmap: lista de temas de investimento de alto nível\n"
        "- horizonte_tempo: período que a estratégia cobre\n\n"
        'Responda apenas em JSON: {"metas": [{"descricao": "...", "metrica": "...", '
        '"alvo": "...", "prazo": "..."}], "temas_roadmap": ["..."], "horizonte_tempo": "..."}'
    )
    dados = complete_json(prompt, system=_SYSTEM)
    metas = [
        StrategicGoal(
            description=item.get("descricao") or "",
            metric=item.get("metrica") or "",
            target=item.get("alvo") or "",
            timeframe=item.get("prazo") or "",
        )
        for item in dados.get("metas", [])
    ]
    return ProductStrategy(
        goals=metas,
        roadmap_themes=dados.get("temas_roadmap") or [],
        time_horizon=dados.get("horizonte_tempo") or "",
    )
