from dataclasses import dataclass


@dataclass
class BusinessObjective:
    """Objetivo de negócio com seu KPI associado, reestruturado a partir de objective/success_criteria já aceitos."""

    objective: str = ""
    kpi: str = ""
