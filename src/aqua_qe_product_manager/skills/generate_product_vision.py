from ..models import ProductVision
from ..services.llm_service import complete_json

_SYSTEM = (
    "Você escreve a visão de produto (statement, público-alvo, "
    "diferenciais, métrica norte) a partir de uma ideia e, opcionalmente, "
    "do contexto de descoberta já sintetizado (problema, personas, "
    "mercado). Baseie-se apenas na ideia e no contexto informados; nunca "
    "invente uma métrica-alvo ou diferencial que não decorra diretamente "
    "deles. Quando a métrica norte não puder ser sustentada, deixe-a "
    "vazia — não preencha com uma métrica genérica 'comum do setor'. "
    "Responda sempre em português, mesmo que a ideia esteja em outro idioma."
)


def generate_product_vision(ideia: str, contexto: dict | None = None) -> ProductVision:
    """Gera a visão de produto a partir de uma ideia e do contexto de descoberta, quando disponível."""
    contexto = contexto or {}
    prompt = (
        f"Ideia:\n{ideia}\n\n"
        f"Contexto de descoberta (pode estar vazio): {contexto}\n\n"
        "Escreva a visão de produto com os seguintes campos:\n"
        "- statement: a visão em uma frase\n"
        "- publico_alvo: público-alvo da visão\n"
        "- diferenciais: lista de diferenciais\n"
        "- metrica_norte: métrica que melhor representa o valor entregue, "
        "vazia se não houver base na ideia/contexto\n\n"
        'Responda apenas em JSON: {"statement": "...", "publico_alvo": "...", '
        '"diferenciais": ["..."], "metrica_norte": "..."}'
    )
    dados = complete_json(prompt, system=_SYSTEM)
    return ProductVision(
        statement=dados.get("statement") or "",
        target_audience=dados.get("publico_alvo") or "",
        differentiators=dados.get("diferenciais") or [],
        north_star_metric=dados.get("metrica_norte") or "",
    )
