from dataclasses import dataclass


@dataclass
class ProblemStatement:
    """Problema sintetizado a partir da fonte de entrada, conforme docs/agent/output_schema.md."""

    problem: str = ""
    affected_users: str = ""
    impact: str = ""
    evidence: str = ""
    source_reference: str = ""
