def compute_wsjf_score(
    business_value: float, time_criticality: float, risk_reduction: float, job_size: float
) -> float:
    """WSJF = (Business Value + Time Criticality + Risk Reduction) / Job Size. Todos os valores vêm do usuário — nunca estimados pelo agente (GR-M4)."""
    return (business_value + time_criticality + risk_reduction) / job_size
