from aqua_qe_product_manager.skills.compute_rice_score import compute_rice_score


def test_compute_rice_score_applies_formula():
    resultado = compute_rice_score(reach=100, impact=2, confidence=0.8, effort=4)

    assert resultado == (100 * 2 * 0.8) / 4
