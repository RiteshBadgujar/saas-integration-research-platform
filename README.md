# SaaS Integration Intelligence & Research Automation

A research and analysis project for evaluating the integration readiness of 100 SaaS products. It combines source-backed product research, structured datasets, a 30-app manual verification sample, and a standalone interactive dashboard.

## Objectives

- Compare SaaS APIs and integration considerations across product categories.
- Document authentication, credential access, API capabilities, webhooks, MCP support, and implementation buildability.
- Validate the curated research dataset and compare automated assessments with a manually reviewed sample.
- Present findings in a filterable dashboard for product and integration planning.

## Features and Methodology

Research scripts collect and normalize product and developer-documentation facts, classify authentication and buildability, and validate records against the project schema.

The analysis scripts compute category summaries and research recommendations from the stored data. Verification records preserve the comparison between automated predictions and a manually reviewed sample.

The dashboard is a standalone `index.html` file with data embedded in the page. It presents charts, category summaries, recommendations, and searchable and filterable app and audit tables.

**Note:** Chart.js is loaded from a CDN, so chart rendering requires an internet connection.

## Dataset and Verification

The curated dataset contains **100 SaaS apps across 10 categories**.

- `data/apps.json` and `data/apps.csv`: Full research dataset.
- `data/seed_apps.json`: Seed catalog and manual-review sample metadata.
- `data/categories.json`: Category definitions and related context.
- `verification/`: Automated results, manual sample, final verification records, and accuracy report. The manual audit covers **30 apps**.
- `reports/`: Category analysis and research summary outputs used by the dashboard.

## Research and Validation Scripts

Key research scripts in `research/` include:

- `researcher.py`, `source_collector.py`: Research workflow and source collection.
- `facts_builder.py`, `generate_all_facts.py`, `verified_facts.py`: Fact-building and verified research data.
- `auth_analyzer.py`, `buildability_classifier.py`: Authentication and buildability analysis.
- `data_validator.py`: Seed-catalog and full-dataset validation.
- `url_liveness_checker.py`: Source URL checks.

Key scripts in `reports/` and `verification/` include:

- `reports/analyzer.py`: Calculate category analysis and research summary.
- `reports/validate_html.py`: Check dashboard structure and embedded data.
- `reports/test_html.py`: Exercise dataset, filtering, and summary integrity checks.
- `verification/verifier.py`: Run the manual verification workflow.

The analysis and generation scripts may write project outputs. The validation commands below are the recommended read-only checks; they do not rebuild the dashboard or regenerate reports.

## Requirements and Installation

Requirements:

- Python 3.10 or later.
- Dependencies listed in `requirements.txt`, including Pydantic, Requests, Beautiful Soup, pandas, Rich, and urllib3.
- Internet access for dashboard charts and research tasks that fetch online sources.

Create and activate a virtual environment, then install the dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

The screenshot utility under `screenshots/` is separate from dashboard operation and uses Puppeteer. Its npm manifests are retained there; Node.js is only needed if using that utility.

## Validation and Tests

Run these commands from the project root:

```powershell
$env:PYTHONIOENCODING = "utf-8"
python -m research.data_validator --mode all
python -m reports.validate_html
python -m reports.test_html
```

Setting `PYTHONIOENCODING` ensures Unicode test output, such as checkmarks, works in Windows terminals using a legacy code page.

## Run the Dashboard

Open `index.html` in a web browser.

The dashboard uses Chart.js from a CDN, so an internet connection is required for chart rendering.

## Project Structure

```text
.
├── data/           Curated app datasets and category definitions
├── reports/        Analysis outputs, report scripts, and HTML checks
├── research/       Research, fact-building, classification, and validation
├── scratch/        Research checkpoint and local cache
├── screenshots/    Optional Puppeteer screenshot utility and npm manifests
├── verification/   Manual and automated audit records and verifier
├── index.html      Interactive SaaS integration dashboard
├── requirements.txt
├── .gitignore
└── README.md
```