from ..models import ArtifactStatus, ProductStrategy, ProductVision
from ..skills.generate_product_strategy import generate_product_strategy
from ..skills.refine_product_strategy import refine_product_strategy
from ..skills.review_product_strategy import review_product_strategy
from ..skills.validate_product_strategy import validate_product_strategy


def finalize_strategy(strategy: ProductStrategy) -> ProductStrategy:
    """Aplica o checklist automático e a revisão por LLM, decidindo o status final da estratégia."""
    if not validate_product_strategy(strategy):
        strategy.status = ArtifactStatus.PENDING_CLARIFICATION
        return strategy

    revisao = review_product_strategy(strategy)
    strategy.review_notes = revisao["problemas"]
    strategy.status = (
        ArtifactStatus.DRAFT_VALIDATED
        if revisao["aprovado"]
        else ArtifactStatus.PENDING_CLARIFICATION
    )
    return strategy


def generate_strategy_draft(
    vision: ProductVision, contexto: dict | None = None
) -> ProductStrategy:
    """Gera a estratégia de produto a partir da visão já aceita, aplicando validação e revisão."""
    strategy = generate_product_strategy(vision, contexto)
    return finalize_strategy(strategy)


def refine_strategy_draft(
    strategy: ProductStrategy, respostas: list[dict]
) -> ProductStrategy:
    """Reescreve a estratégia com base nas respostas do usuário e reaplica validação/revisão."""
    strategy_refinada = refine_product_strategy(strategy, respostas)
    return finalize_strategy(strategy_refinada)
