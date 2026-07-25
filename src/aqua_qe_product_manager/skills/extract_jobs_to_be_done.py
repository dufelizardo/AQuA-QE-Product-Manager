from ..models import JobToBeDone
from ..services.llm_service import complete_json

_SYSTEM = (
    "Você extrai Jobs to Be Done (JTBD) de um texto de entrada, no formato "
    "'Quando [situação], eu quero [motivação], para que [resultado "
    "esperado]'. Só responda com jobs literalmente sustentados pelo texto. "
    "Nunca invente um job não sustentado por ele — se não houver job "
    "identificável, responda com uma lista vazia."
)


def extract_jobs_to_be_done(texto: str) -> list[JobToBeDone]:
    """Extrai jobs-to-be-done do texto de entrada, conforme knowledge/methodology/jtbd.md."""
    prompt = (
        f"Texto:\n{texto}\n\n"
        "Identifique os Jobs to Be Done descritos no texto.\n"
        'Responda apenas em JSON: {"jobs": [{"situacao": "...", "motivacao": "...", '
        '"resultado_esperado": "...", "trecho_fonte": "..."}]}'
    )
    dados = complete_json(prompt, system=_SYSTEM)
    return [
        JobToBeDone(
            situation=item.get("situacao") or "",
            motivation=item.get("motivacao") or "",
            expected_outcome=item.get("resultado_esperado") or "",
            source_reference=item.get("trecho_fonte") or "",
        )
        for item in dados.get("jobs", [])
    ]
