from dataclasses import dataclass


@dataclass
class GlossaryTerm:
    """Termo de domínio específico deste PRD, distinto do glossário conceitual da plataforma (knowledge/glossary/)."""

    term: str = ""
    definition: str = ""
