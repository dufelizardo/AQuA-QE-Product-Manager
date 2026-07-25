from dataclasses import dataclass, field


@dataclass
class Persona:
    """Persona sintetizada a partir da fonte de entrada, conforme docs/agent/output_schema.md."""

    name: str = ""
    description: str = ""
    goals: list[str] = field(default_factory=list)
    pain_points: list[str] = field(default_factory=list)
    source_reference: str = ""
