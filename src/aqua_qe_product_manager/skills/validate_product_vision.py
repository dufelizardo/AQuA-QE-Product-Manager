from ..models import ProductVision


def validate_product_vision(vision: ProductVision) -> bool:
    """Valida se a visão tem statement e público-alvo preenchidos."""
    return bool(vision.statement) and bool(vision.target_audience)
