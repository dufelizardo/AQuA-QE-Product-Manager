from dataclasses import dataclass, field

from .business_objective import BusinessObjective
from .glossary_term import GlossaryTerm
from .persona import Persona
from .status import ArtifactStatus
from .user_journey import UserJourney


@dataclass
class PRDDraft:
    """PRD gerado a partir de uma ideia (e, opcionalmente, de descoberta/visão/estratégia aceitas),
    seções conforme docs/standards/prd_standard.md — exportado em Markdown byte-compatível com o
    que o AQuA-QE Product Owner já sabe interpretar via --modo lote --arquivo (as 9 seções
    originais nunca mudam de nome/ordem; campos novos só adicionam seções)."""

    context_problem: str = ""
    objective: str = ""
    target_audience: str = ""
    scope: str = ""
    out_of_scope: str = ""
    functional_requirements: list[str] = field(default_factory=list)
    non_functional_requirements: list[str] = field(default_factory=list)
    success_criteria: list[str] = field(default_factory=list)
    risks_assumptions: list[str] = field(default_factory=list)
    personas: list[Persona] = field(default_factory=list)
    user_journeys: list[UserJourney] = field(default_factory=list)
    business_objectives: list[BusinessObjective] = field(default_factory=list)
    use_cases: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    technical_assumptions: list[str] = field(default_factory=list)
    constraints: list[str] = field(default_factory=list)
    glossary: list[GlossaryTerm] = field(default_factory=list)
    candidate_product_metrics: list[str] = field(default_factory=list)
    mvp_scope: list[str] = field(default_factory=list)
    future_scope: list[str] = field(default_factory=list)
    status: ArtifactStatus = ArtifactStatus.PENDING_CLARIFICATION
    review_notes: list[str] = field(default_factory=list)
