# Jira Story Defect + Automation Pipeline

This project builds a Python data pipeline to pull Jira stories for a team, map linked defects, enrich automation state from Jira labels and QMetry, and export flat files for Power BI live reporting.

## Setup
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy environment template and configure secrets:
   ```bash
   cp .env.example .env
   ```
4. Update `config.yaml` for project/team-specific settings.

## Run locally
```bash
python run_report.py
```
Outputs are written to `output/` as:
- `stories.csv`, `defects.csv`
- `stories.json`, `defects.json`

## GitHub Actions automation
Workflow: `.github/workflows/refresh_report.yml`
- Schedule: weekdays at 06:00 UTC
- Manual trigger: `workflow_dispatch`
- Executes pipeline and commits refreshed output files
- Uses GitHub Secrets for Jira/QMetry credentials

## Power BI integration
See `/powerbi/README.md` for step-by-step setup of model relationships, visuals, and scheduled refresh.

## Customization
- Team/project: `config.yaml` and env vars
- Jira custom fields: `config.yaml -> jira_custom_fields`
- Automation label behavior: `automation_label_prefix`
