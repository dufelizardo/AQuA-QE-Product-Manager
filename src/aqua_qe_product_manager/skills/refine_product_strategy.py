from ..models import ProductStrategy, StrategicGoal
from ..services.llm_service import complete_json

_SYSTEM = (
    "Você refina uma estratégia de produto existente com base nas "
    "respostas que quem propôs a ideia deu às perguntas de esclarecimento "
    "levantadas por um revisor. Baseie-se apenas na estratégia atual e nas "
    "respostas fornecidas; nunca invente meta, métrica ou prazo que não "
    "tenha sido informado neles. Nunca remova ou resuma um detalhe que já "
    "existe em um campo atual, a menos que uma resposta contradiga esse "
    "detalhe especificamente — preserve o texto existente nos campos que "
    "as respostas não abordam. Responda sempre em português."
)


def refine_product_strategy(
    strategy: ProductStrategy, respostas: list[dict]
) -> ProductStrategy:
    """Reescreve os campos da estratégia usando as respostas às perguntas de esclarecimento, preservando o que não foi perguntado."""
    perguntas_respostas = [
        f"P: {item['pergunta']}\nR: {item['resposta']}" for item in respostas
    ]

    prompt = (
        f"Metas atuais: {strategy.goals}\n"
        f"Temas de roadmap atuais: {strategy.roadmap_themes}\n"
        f"Horizonte de tempo atual: {strategy.time_horizon}\n\n"
        "Respostas às perguntas de esclarecimento:\n"
        + "\n".join(perguntas_respostas)
        + "\n\nReescreva os campos da estratégia incorporando essas "
        "respostas, resolvendo as lacunas apontadas. Campos que não têm "
        "relação com nenhuma das respostas acima devem manter o texto "
        "atual, com o mesmo nível de detalhe.\n\n"
        'Responda apenas em JSON: {"metas": [{"descricao": "...", "metrica": "...", '
        '"alvo": "...", "prazo": "..."}], "temas_roadmap": ["..."], "horizonte_tempo": "..."}'
    )
    dados = complete_json(prompt, system=_SYSTEM)

    if dados.get("metas"):
        strategy.goals = [
            StrategicGoal(
                description=item.get("descricao") or "",
                metric=item.get("metrica") or "",
                target=item.get("alvo") or "",
                timeframe=item.get("prazo") or "",
            )
            for item in dados["metas"]
        ]
    strategy.roadmap_themes = dados.get("temas_roadmap") or strategy.roadmap_themes
    strategy.time_horizon = dados.get("horizonte_tempo") or strategy.time_horizon
    return strategy
