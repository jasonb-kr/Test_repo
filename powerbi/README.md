# Power BI Setup Guide

## 1) Connect Power BI Desktop to report files
- Option A (local): **Get Data -> Text/CSV** and select `output/stories.csv` and `output/defects.csv`.
- Option B (GitHub raw URL): **Get Data -> Web** and use raw GitHub URLs for both CSV files.

## 2) Build the data model
- In **Model** view, create relationship:
  - `stories[story_key]` (one) -> `defects[story_key]` (many)
- Cross filter direction: single (stories to defects).

## 3) Suggested visuals
- Stories by Sprint: bar chart (`sprint`, count of `story_key`)
- Defect Count per Story: table (`story_key`, `summary`, `defect_count`)
- Automation Coverage %: donut (`automation_coverage`, count of `story_key`)
- Defect trend over time: line chart (`defects.created_date`, count of `defect_key`)
- Stories with 0 automation: table filtered where `is_automated=false` and `qmetry_automated=false`

## 4) Publish to Power BI Service
- Publish report from Desktop.
- Configure dataset credentials/source for CSV Web endpoints (raw GitHub URLs).
- Configure scheduled refresh in dataset settings.

## 5) Keep report live
- Use Power BI Web connector against raw GitHub CSV URLs.
- The GitHub Actions workflow refreshes files on schedule, and Power BI scheduled refresh pulls latest data.
