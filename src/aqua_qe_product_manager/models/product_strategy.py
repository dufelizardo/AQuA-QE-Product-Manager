from dataclasses import dataclass, field

from .status import ArtifactStatus


@dataclass
class StrategicGoal:
    """Meta de estratégia de produto, rastreável à visão aceita."""

    description: str = ""
    metric: str = ""
    target: str = ""
    timeframe: str = ""
    source_reference: str = ""


@dataclass
class ProductStrategy:
    """Estratégia de produto, conforme docs/standards/product_strategy_standard.md."""

    goals: list[StrategicGoal] = field(default_factory=list)
    roadmap_themes: list[str] = field(default_factory=list)
    time_horizon: str = ""
    status: ArtifactStatus = ArtifactStatus.PENDING_CLARIFICATION
    review_notes: list[str] = field(default_factory=list)
