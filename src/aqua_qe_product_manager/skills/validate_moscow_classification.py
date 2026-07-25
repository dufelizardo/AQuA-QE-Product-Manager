from ..models import MOSCOW_CATEGORIAS, PrioritizedRequirement

_CATEGORIAS_VALIDAS = (*MOSCOW_CATEGORIAS, "")


def validate_moscow_classification(
    itens: list[PrioritizedRequirement], requisitos_originais: list[str]
) -> bool:
    """Confere que a classificação corresponde 1:1 aos requisitos originais (mesmo texto, mesma ordem) e usa só categorias válidas (ou vazia)."""
    if len(itens) != len(requisitos_originais):
        return False
    for item, esperado in zip(itens, requisitos_originais):
        if item.requirement != esperado:
            return False
        if item.moscow not in _CATEGORIAS_VALIDAS:
            return False
    return True
