from aqua_qe_product_manager.models import PrioritizedRequirement
from aqua_qe_product_manager.skills.validate_moscow_classification import (
    validate_moscow_classification,
)


def test_valida_quando_corresponde_e_categorias_sao_validas():
    itens = [
        PrioritizedRequirement(requirement="A", moscow="must"),
        PrioritizedRequirement(requirement="B", moscow=""),
    ]

    assert validate_moscow_classification(itens, ["A", "B"]) is True


def test_invalida_quando_tamanho_diferente():
    itens = [PrioritizedRequirement(requirement="A", moscow="must")]

    assert validate_moscow_classification(itens, ["A", "B"]) is False


def test_invalida_quando_requisito_nao_corresponde():
    itens = [PrioritizedRequirement(requirement="Outro requisito", moscow="must")]

    assert validate_moscow_classification(itens, ["A"]) is False


def test_invalida_quando_categoria_desconhecida():
    itens = [PrioritizedRequirement(requirement="A", moscow="urgente")]

    assert validate_moscow_classification(itens, ["A"]) is False
