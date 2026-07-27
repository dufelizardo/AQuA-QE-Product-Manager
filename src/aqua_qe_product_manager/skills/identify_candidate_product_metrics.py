from ..services.llm_service import complete_json

_SYSTEM = (
    "Você sugere métricas de produto comumente usadas para acompanhar a "
    "saúde de um produto do tipo descrito no texto (ex.: MAU, DAU, tempo "
    "médio para completar uma ação-chave, taxa de abandono/cancelamento). "
    "Estas são SUGESTÕES de mercado a confirmar pelo Product Manager "
    "humano — nunca afirme que a métrica já foi definida, medida ou "
    "aceita para este produto. Nunca invente um número/meta para a "
    "métrica; sugira só o nome da métrica."
)


def identify_candidate_product_metrics(texto: str) -> list[str]:
    """Sugere métricas de produto típicas para o domínio descrito — sempre como recomendação a confirmar, nunca como fato (distinto de success_criteria, que exige evidência textual)."""
    prompt = (
        f"Texto:\n{texto}\n\n"
        'Responda apenas em JSON: {"metricas_candidatas": ["..."]}'
    )
    dados = complete_json(prompt, system=_SYSTEM)
    return dados.get("metricas_candidatas", [])
