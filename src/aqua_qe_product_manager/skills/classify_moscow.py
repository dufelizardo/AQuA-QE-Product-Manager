from ..models import PrioritizedRequirement
from ..services.llm_service import complete_json

_SYSTEM = (
    "Você classifica requisitos funcionais de um PRD em MoSCoW (Must/Should/"
    "Could/Won't), com base exclusivamente em sinais de linguagem explícitos "
    "no texto de origem (ex.: 'essencial', 'obrigatório', 'crítico' → must; "
    "'importante', 'deveria' → should; 'seria bom ter', 'desejável' → could; "
    "'não é prioridade agora', 'fora do escopo inicial' → wont). Nunca "
    "invente uma categoria quando o texto não der nenhum sinal claro — "
    "nesse caso, deixe a categoria vazia e a justificativa vazia."
)


def classify_moscow(requisitos: list[str], texto_fonte: str) -> list[PrioritizedRequirement]:
    """Classifica cada requisito funcional em MoSCoW a partir de sinais de linguagem no texto de origem (nunca inventados)."""
    prompt = (
        f"Texto de origem (PRD completo):\n{texto_fonte}\n\n"
        f"Requisitos funcionais a classificar, na ordem:\n"
        + "\n".join(f"{i + 1}. {r}" for i, r in enumerate(requisitos))
        + "\n\nPara cada requisito, na mesma ordem, retorne a categoria MoSCoW "
        "('must', 'should', 'could', 'wont' ou '' se não houver sinal claro) "
        "e uma justificativa citando o trecho do texto que sustenta a "
        "categoria (ou justificativa vazia, se a categoria for vazia).\n\n"
        'Responda apenas em JSON: {"classificacoes": [{"requisito": "...", '
        '"categoria": "...", "justificativa": "..."}]}'
    )
    dados = complete_json(prompt, system=_SYSTEM)
    itens = dados.get("classificacoes") or []
    return [
        PrioritizedRequirement(
            requirement=item.get("requisito") or "",
            moscow=(item.get("categoria") or "").lower(),
            moscow_justification=item.get("justificativa") or "",
        )
        for item in itens
    ]
