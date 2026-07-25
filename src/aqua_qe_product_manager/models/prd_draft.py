from dataclasses import dataclass, field

from .status import ArtifactStatus


@dataclass
class PRDDraft:
    """PRD gerado a partir de uma ideia (e, opcionalmente, de descoberta/visão/estratégia aceitas),
    seções conforme docs/standards/prd_standard.md — mesmos campos exatos do PRDDraft do
    AQuA-QE Product Owner, para compatibilidade de handoff via --modo lote --arquivo."""

    context_problem: str = ""
    objective: str = ""
    target_audience: str = ""
    scope: str = ""
    out_of_scope: str = ""
    functional_requirements: list[str] = field(default_factory=list)
    non_functional_requirements: list[str] = field(default_factory=list)
    success_criteria: list[str] = field(default_factory=list)
    risks_assumptions: list[str] = field(default_factory=list)
    status: ArtifactStatus = ArtifactStatus.PENDING_CLARIFICATION
    review_notes: list[str] = field(default_factory=list)
