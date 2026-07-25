from ..models import ArtifactStatus, ProductVision
from ..skills.generate_product_vision import generate_product_vision
from ..skills.refine_product_vision import refine_product_vision
from ..skills.review_product_vision import review_product_vision
from ..skills.validate_product_vision import validate_product_vision


def finalize_vision(vision: ProductVision) -> ProductVision:
    """Aplica o checklist automático e a revisão por LLM, decidindo o status final da visão."""
    if not validate_product_vision(vision):
        vision.status = ArtifactStatus.PENDING_CLARIFICATION
        return vision

    revisao = review_product_vision(vision)
    vision.review_notes = revisao["problemas"]
    vision.status = (
        ArtifactStatus.DRAFT_VALIDATED
        if revisao["aprovado"]
        else ArtifactStatus.PENDING_CLARIFICATION
    )
    return vision


def generate_vision_draft(ideia: str, contexto: dict | None = None) -> ProductVision:
    """Gera a visão de produto a partir de uma ideia (e contexto de descoberta, quando disponível), aplicando validação e revisão."""
    vision = generate_product_vision(ideia, contexto)
    return finalize_vision(vision)


def refine_vision_draft(vision: ProductVision, respostas: list[dict]) -> ProductVision:
    """Reescreve a visão com base nas respostas do usuário e reaplica validação/revisão."""
    vision_refinada = refine_product_vision(vision, respostas)
    return finalize_vision(vision_refinada)
