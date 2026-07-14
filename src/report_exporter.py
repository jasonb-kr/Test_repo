"""Export story and defect metrics for Power BI consumption."""

from pathlib import Path
from typing import List

import pandas as pd

from src.models import StoryMetrics


def export_to_powerbi(stories: List[StoryMetrics], output_dir: str) -> None:
    """Export flat story/defect data to CSV and JSON files."""

    target = Path(output_dir)
    target.mkdir(parents=True, exist_ok=True)

    story_rows = []
    defect_rows = []

    for story in stories:
        story_rows.append(
            {
                "story_key": story.story_key,
                "summary": story.summary,
                "status": story.status,
                "team": story.team,
                "sprint": story.sprint,
                "story_points": story.story_points,
                "created_date": story.created_date,
                "resolved_date": story.resolved_date,
                "defect_count": story.defect_count,
                "is_automated": story.automation.is_automated,
                "automation_label": story.automation.automation_label,
                "qmetry_automated": story.automation.qmetry_automated,
                "automation_coverage": story.automation.coverage_type,
            }
        )

        for defect in story.defects:
            defect_rows.append(
                {
                    "defect_key": defect.defect_key,
                    "story_key": story.story_key,
                    "summary": defect.summary,
                    "status": defect.status,
                    "severity": defect.severity,
                    "created_date": defect.created_date,
                    "resolved_date": defect.resolved_date,
                }
            )

    stories_df = pd.DataFrame(story_rows)
    defects_df = pd.DataFrame(defect_rows)

    stories_df.to_csv(target / "stories.csv", index=False)
    defects_df.to_csv(target / "defects.csv", index=False)
    stories_df.to_json(target / "stories.json", orient="records", indent=2)
    defects_df.to_json(target / "defects.json", orient="records", indent=2)
