from dataclasses import dataclass, field


@dataclass
class UserJourney:
    """Jornada de um usuário/persona através do produto, sintetizada a partir da fonte de entrada."""

    name: str = ""
    steps: list[str] = field(default_factory=list)
    source_reference: str = ""
