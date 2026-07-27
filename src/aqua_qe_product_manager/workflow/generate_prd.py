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

_CAMPOS_CENTRAIS = (
    "context_problem",
    "objective",
    "target_audience",
    "scope",
    "out_of_scope",
    "functional_requirements",
    "non_functional_requirements",
    "success_criteria",
    "risks_assumptions",
)

# Mapa de dependência heurístico: por campo de profundidade, quais campos centrais o afetam.
# Usado só para decidir se vale a pena re-rodar a skill correspondente após um refinamento —
# não é uma prova de que a skill mudaria, é uma heurística deliberadamente enviesada para
# re-executar quando houver dúvida (nunca para o lado de pular na dúvida), para não reintroduzir
# o bug de obsolescência já corrigido uma vez no agente irmão AQuA-QE Solution Architect.
_DEPENDENCIAS_PROFUNDIDADE: dict[str, frozenset[str]] = {
    "personas": frozenset({"context_problem", "target_audience", "scope"}),
    "user_journeys": frozenset({"scope", "functional_requirements"}),
    "business_objectives": frozenset({"objective", "success_criteria"}),
    "use_cases": frozenset({"scope", "functional_requirements"}),
    "dependencies": frozenset({"functional_requirements", "non_functional_requirements"}),
    "technical_assumptions": frozenset({"non_functional_requirements", "risks_assumptions"}),
    "constraints": frozenset({"non_functional_requirements", "risks_assumptions", "out_of_scope"}),
    "glossary": frozenset(
        {"context_problem", "scope", "functional_requirements", "non_functional_requirements"}
    ),
    "candidate_product_metrics": frozenset({"context_problem", "objective", "target_audience"}),
    "mvp_scope": frozenset({"functional_requirements", "scope", "out_of_scope"}),
}


def _capturar_campos_centrais(draft: PRDDraft) -> dict[str, object]:
    """Snapshot dos 9 campos centrais antes de um refinamento, para diff posterior."""
    return {campo: getattr(draft, campo) for campo in _CAMPOS_CENTRAIS}


def _campos_centrais_alterados(antes: dict[str, object], depois: PRDDraft) -> set[str]:
    """Compara o snapshot anterior com o draft atual, campo a campo, sem heurística — qualquer
    diferença de conteúdo conta como alterado (inclusive uma lista reordenada com o mesmo
    conteúdo), de propósito, para nunca subestimar o que mudou."""
    return {campo for campo, valor in antes.items() if valor != getattr(depois, campo)}


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


def _enriquecer_prd(
    draft: PRDDraft,
    ideia: str,
    contexto: dict | None,
    campos_alterados: set[str] | None = None,
) -> PRDDraft:
    """Preenche os campos de profundidade do PRD (personas, jornadas, objetivos com KPI, casos de
    uso, dependências, premissas, restrições, glossário, métricas candidatas e MVP), reaproveitando
    personas já sintetizadas na descoberta quando disponíveis, para não pagar duas vezes o custo do LLM.

    `campos_alterados`, quando informado (só no caminho de refinamento), restringe a re-derivação
    aos campos de profundidade cujo mapa de dependência (`_DEPENDENCIAS_PROFUNDIDADE`) intersecta
    os campos centrais que de fato mudaram — os demais mantêm o valor já existente no draft. Com
    `None` (geração inicial, ou refinamento forçado), todos os 10 campos são sempre re-derivados,
    igual ao comportamento histórico.
    """

    def _rederivar(campo: str) -> bool:
        return campos_alterados is None or bool(
            _DEPENDENCIAS_PROFUNDIDADE[campo] & campos_alterados
        )

    contexto = contexto or {}
    if _rederivar("personas"):
        personas_descoberta = contexto.get("personas")
        draft.personas = (
            personas_descoberta if personas_descoberta else synthesize_personas(ideia)
        )
    if _rederivar("user_journeys"):
        draft.user_journeys = identify_user_journeys(ideia)
    if _rederivar("business_objectives"):
        draft.business_objectives = identify_business_objectives(
            draft.objective, draft.success_criteria
        )
    if _rederivar("use_cases"):
        draft.use_cases = identify_use_cases(ideia)
    if _rederivar("dependencies"):
        draft.dependencies = identify_external_dependencies(ideia)
    if _rederivar("technical_assumptions"):
        draft.technical_assumptions = identify_technical_assumptions(ideia)
    if _rederivar("constraints"):
        draft.constraints = identify_constraints(ideia)
    if _rederivar("glossary"):
        draft.glossary = identify_prd_glossary(ideia)
    if _rederivar("candidate_product_metrics"):
        draft.candidate_product_metrics = identify_candidate_product_metrics(ideia)
    if _rederivar("mvp_scope"):
        draft.mvp_scope, draft.future_scope = identify_mvp_scope(
            draft.functional_requirements, ideia
        )
    return draft


def generate_prd_draft(ideia: str, contexto: dict | None = None) -> PRDDraft:
    """Gera um PRD a partir de uma ideia crua e, opcionalmente, de descoberta/visão/estratégia já aceitas, aplicando validação e revisão."""
    draft = generate_prd(ideia, contexto)
    draft = _enriquecer_prd(draft, ideia, contexto)
    return finalize_prd(draft)


def refine_prd_draft(
    draft: PRDDraft, respostas: list[dict], forcar_rederivacao_completa: bool = False
) -> PRDDraft:
    """Reescreve o PRD com base nas respostas do usuário e reaplica validação/revisão.

    Os campos de profundidade só são re-derivados quando o mapa de dependência
    (`_DEPENDENCIAS_PROFUNDIDADE`) indica que um dos campos centrais alterados por este
    refinamento os afeta — evita pagar o custo de todas as 10 skills quando a resposta do
    usuário só tocou, por exemplo, riscos e premissas. Na dúvida (heurística de baixa confiança),
    a skill é re-executada; nunca pulada por engano. `forcar_rederivacao_completa=True` ignora o
    mapa e sempre re-deriva todos os 10 campos (mesmo comportamento de antes desta otimização),
    como válvula de escape caso o mapa heurístico erre em algum caso real.
    """
    campos_antes = _capturar_campos_centrais(draft)
    draft_refinado = refine_prd(draft, respostas)

    if forcar_rederivacao_completa:
        campos_alterados = None
    else:
        campos_alterados = _campos_centrais_alterados(campos_antes, draft_refinado)

    texto_atualizado = format_prd_markdown(draft_refinado)
    draft_refinado = _enriquecer_prd(
        draft_refinado, texto_atualizado, contexto=None, campos_alterados=campos_alterados
    )
    return finalize_prd(draft_refinado)
