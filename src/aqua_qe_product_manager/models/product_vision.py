from dataclasses import dataclass, field

from .status import ArtifactStatus


@dataclass
class ProductVision:
    """Visão de produto, conforme docs/standards/product_strategy_standard.md."""

    statement: str = ""
    target_audience: str = ""
    differentiators: list[str] = field(default_factory=list)
    north_star_metric: str = ""
    status: ArtifactStatus = ArtifactStatus.PENDING_CLARIFICATION
    review_notes: list[str] = field(default_factory=list)
