from ..models import ArtifactStatus, PRDDraft
from ..skills.format_prd_markdown import format_prd_markdown
from ..skills.generate_prd import generate_prd
from ..skills.identify_business_objectives import identify_business_objectives
from ..skills.identify_candidate_product_metrics import identify_candidate_product_metrics
from ..skills.identify_constraints import identify_constraints
from ..skills.identify_external_dependencies import identify_external_dependencies
from ..skills.identify_mvp_scope import identify_mvp_scope
from ..skills.identify_prd_glossary import identify_prd_glossary
from ..skills.identify_technical_assumptions import identify_technical_assumptions
from ..skills.identify_use_cases import identify_use_cases
from ..skills.identify_user_journeys import identify_user_journeys
from ..skills.refine_prd import refine_prd
from ..skills.review_prd import review_prd
from ..skills.synthesize_personas import synthesize_personas
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


def _enriquecer_prd(draft: PRDDraft, ideia: str, contexto: dict | None) -> PRDDraft:
    """Preenche os campos de profundidade do PRD (personas, jornadas, objetivos com KPI, casos de
    uso, dependências, premissas, restrições, glossário, métricas candidatas e MVP), reaproveitando
    personas já sintetizadas na descoberta quando disponíveis, para não pagar duas vezes o custo do LLM."""
    contexto = contexto or {}
    personas_descoberta = contexto.get("personas")
    draft.personas = personas_descoberta if personas_descoberta else synthesize_personas(ideia)
    draft.user_journeys = identify_user_journeys(ideia)
    draft.business_objectives = identify_business_objectives(draft.objective, draft.success_criteria)
    draft.use_cases = identify_use_cases(ideia)
    draft.dependencies = identify_external_dependencies(ideia)
    draft.technical_assumptions = identify_technical_assumptions(ideia)
    draft.constraints = identify_constraints(ideia)
    draft.glossary = identify_prd_glossary(ideia)
    draft.candidate_product_metrics = identify_candidate_product_metrics(ideia)
    draft.mvp_scope, draft.future_scope = identify_mvp_scope(
        draft.functional_requirements, ideia
    )
    return draft


def generate_prd_draft(ideia: str, contexto: dict | None = None) -> PRDDraft:
    """Gera um PRD a partir de uma ideia crua e, opcionalmente, de descoberta/visão/estratégia já aceitas, aplicando validação e revisão."""
    draft = generate_prd(ideia, contexto)
    draft = _enriquecer_prd(draft, ideia, contexto)
    return finalize_prd(draft)


def refine_prd_draft(draft: PRDDraft, respostas: list[dict]) -> PRDDraft:
    """Reescreve o PRD com base nas respostas do usuário, re-deriva os campos de profundidade a
    partir do conteúdo já refinado (evita ficarem obsoletos após a refinada) e reaplica validação/revisão."""
    draft_refinado = refine_prd(draft, respostas)
    texto_atualizado = format_prd_markdown(draft_refinado)
    draft_refinado = _enriquecer_prd(draft_refinado, texto_atualizado, contexto=None)
    return finalize_prd(draft_refinado)
