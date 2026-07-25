from dataclasses import dataclass, field

from .status import ArtifactStatus


@dataclass
class Competitor:
    """Concorrente citado na fonte de entrada, com rastreabilidade (GR-M1)."""

    name: str = ""
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    source_reference: str = ""


@dataclass
class MarketAnalysis:
    """Contexto de mercado sintetizado exclusivamente a partir da fonte de entrada, conforme docs/agent/output_schema.md."""

    competitors: list[Competitor] = field(default_factory=list)
    trends: list[str] = field(default_factory=list)
    market_context: str = ""
    status: ArtifactStatus = ArtifactStatus.PENDING_CLARIFICATION
    review_notes: list[str] = field(default_factory=list)
