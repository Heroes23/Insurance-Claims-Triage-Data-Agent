"""Dagster definitions: partitioned batch ingest -> dbt build, plus a schedule and a failure sensor.

Run the UI from the repo root:
    dagster dev -f src/python/dagster_defs.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from dagster import (  # noqa: E402
    AssetExecutionContext,
    AssetSelection,
    DailyPartitionsDefinition,
    DefaultSensorStatus,
    Definitions,
    MaterializeResult,
    RunFailureSensorContext,
    ScheduleDefinition,
    asset,
    define_asset_job,
    run_failure_sensor,
)
from dagster_dbt import DbtCliResource, DbtProject, dbt_assets  # noqa: E402

from common import DBT_DIR  # noqa: E402  (also loads .env)
from ingest import load_batch  # noqa: E402

# 59 daily batches: 2026-01-01 .. 2026-02-28 (end date is exclusive)
daily_batches = DailyPartitionsDefinition(start_date="2026-01-01", end_date="2026-03-01")


# The asset key matches dbt's source('raw', 'auto_insurance_batches'),
# so Dagster draws the lineage ingest -> staging -> marts automatically.
@asset(
    key=["raw", "auto_insurance_batches"],
    partitions_def=daily_batches,
    group_name="ingest",
    description="Daily CSV batch loaded into RAW.AUTO_INSURANCE_BATCHES with PUT + COPY INTO.",
)
def raw_auto_insurance_batches(context: AssetExecutionContext) -> MaterializeResult:
    result = load_batch(context.partition_key)
    context.log.info(f"Loaded batch: {result}")
    return MaterializeResult(metadata=result)


dbt_project = DbtProject(project_dir=DBT_DIR, profiles_dir=DBT_DIR)
dbt_project.prepare_if_dev()


@dbt_assets(manifest=dbt_project.manifest_path)
def insurance_dbt_assets(context: AssetExecutionContext, dbt: DbtCliResource):
    yield from dbt.cli(["build"], context=context).stream()


ingest_job = define_asset_job(
    "ingest_daily_batch",
    selection=AssetSelection.assets(raw_auto_insurance_batches),
    partitions_def=daily_batches,
)
dbt_job = define_asset_job("dbt_build", selection=AssetSelection.assets(insurance_dbt_assets))

dbt_schedule = ScheduleDefinition(job=dbt_job, cron_schedule="0 6 * * *")


@run_failure_sensor(
    name="triage_on_dbt_failure",
    monitored_jobs=[dbt_job],
    default_status=DefaultSensorStatus.STOPPED,  # turn on in the UI when you want it
)
def triage_on_dbt_failure(context: RunFailureSensorContext):
    from triage_agent import run_triage

    report = run_triage()
    context.log.info(f"Triage report: {report}")


defs = Definitions(
    assets=[raw_auto_insurance_batches, insurance_dbt_assets],
    jobs=[ingest_job, dbt_job],
    schedules=[dbt_schedule],
    sensors=[triage_on_dbt_failure],
    resources={"dbt": DbtCliResource(project_dir=dbt_project, profiles_dir=str(DBT_DIR))},
)