import re

from ..models import PRDDraft

_SECAO_PARA_CAMPO = {
    "Contexto e problema": "context_problem",
    "Objetivo do produto": "objective",
    "Público-alvo": "target_audience",
    "Escopo": "scope",
    "Fora de escopo": "out_of_scope",
    "Requisitos funcionais": "functional_requirements",
    "Requisitos não funcionais": "non_functional_requirements",
    "Critérios de sucesso": "success_criteria",
    "Riscos e premissas": "risks_assumptions",
}

_CAMPOS_LISTA = {
    "functional_requirements",
    "non_functional_requirements",
    "success_criteria",
    "risks_assumptions",
}


def _para_lista(texto: str) -> list[str]:
    linhas = [linha.strip() for linha in texto.splitlines() if linha.strip()]
    if not linhas or linhas == ["(nenhum)"]:
        return []
    return [linha[2:] if linha.startswith("- ") else linha for linha in linhas]


def parse_prd_markdown(texto: str) -> PRDDraft:
    """Reconstrói um PRDDraft a partir do Markdown produzido por format_prd_markdown, preservando a redação original campo a campo.

    Puro Python, determinístico — nunca invoca o LLM e nunca inventa
    conteúdo para uma seção ausente ou não reconhecida (o campo fica com
    o default vazio do dataclass, mesmo padrão de robustez do resto do
    agente).
    """
    secoes = re.split(r"(?m)^## (.+)$", texto)

    draft = PRDDraft()
    for titulo, conteudo in zip(secoes[1::2], secoes[2::2]):
        campo = _SECAO_PARA_CAMPO.get(titulo.strip())
        if not campo:
            continue
        if campo in _CAMPOS_LISTA:
            setattr(draft, campo, _para_lista(conteudo))
        else:
            setattr(draft, campo, conteudo.strip())
    return draft
