from aqua_qe_product_manager.skills.compute_wsjf_score import compute_wsjf_score


def test_compute_wsjf_score_applies_formula():
    resultado = compute_wsjf_score(
        business_value=8, time_criticality=5, risk_reduction=3, job_size=4
    )

    assert resultado == (8 + 5 + 3) / 4
