from ..models import BusinessObjective
from ..services.llm_service import complete_json

_SYSTEM = (
    "Você reestrutura o objetivo do produto e os critérios de sucesso já "
    "definidos em pares objetivo-de-negócio → KPI explícitos. Baseie-se "
    "apenas no objetivo e nos critérios de sucesso informados — nunca "
    "invente uma meta numérica ou KPI que não decorra diretamente deles. "
    "Se o objetivo/critérios não permitirem extrair um KPI claro para um "
    "item, deixe o campo de KPI vazio em vez de inventar um número."
)


def identify_business_objectives(
    objetivo: str, criterios_sucesso: list[str]
) -> list[BusinessObjective]:
    """Reestrutura objetivo/critérios de sucesso já aceitos em pares objetivo-de-negócio → KPI."""
    prompt = (
        f"Objetivo do produto: {objetivo}\n"
        f"Critérios de sucesso: {criterios_sucesso}\n\n"
        'Responda apenas em JSON: {"objetivos": [{"objetivo": "...", "kpi": "..."}]}'
    )
    dados = complete_json(prompt, system=_SYSTEM)
    return [
        BusinessObjective(objective=item.get("objetivo", ""), kpi=item.get("kpi", ""))
        for item in dados.get("objetivos", [])
    ]
