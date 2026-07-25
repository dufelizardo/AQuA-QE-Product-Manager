from ..models import ArtifactStatus, PRDDraft
from ..skills.generate_prd import generate_prd
from ..skills.refine_prd import refine_prd
from ..skills.review_prd import review_prd
from ..skills.validate_prd import validate_prd


def finalize_prd(draft: PRDDraft) -> PRDDraft:
    """Aplica o checklist automático e a revisão por LLM, decidindo o status final do PRD."""
    if not validate_prd(draft):
        draft.status = ArtifactStatus.PENDING_CLARIFICATION
        return draft

    revisao = review_prd(draft)
    draft.review_notes = revisao["problemas"]
    draft.status = (
        ArtifactStatus.DRAFT_VALIDATED
        if revisao["aprovado"]
        else ArtifactStatus.PENDING_CLARIFICATION
    )
    return draft


def generate_prd_draft(ideia: str, contexto: dict | None = None) -> PRDDraft:
    """Gera um PRD a partir de uma ideia crua e, opcionalmente, de descoberta/visão/estratégia já aceitas, aplicando validação e revisão."""
    draft = generate_prd(ideia, contexto)
    return finalize_prd(draft)


def refine_prd_draft(draft: PRDDraft, respostas: list[dict]) -> PRDDraft:
    """Reescreve o PRD com base nas respostas do usuário e reaplica validação/revisão."""
    draft_refinado = refine_prd(draft, respostas)
    return finalize_prd(draft_refinado)
