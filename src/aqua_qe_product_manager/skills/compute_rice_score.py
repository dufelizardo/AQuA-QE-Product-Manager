def compute_rice_score(reach: float, impact: float, confidence: float, effort: float) -> float:
    """RICE = (Reach x Impact x Confidence) / Effort. Todos os valores vêm do usuário — nunca estimados pelo agente (GR-M4)."""
    return (reach * impact * confidence) / effort
