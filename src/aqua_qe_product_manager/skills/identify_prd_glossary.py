from ..models import GlossaryTerm
from ..services.llm_service import complete_json

_SYSTEM = (
    "Você identifica termos de domínio específicos deste produto (ex.: "
    "'Unidade', 'Paciente', 'Fila') que aparecem no texto e se "
    "beneficiariam de uma definição curta para alinhar terminologia entre "
    "as equipes. Só responda com termos e definições sustentados pelo "
    "próprio texto — nunca adicione um termo genérico do domínio que não "
    "esteja presente nele. Se não houver termo relevante, responda com "
    "uma lista vazia."
)


def identify_prd_glossary(texto: str) -> list[GlossaryTerm]:
    """Identifica termos de domínio específicos deste PRD, distinto do glossário conceitual da plataforma."""
    prompt = (
        f"Texto:\n{texto}\n\n"
        'Responda apenas em JSON: {"termos": [{"termo": "...", "definicao": "..."}]}'
    )
    dados = complete_json(prompt, system=_SYSTEM)
    return [
        GlossaryTerm(term=item.get("termo", ""), definition=item.get("definicao", ""))
        for item in dados.get("termos", [])
    ]
