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

# format_prd_markdown numera "Requisitos funcionais"/"Requisitos não funcionais" como
# "RF-001: texto"/"RNF-001: texto" só na exportação — o prefixo precisa ser removido aqui
# para restaurar o texto original do requisito, não o texto numerado.
_CAMPOS_NUMERADOS = {
    "functional_requirements": re.compile(r"^RF-\d+: "),
    "non_functional_requirements": re.compile(r"^RNF-\d+: "),
}


def _para_lista(texto: str, prefixo_numerado: re.Pattern | None = None) -> list[str]:
    linhas = [linha.strip() for linha in texto.splitlines() if linha.strip()]
    if not linhas or linhas == ["(nenhum)"]:
        return []
    itens = [linha[2:] if linha.startswith("- ") else linha for linha in linhas]
    if prefixo_numerado:
        itens = [prefixo_numerado.sub("", item) for item in itens]
    return itens


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
            setattr(draft, campo, _para_lista(conteudo, _CAMPOS_NUMERADOS.get(campo)))
        else:
            setattr(draft, campo, conteudo.strip())
    return draft
