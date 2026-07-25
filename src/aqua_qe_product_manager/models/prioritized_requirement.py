from dataclasses import dataclass, field

MOSCOW_CATEGORIAS = ("must", "should", "could", "wont")


@dataclass
class PriorityInputs:
    """Estimativas numéricas para RICE/WSJF, sempre fornecidas pelo usuário — nunca inventadas (GR-M4)."""

    reach: float | None = None
    impact: float | None = None
    confidence: float | None = None
    effort: float | None = None
    business_value: float | None = None
    time_criticality: float | None = None
    risk_reduction: float | None = None
    job_size: float | None = None


@dataclass
class PrioritizedRequirement:
    """Um requisito funcional do PRD com sua priorização, conforme docs/agent/output_schema.md."""

    requirement: str
    moscow: str = ""
    moscow_justification: str = ""
    metodo_numerico: str = ""
    score: float | None = None
    inputs: PriorityInputs = field(default_factory=PriorityInputs)
