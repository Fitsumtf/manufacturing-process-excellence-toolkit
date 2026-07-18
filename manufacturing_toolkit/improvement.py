"""Structured manufacturing problem-solving records."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ImprovementRecord:
    title: str
    problem: str
    baseline: str
    evidence: str
    root_cause: str
    engineering_action: str
    validation: str
    control_plan: str

    def as_markdown(self) -> str:
        fields = [
            ("Problem", self.problem), ("Baseline", self.baseline),
            ("Evidence", self.evidence), ("Root cause", self.root_cause),
            ("Engineering action", self.engineering_action),
            ("Validation", self.validation), ("Control plan", self.control_plan),
        ]
        return "\n".join([f"# {self.title}", ""] + [f"## {k}\n\n{v}\n" for k, v in fields])
