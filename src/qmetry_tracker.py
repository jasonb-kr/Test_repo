"""QMetry enrichment for Jira story automation metadata."""

from typing import List
import logging

import requests

from src.models import StoryMetrics

LOGGER = logging.getLogger(__name__)


def _derive_coverage(story: StoryMetrics) -> str:
    if story.automation.qmetry_automated and story.automation.is_automated:
        return "Full"
    if story.automation.qmetry_automated or story.automation.is_automated:
        return "Partial"
    return "None"


def enrich_with_qmetry(stories: List[StoryMetrics], config) -> List[StoryMetrics]:
    """Update stories with QMetry automation checkbox data when configured."""

    if not config.QMETRY_API_TOKEN or not config.QMETRY_URL:
        LOGGER.warning("QMetry credentials missing. Skipping QMetry enrichment.")
        for story in stories:
            story.automation.qmetry_automated = False
            story.automation.coverage_type = _derive_coverage(story)
        return stories

    headers = {
        "Authorization": "Bearer " + config.QMETRY_API_TOKEN,
        "Accept": "application/json",
    }

    for story in stories:
        story.automation.qmetry_automated = False

        try:
            response = requests.get(
                f"{config.QMETRY_URL.rstrip('/')}/testcases",
                headers=headers,
                params={"jiraKey": story.story_key},
                timeout=15,
            )
            response.raise_for_status()
            payload = response.json() or {}

            items = payload.get("items") if isinstance(payload, dict) else []
            if not items:
                LOGGER.warning("No QMetry test case found for story %s", story.story_key)
            else:
                first = items[0]
                story.automation.qmetry_automated = bool(
                    first.get("automation")
                    or first.get("automated")
                    or first.get("isAutomated")
                    or first.get("automationCheckbox")
                )
        except requests.RequestException as exc:
            LOGGER.warning("QMetry lookup failed for %s: %s", story.story_key, exc)
            story.automation.qmetry_automated = False

        story.automation.coverage_type = _derive_coverage(story)

    return stories
