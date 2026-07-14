"""Configuration loading for the Jira/QMetry reporting pipeline."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv
import os


@dataclass
class AppConfig:
    """Runtime settings loaded from .env and config.yaml."""

    JIRA_URL: str
    JIRA_USERNAME: str
    JIRA_API_TOKEN: str
    QMETRY_URL: str
    QMETRY_API_TOKEN: str
    TEAM_NAME: str
    JIRA_PROJECT_KEY: str
    OUTPUT_DIR: str
    JIRA_CUSTOM_FIELDS: Dict[str, str]
    AUTOMATION_LABEL_PREFIX: str


def _load_yaml_config(path: str) -> Dict[str, Any]:
    file_path = Path(path)
    if not file_path.exists():
        return {}

    with file_path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
        if not isinstance(data, dict):
            return {}
        return data


def load_config(config_path: str = "config.yaml") -> AppConfig:
    """Load configuration from .env and config.yaml with env var overrides."""

    load_dotenv()
    yaml_config = _load_yaml_config(config_path)

    team_name = os.getenv("TEAM_NAME") or yaml_config.get("team_name") or "CS-FAAzureApps-BadAssets"
    jira_project_key = os.getenv("JIRA_PROJECT_KEY") or yaml_config.get("jira_project_key") or ""
    output_dir = os.getenv("OUTPUT_DIR") or yaml_config.get("output_dir") or "output"

    return AppConfig(
        JIRA_URL=os.getenv("JIRA_URL", ""),
        JIRA_USERNAME=os.getenv("JIRA_USERNAME", ""),
        JIRA_API_TOKEN=os.getenv("JIRA_API_TOKEN", ""),
        QMETRY_URL=os.getenv("QMETRY_URL", ""),
        QMETRY_API_TOKEN=os.getenv("QMETRY_API_TOKEN", ""),
        TEAM_NAME=team_name,
        JIRA_PROJECT_KEY=jira_project_key,
        OUTPUT_DIR=output_dir,
        JIRA_CUSTOM_FIELDS=yaml_config.get("jira_custom_fields", {}),
        AUTOMATION_LABEL_PREFIX=yaml_config.get("automation_label_prefix", "automation"),
    )
