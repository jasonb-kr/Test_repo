"""Jira data retrieval and story metric extraction."""

import logging
import traceback
from typing import List, Optional

from jira import JIRA

from src.models import AutomationStatus, DefectInfo, StoryMetrics

LOGGER = logging.getLogger(__name__)


def _get_story_points(issue, config) -> float:
    field_name = (config.JIRA_CUSTOM_FIELDS or {}).get("story_points", "customfield_10016")
    return getattr(issue.fields, field_name, None) or 0


def _get_sprint(issue, config) -> str:
    field_name = (config.JIRA_CUSTOM_FIELDS or {}).get("sprint", "customfield_10020")
    sprint_data = getattr(issue.fields, field_name, None)
    if not sprint_data:
        return ""
    if isinstance(sprint_data, list) and sprint_data:
        latest = sprint_data[-1]
        return getattr(latest, "name", str(latest))
    return getattr(sprint_data, "name", str(sprint_data))


def _first_automation_label(labels: List[str]) -> str:
    for label in labels or []:
        if "automation" in label.lower():
            return label
    return ""


def _coverage_type_from_label(label: str) -> str:
    if not label:
        return "None"

    lowered = label.lower()
    if "full" in lowered:
        return "Full"
    if "partial" in lowered:
        return "Partial"
    return "Partial"


def _build_defect_info(jira_client: JIRA, linked_issue_ref) -> Optional[DefectInfo]:
    try:
        linked_issue = jira_client.issue(linked_issue_ref.key)
    except Exception as exc:
        LOGGER.warning("Unable to fetch linked issue %s: %s", getattr(linked_issue_ref, "key", "unknown"), exc)
        return None

    issue_type = getattr(linked_issue.fields.issuetype, "name", "")
    if issue_type.lower() != "bug":
        return None

    priority = getattr(linked_issue.fields, "priority", None)
    severity = getattr(priority, "name", "Unknown") if priority else "Unknown"

    return DefectInfo(
        defect_key=linked_issue.key,
        summary=getattr(linked_issue.fields, "summary", ""),
        status=getattr(getattr(linked_issue.fields, "status", None), "name", ""),
        severity=severity,
        created_date=getattr(linked_issue.fields, "created", ""),
        resolved_date=getattr(linked_issue.fields, "resolutiondate", "") or "",
    )


def get_team_stories(config) -> List[StoryMetrics]:
    """Fetch team stories from Jira and calculate defect and automation metrics."""

    jira_client = JIRA(server=config.JIRA_URL, basic_auth=(config.JIRA_USERNAME, config.JIRA_API_TOKEN))

    primary_jql = (
        f'project = {config.JIRA_PROJECT_KEY} AND issuetype = Story AND '
        f'"Team[Team]" = "{config.TEAM_NAME}" ORDER BY created DESC'
    )
    fallback_jql = (
        f'project = {config.JIRA_PROJECT_KEY} AND issuetype = Story AND '
        f'labels = "{config.TEAM_NAME}" ORDER BY created DESC'
    )

    fields = "summary,status,issuelinks,labels,created,resolutiondate"

    try:
        print(f"Executing primary Jira JQL: {primary_jql}")
        LOGGER.info("Executing primary Jira JQL: %s", primary_jql)
        issues = jira_client.search_issues(primary_jql, maxResults=False, fields=fields)
        print(f"Primary Jira query returned {len(issues)} issues")
        LOGGER.info("Primary Jira query returned %s issues", len(issues))
    except Exception as exc:
        print(f"Primary Jira JQL failed with exception:\n{traceback.format_exc()}")
        LOGGER.warning("Primary JQL failed, falling back to label query: %s", exc)
        issues = []

    if not issues:
        print(f"Executing fallback Jira JQL: {fallback_jql}")
        LOGGER.info("Executing fallback Jira JQL: %s", fallback_jql)
        issues = jira_client.search_issues(fallback_jql, maxResults=False, fields=fields)
        print(f"Fallback Jira query returned {len(issues)} issues")
        LOGGER.info("Fallback Jira query returned %s issues", len(issues))

    stories: List[StoryMetrics] = []

    for issue in issues:
        labels = getattr(issue.fields, "labels", []) or []
        automation_label = _first_automation_label(labels)
        defects: List[DefectInfo] = []

        for link in getattr(issue.fields, "issuelinks", []) or []:
            linked_issue_ref = getattr(link, "inwardIssue", None) or getattr(link, "outwardIssue", None)
            if not linked_issue_ref:
                continue

            defect = _build_defect_info(jira_client, linked_issue_ref)
            if defect:
                defects.append(defect)

        automation = AutomationStatus(
            is_automated=bool(automation_label),
            automation_label=automation_label,
            qmetry_automated=False,
            coverage_type=_coverage_type_from_label(automation_label),
        )

        stories.append(
            StoryMetrics(
                story_key=issue.key,
                summary=getattr(issue.fields, "summary", ""),
                status=getattr(getattr(issue.fields, "status", None), "name", ""),
                team=config.TEAM_NAME,
                sprint=_get_sprint(issue, config),
                story_points=float(_get_story_points(issue, config) or 0),
                created_date=getattr(issue.fields, "created", ""),
                resolved_date=getattr(issue.fields, "resolutiondate", "") or "",
                defects=defects,
                defect_count=len(defects),
                automation=automation,
            )
        )

    print(f"Total stories returned from Jira: {len(stories)}")
    LOGGER.info("Total stories returned from Jira: %s", len(stories))
    return stories
