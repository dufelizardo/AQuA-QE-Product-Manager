from ..models import ProductVision
from ..services.llm_service import complete_json

_SYSTEM = (
    "Você refina uma visão de produto existente com base nas respostas que "
    "quem propôs a ideia deu às perguntas de esclarecimento levantadas por "
    "um revisor. Baseie-se apenas na visão atual e nas respostas "
    "fornecidas; nunca invente diferencial ou métrica que não tenha sido "
    "informado neles. Nunca remova ou resuma um detalhe que já existe em "
    "um campo atual, a menos que uma resposta contradiga esse detalhe "
    "especificamente — preserve o texto existente nos campos que as "
    "respostas não abordam. Responda sempre em português."
)


def refine_product_vision(vision: ProductVision, respostas: list[dict]) -> ProductVision:
    """Reescreve os campos da visão usando as respostas às perguntas de esclarecimento, preservando o que não foi perguntado."""
    perguntas_respostas = [
        f"P: {item['pergunta']}\nR: {item['resposta']}" for item in respostas
    ]

    prompt = (
        f"Statement atual: {vision.statement}\n"
        f"Público-alvo atual: {vision.target_audience}\n"
        f"Diferenciais atuais: {vision.differentiators}\n"
        f"Métrica norte atual: {vision.north_star_metric}\n\n"
        "Respostas às perguntas de esclarecimento:\n"
        + "\n".join(perguntas_respostas)
        + "\n\nReescreva os campos da visão incorporando essas respostas, "
        "resolvendo as lacunas apontadas. Campos que não têm relação com "
        "nenhuma das respostas acima devem manter o texto atual, com o "
        "mesmo nível de detalhe.\n\n"
        'Responda apenas em JSON: {"statement": "...", "publico_alvo": "...", '
        '"diferenciais": ["..."], "metrica_norte": "..."}'
    )
    dados = complete_json(prompt, system=_SYSTEM)

    vision.statement = dados.get("statement") or vision.statement
    vision.target_audience = dados.get("publico_alvo") or vision.target_audience
    vision.differentiators = dados.get("diferenciais") or vision.differentiators
    vision.north_star_metric = dados.get("metrica_norte") or vision.north_star_metric
    return vision
