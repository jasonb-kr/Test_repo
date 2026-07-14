"""Run the end-to-end Jira/QMetry to Power BI export pipeline."""

from src.config import load_config
from src.jira_tracker import get_team_stories
from src.qmetry_tracker import enrich_with_qmetry
from src.report_exporter import export_to_powerbi


def main() -> None:
    """Execute pipeline and print a concise summary."""

    config = load_config()
    stories = get_team_stories(config)
    stories = enrich_with_qmetry(stories, config)
    export_to_powerbi(stories, config.OUTPUT_DIR)

    total_stories = len(stories)
    total_defects = sum(len(story.defects) for story in stories)
    automated_count = sum(1 for story in stories if story.automation.is_automated or story.automation.qmetry_automated)
    automated_pct = (automated_count / total_stories * 100) if total_stories else 0

    print(f"Total stories: {total_stories}")
    print(f"Total defects: {total_defects}")
    print(f"% automated: {automated_pct:.2f}%")


if __name__ == "__main__":
    main()
