from dataclasses import dataclass


@dataclass
class JobToBeDone:
    """Job to Be Done extraído da fonte de entrada, conforme knowledge/methodology/jtbd.md."""

    situation: str = ""
    motivation: str = ""
    expected_outcome: str = ""
    source_reference: str = ""
