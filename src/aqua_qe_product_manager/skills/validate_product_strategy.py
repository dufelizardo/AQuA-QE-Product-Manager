from ..models import ProductStrategy


def validate_product_strategy(strategy: ProductStrategy) -> bool:
    """Valida se a estratégia tem ao menos uma meta com descrição e métrica preenchidas."""
    if not strategy.goals:
        return False
    primeira = strategy.goals[0]
    return bool(primeira.description) and bool(primeira.metric)
