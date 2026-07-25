from aqua_qe_product_manager.models import ProductVision
from aqua_qe_product_manager.skills.validate_product_vision import validate_product_vision


def _vision(**overrides) -> ProductVision:
    base = {
        "statement": "visao do produto",
        "target_audience": "publico alvo",
    }
    base.update(overrides)
    return ProductVision(**base)


def test_valid_vision_passes():
    assert validate_product_vision(_vision()) is True


def test_missing_statement_fails():
    assert validate_product_vision(_vision(statement="")) is False


def test_missing_target_audience_fails():
    assert validate_product_vision(_vision(target_audience="")) is False
