from ..models import JobToBeDone, MarketAnalysis, Persona, ProblemStatement
from ..skills.extract_jobs_to_be_done import extract_jobs_to_be_done
from ..skills.extract_market_context import extract_market_context
from ..skills.identify_problem_statement import identify_problem_statement
from ..skills.synthesize_personas import synthesize_personas


def generate_problem_discovery(
    texto: str,
) -> tuple[ProblemStatement, list[Persona], list[JobToBeDone], MarketAnalysis]:
    """Sintetiza problem statement, personas, jobs-to-be-done e contexto de mercado a partir do texto de entrada.

    Sem ciclo de aceite formal — são insumos estruturados que alimentam
    visão/estratégia/PRD, não artefatos "aceitos" isoladamente (ver
    docs/agent/acceptance_patterns.md).
    """
    problem_statement = identify_problem_statement(texto)
    personas = synthesize_personas(texto)
    jobs = extract_jobs_to_be_done(texto)
    market_analysis = extract_market_context(texto)
    return problem_statement, personas, jobs, market_analysis
