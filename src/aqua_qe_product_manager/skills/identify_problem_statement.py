from ..models import ProblemStatement
from ..services.llm_service import complete_json

_SYSTEM = (
    "Você sintetiza um problem statement (problema, usuários afetados, "
    "impacto, evidência) a partir de um texto de entrada. Só responda com "
    "informação literalmente sustentada pelo texto. Nunca invente um "
    "problema, usuário afetado ou impacto que não decorra diretamente dele. "
    "Quando um campo não for identificável com confiança, deixe-o vazio."
)


def identify_problem_statement(texto: str) -> ProblemStatement:
    """Sintetiza um problem statement a partir do texto de entrada, conforme knowledge/templates/problem_statement.md."""
    prompt = (
        f"Texto:\n{texto}\n\n"
        "Identifique o problem statement descrito.\n"
        'Responda apenas em JSON: {"problema": "...", "usuarios_afetados": "...", '
        '"impacto": "...", "evidencia": "...", "trecho_fonte": "..."}\n'
        "Use string vazia para qualquer campo não identificável no texto."
    )
    dados = complete_json(prompt, system=_SYSTEM)
    return ProblemStatement(
        problem=dados.get("problema") or "",
        affected_users=dados.get("usuarios_afetados") or "",
        impact=dados.get("impacto") or "",
        evidence=dados.get("evidencia") or "",
        source_reference=dados.get("trecho_fonte") or "",
    )
