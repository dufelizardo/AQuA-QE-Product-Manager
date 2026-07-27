from ..services.llm_service import complete_json

_SYSTEM = (
    "Você agrupa requisitos funcionais já definidos em dois conjuntos: "
    "MVP (essenciais para a primeira entrega) e versão futura (podem vir "
    "depois), com base em sinal de linguagem explícito no texto de origem "
    "(ex.: 'essencial', 'pode vir depois', 'fase 2'). Use apenas os "
    "requisitos fornecidos, sem reescrevê-los, adicionar novos ou remover "
    "nenhum — todo requisito da lista de entrada deve aparecer em "
    "exatamente um dos dois conjuntos de saída. Se o texto não distinguir "
    "claramente o que é essencial do que pode esperar, coloque todos em "
    "MVP e deixe a versão futura vazia — nunca decida uma priorização de "
    "negócio sem base no texto."
)


def identify_mvp_scope(
    requisitos_funcionais: list[str], texto: str
) -> tuple[list[str], list[str]]:
    """Agrupa os requisitos funcionais já existentes em MVP vs. versão futura, a partir de sinal de linguagem na fonte."""
    prompt = (
        f"Requisitos funcionais:\n{requisitos_funcionais}\n\n"
        f"Texto de origem:\n{texto}\n\n"
        'Responda apenas em JSON: {"mvp": ["..."], "versao_futura": ["..."]}'
    )
    dados = complete_json(prompt, system=_SYSTEM)
    return dados.get("mvp", []), dados.get("versao_futura", [])
