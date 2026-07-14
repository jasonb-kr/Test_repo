import unittest
from unittest.mock import Mock, patch

from src.models import AutomationStatus, StoryMetrics
from src.qmetry_tracker import enrich_with_qmetry


class TestQmetryTracker(unittest.TestCase):
    def test_skips_when_token_missing(self):
        config = Mock(QMETRY_API_TOKEN="", QMETRY_URL="")
        story = StoryMetrics(
            story_key="ABC-1",
            summary="s",
            status="Open",
            team="T",
            sprint="",
            story_points=1,
            created_date="",
            resolved_date="",
            automation=AutomationStatus(is_automated=False),
        )

        result = enrich_with_qmetry([story], config)
        self.assertFalse(result[0].automation.qmetry_automated)
        self.assertEqual(result[0].automation.coverage_type, "None")

    @patch("src.qmetry_tracker.requests.get")
    def test_marks_qmetry_automated_from_api(self, mock_get):
        config = Mock(QMETRY_API_TOKEN="token", QMETRY_URL="https://qmetry")
        response = Mock()
        response.json.return_value = {"items": [{"automation": True}]}
        response.raise_for_status.return_value = None
        mock_get.return_value = response

        story = StoryMetrics(
            story_key="ABC-1",
            summary="s",
            status="Open",
            team="T",
            sprint="",
            story_points=1,
            created_date="",
            resolved_date="",
            automation=AutomationStatus(is_automated=False),
        )

        result = enrich_with_qmetry([story], config)
        self.assertTrue(result[0].automation.qmetry_automated)
        self.assertEqual(result[0].automation.coverage_type, "Partial")


if __name__ == "__main__":
    unittest.main()
