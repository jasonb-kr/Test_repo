import json
import tempfile
import unittest
from pathlib import Path

from src.models import AutomationStatus, DefectInfo, StoryMetrics
from src.report_exporter import export_to_powerbi


class TestReportExporter(unittest.TestCase):
    def test_export_creates_flat_story_and_defect_outputs(self):
        story = StoryMetrics(
            story_key="ABC-1",
            summary="Story summary",
            status="Done",
            team="CS-FAAzureApps-BadAssets",
            sprint="Sprint 1",
            story_points=5,
            created_date="2026-01-01",
            resolved_date="2026-01-02",
            defects=[
                DefectInfo(
                    defect_key="ABC-2",
                    summary="Bug",
                    status="Open",
                    severity="High",
                    created_date="2026-01-01",
                    resolved_date="",
                )
            ],
            defect_count=1,
            automation=AutomationStatus(
                is_automated=True,
                automation_label="automation-full",
                qmetry_automated=True,
                coverage_type="Full",
            ),
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            export_to_powerbi([story], tmp_dir)

            stories_json = Path(tmp_dir) / "stories.json"
            defects_json = Path(tmp_dir) / "defects.json"
            self.assertTrue((Path(tmp_dir) / "stories.csv").exists())
            self.assertTrue((Path(tmp_dir) / "defects.csv").exists())
            self.assertTrue(stories_json.exists())
            self.assertTrue(defects_json.exists())

            stories = json.loads(stories_json.read_text(encoding="utf-8"))
            defects = json.loads(defects_json.read_text(encoding="utf-8"))

            self.assertEqual(stories[0]["story_key"], "ABC-1")
            self.assertEqual(stories[0]["defect_count"], 1)
            self.assertEqual(defects[0]["story_key"], "ABC-1")


if __name__ == "__main__":
    unittest.main()
