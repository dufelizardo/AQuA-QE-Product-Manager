from aqua_qe_product_manager.models import ProductStrategy, StrategicGoal
from aqua_qe_product_manager.skills.validate_product_strategy import validate_product_strategy


def _strategy(**overrides) -> ProductStrategy:
    base = {
        "goals": [StrategicGoal(description="meta", metric="metrica")],
    }
    base.update(overrides)
    return ProductStrategy(**base)


def test_valid_strategy_passes():
    assert validate_product_strategy(_strategy()) is True


def test_no_goals_fails():
    assert validate_product_strategy(_strategy(goals=[])) is False


def test_first_goal_missing_description_fails():
    assert validate_product_strategy(
        _strategy(goals=[StrategicGoal(description="", metric="metrica")])
    ) is False


def test_first_goal_missing_metric_fails():
    assert validate_product_strategy(
        _strategy(goals=[StrategicGoal(description="meta", metric="")])
    ) is False
