from ..models import PrioritizedRequirement
from ..skills.classify_moscow import classify_moscow
from ..skills.validate_moscow_classification import validate_moscow_classification


def classify_moscow_draft(
    requisitos: list[str], texto_fonte: str
) -> list[PrioritizedRequirement]:
    """Classifica os requisitos em MoSCoW e valida a correspondência com a lista original.

    Se a validação falhar (LLM devolveu uma lista inconsistente com os
    requisitos originais), aplica o fallback seguro de categoria vazia para
    todos, em vez de propagar uma classificação que não corresponde ao PRD.
    """
    itens = classify_moscow(requisitos, texto_fonte)
    if not validate_moscow_classification(itens, requisitos):
        return [PrioritizedRequirement(requirement=r) for r in requisitos]
    return itens
