## Insurance Claims Data Agent 

Batch data pipeline for insurance claims on Snowflake (dbt + Dagster), with a LangGraph agent that diagnoses failed pipeline runs and proposes fixes.

> **Status:** work in progress (weekend build). See the [roadmap](#roadmap).

## Overview

Daily claims files land in Snowflake, get transformed by dbt into analytics-ready marts, and are orchestrated by Dagster. When a dbt run or test fails, an AI agent reads the run artifacts, inspects the data with read-only queries, classifies the root cause, and writes a triage report with a suggested patch. A human reviews it; nothing is applied automatically.

## Architecture

```
daily CSV batches
      │  PUT + COPY INTO
      ▼
Snowflake RAW ──► dbt (staging → intermediate → marts) ──► Streamlit dashboard
      ▲                      │
      │                      ▼ on failure
 Dagster (partitions,   run_results.json / manifest.json
 schedule, sensor)            │
                              ▼
                  LangGraph triage agent (Claude)
                  tools: failures · model SQL · lineage ·
                         read-only SQL · table profile · propose patch
                              │
                              ▼
                      reports/*.md  +  patches/
```

## Stack

| Layer | Tool |
|---|---|
| Warehouse | Snowflake |
| Transformation | dbt (dbt-snowflake) |
| Orchestration | Dagster (`dagster-dbt`) |
| Agent | LangGraph + LangChain + Anthropic SDK (Claude) |
| Dashboard | Streamlit |
| Language | Python, SQL |

## Design decisions

- **Least privilege:** the agent and dashboard use a read-only Snowflake role (`AGENT_RO`); dbt and ingest use `TRANSFORMER`.
- **Human in the loop:** the agent proposes patches as files and never modifies the dbt project.
- **Idempotent batch loads:** daily partitions, re-runnable without duplicating rows.
- **Loose RAW, strict staging:** raw data is loaded as-is; typing and cleaning happen in dbt.

## Data models (planned)

- **Staging:** `stg_policies`, `stg_claims`, ...
- **Snapshot:** policies (SCD2)
- **Marts:** claim frequency and severity, earned premium, loss ratio by state / line / month
- **Tests:** unique, not_null, relationships, accepted_values, plus business-rule tests (e.g. paid ≤ incurred)

## Project structure

```
├── dbt_project/        # models, snapshots, tests, profiles
├── orchestration/      # Dagster definitions
├── ingest/             # stage + COPY INTO loader
├── agent/              # tools.py, graph.py
├── app/                # Streamlit dashboard
├── reports/            # agent triage reports
├── patches/            # agent-proposed fixes (for review)
└── README.md
```

## Setup

```bash
git clone <repo-url> && cd insurance-claims-triage-data-agent
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add Snowflake + Anthropic credentials
```

Required environment variables (see `.env.example`):

`SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD`, `SNOWFLAKE_ROLE`, `SNOWFLAKE_WAREHOUSE`, `SNOWFLAKE_DATABASE`, `ANTHROPIC_API_KEY`

## Usage

```bash
# Orchestration UI
dagster dev -f orchestration/definitions.py

# Dashboard
streamlit run app/streamlit_app.py

# Agent (after a failed dbt build)
python -m agent.graph
```

## Roadmap

- [ ] Snowflake setup (database, schemas, roles, warehouse)
- [ ] Batch ingest (stage + COPY INTO)
- [ ] dbt staging models and tests
- [ ] Snapshot and marts (loss ratio)
- [ ] Dagster partitions, schedule, failure sensor
- [ ] Triage agent (LangGraph) with read-only tools
- [ ] Poison-batch demo (duplicates, nulls, schema drift)
- [ ] Streamlit dashboard + agent reports page
- [ ] CI: `dbt build` on pull requests

## Dataset

Describe the source, size, and any synthetic or anonymized data here. Do not commit real policyholder data.
