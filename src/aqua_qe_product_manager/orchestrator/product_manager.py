from ..models import (
    JobToBeDone,
    MarketAnalysis,
    PRDDraft,
    Persona,
    ProblemStatement,
    ProductStrategy,
    ProductVision,
)
from ..workflow.generate_prd import generate_prd_draft
from ..workflow.generate_problem_discovery import generate_problem_discovery
from ..workflow.generate_product_strategy import generate_strategy_draft
from ..workflow.generate_product_vision import generate_vision_draft


def handle_discovery(
    texto: str,
) -> tuple[ProblemStatement, list[Persona], list[JobToBeDone], MarketAnalysis]:
    """Sintetiza a descoberta (problem statement, personas, JTBD, mercado) a partir do texto de entrada, conforme docs/agent/agent_design.md."""
    return generate_problem_discovery(texto)


def handle_vision(ideia: str, contexto: dict | None = None) -> ProductVision:
    """Gera a visão de produto a partir de uma ideia e do contexto de descoberta, quando disponível."""
    return generate_vision_draft(ideia, contexto)


def handle_strategy(vision: ProductVision, contexto: dict | None = None) -> ProductStrategy:
    """Gera a estratégia de produto a partir da visão já aceita."""
    return generate_strategy_draft(vision, contexto)


def handle_prd(ideia: str, contexto: dict | None = None) -> PRDDraft:
    """Gera o PRD a partir de uma ideia e, opcionalmente, de descoberta/visão/estratégia já aceitas."""
    return generate_prd_draft(ideia, contexto)
