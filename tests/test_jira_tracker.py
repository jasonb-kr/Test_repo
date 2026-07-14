import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from src.jira_tracker import get_team_stories


class TestJiraTracker(unittest.TestCase):
    @patch("src.jira_tracker.JIRA")
    def test_get_team_stories_with_automation_and_bug_links(self, mock_jira):
        config = Mock(
            JIRA_URL="https://jira.example.com",
            JIRA_USERNAME="user",
            JIRA_API_TOKEN="token",
            JIRA_PROJECT_KEY="ABC",
            TEAM_NAME="CS-FAAzureApps-BadAssets",
            JIRA_CUSTOM_FIELDS={"story_points": "customfield_10016", "sprint": "customfield_10020"},
        )

        issue = SimpleNamespace(
            key="ABC-1",
            fields=SimpleNamespace(
                summary="Story",
                status=SimpleNamespace(name="In Progress"),
                labels=["automation-full"],
                created="2026-01-01",
                resolutiondate="",
                customfield_10016=8,
                customfield_10020=[SimpleNamespace(name="Sprint X")],
                issuelinks=[SimpleNamespace(outwardIssue=SimpleNamespace(key="ABC-2"))],
            ),
        )
        bug_issue = SimpleNamespace(
            key="ABC-2",
            fields=SimpleNamespace(
                issuetype=SimpleNamespace(name="Bug"),
                summary="Bug summary",
                status=SimpleNamespace(name="Open"),
                priority=SimpleNamespace(name="High"),
                created="2026-01-01",
                resolutiondate="",
            ),
        )

        jira_client = Mock()
        jira_client.search_issues.return_value = [issue]
        jira_client.issue.return_value = bug_issue
        mock_jira.return_value = jira_client

        stories = get_team_stories(config)

        self.assertEqual(len(stories), 1)
        self.assertEqual(stories[0].story_key, "ABC-1")
        self.assertEqual(stories[0].defect_count, 1)
        self.assertTrue(stories[0].automation.is_automated)
        self.assertEqual(stories[0].automation.automation_label, "automation-full")


if __name__ == "__main__":
    unittest.main()
