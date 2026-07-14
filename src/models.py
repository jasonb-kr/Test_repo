"""Data models used by the Jira/QMetry reporting pipeline."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class DefectInfo:
    """Represents defect details linked to a story."""

    defect_key: str
    summary: str
    status: str
    severity: str
    created_date: str
    resolved_date: str


@dataclass
class AutomationStatus:
    """Represents automation coverage for a story."""

    is_automated: bool = False
    automation_label: str = ""
    qmetry_automated: bool = False
    coverage_type: str = "None"


@dataclass
class StoryMetrics:
    """Represents story-level metrics for reporting."""

    story_key: str
    summary: str
    status: str
    team: str
    sprint: str
    story_points: float
    created_date: str
    resolved_date: str
    defects: List[DefectInfo] = field(default_factory=list)
    defect_count: int = 0
    automation: AutomationStatus = field(default_factory=AutomationStatus)
