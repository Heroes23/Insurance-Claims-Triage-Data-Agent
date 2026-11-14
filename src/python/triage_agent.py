"""LangGraph triage agent.

Flow:  load_failures -> (no failures? stop) -> triage (Claude + tools) -> save_report

Run after a failed dbt build / dbt test:
    python src/python/triage_agent.py
"""
import json
import os
from datetime import datetime
from typing import TypedDict

from langchain.agents import create_agent
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langgraph.graph import END, START, StateGraph

import agent_tools as t
from common import REPORTS_DIR

SYSTEM_PROMPT = """You are a data engineering triage agent for an auto insurance dbt pipeline on Snowflake.

You are given failed or warned dbt nodes from the latest run. For each failure:
1. Inspect it: use get_model_sql and get_lineage to understand the node and its parents.
2. Gather evidence with read-only SQL (run_sql, profile_table). Look at the actual failing rows.
   Data lives in INSURANCE_DB: RAW.AUTO_INSURANCE_BATCHES (raw text, one row per customer per
   batch, BATCH_DATE = batch) and ANALYTICS.STG_AUTO_INSURANCE (cleaned view).
3. Classify the root cause as exactly one of:
   - BAD_UPSTREAM_DATA: the source batch contains bad values (duplicates, nulls, invalid categories, bad dates).
   - MODEL_LOGIC: the dbt SQL or test definition is wrong.
   - SCHEMA_DRIFT: columns were added, removed or renamed upstream.
   - INFRASTRUCTURE: warehouse, permissions or connection problem.
4. If a dbt file should change, call propose_patch with the full new file content and a short rationale.
   Do not propose a patch when the right fix is to correct or reload the upstream batch.

Rules:
- You are read-only. Never claim to have changed data or code; propose_patch only writes a review file.
- Back every claim with evidence from a query. Quote the offending values or counts.
- If evidence is inconclusive, say so rather than guessing.

Finish with a markdown report using these headings:
## Summary
## Findings   (one subsection per failure: root cause category, evidence, impact)
## Recommended actions   (ordered, concrete)
"""


# ---------------------------------------------------------------------- tools
@tool
def get_model_sql(name: str) -> dict:
    """Get the raw SQL and file path of a dbt model, snapshot or test by its name."""
    return t.get_model_sql(name)


@tool
def get_lineage(name: str) -> dict:
    """Get the direct parents and children of a dbt node by its name."""
    return t.get_lineage(name)


@tool
def run_sql(sql: str) -> dict:
    """Run one read-only SELECT/WITH query against Snowflake (max 50 rows returned)."""
    return t.run_sql(sql)


@tool
def profile_table(table: str) -> dict:
    """Profile a table or view (DATABASE.SCHEMA.NAME): row count, nulls, distinct, min and max per column."""
    return t.profile_table(table)


@tool
def propose_patch(file: str, new_content: str, rationale: str) -> dict:
    """Write a proposed fix for a dbt file (path relative to the dbt folder, e.g. models/staging/x.sql) for human review."""
    return t.propose_patch(file, new_content, rationale)


TOOLS = [get_model_sql, get_lineage, run_sql, profile_table, propose_patch]


# ---------------------------------------------------------------------- graph
class TriageState(TypedDict, total=False):
    failures: list[dict]
    analysis: str
    report_path: str


def _text(content) -> str:
    """ChatAnthropic content can be a string or a list of blocks."""
    if isinstance(content, str):
        return content
    return "".join(
        block.get("text", "") if isinstance(block, dict) else str(block) for block in content
    )


def load_failures(state: TriageState) -> TriageState:
    return {"failures": t.get_failures()}


def route(state: TriageState) -> str:
    return "triage" if state.get("failures") else END


def triage(state: TriageState) -> TriageState:
    model = ChatAnthropic(
        model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-5-5"),
        max_tokens=4096,
    )
    agent = create_agent(model, TOOLS, system_prompt=SYSTEM_PROMPT)
    payload = json.dumps(state["failures"], indent=2, default=str)[:12000]
    result = agent.invoke(
        {"messages": [("user", f"Latest dbt run failures:\n{payload}")]},
        config={"recursion_limit": 30},
    )
    return {"analysis": _text(result["messages"][-1].content)}


def save_report(state: TriageState) -> TriageState:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORTS_DIR / f"triage_{datetime.now():%Y%m%d_%H%M%S}.md"
    names = ", ".join(f"`{f['name']}` ({f['status']})" for f in state["failures"])
    path.write_text(
        f"# dbt triage report\n\n"
        f"_Generated {datetime.now():%Y-%m-%d %H:%M:%S}_\n\n"
        f"**Failing nodes:** {names}\n\n"
        f"{state['analysis']}\n"
    )
    return {"report_path": str(path)}


def build_graph():
    graph = StateGraph(TriageState)
    graph.add_node("load_failures", load_failures)
    graph.add_node("triage", triage)
    graph.add_node("save_report", save_report)
    graph.add_edge(START, "load_failures")
    graph.add_conditional_edges("load_failures", route, {"triage": "triage", END: END})
    graph.add_edge("triage", "save_report")
    graph.add_edge("save_report", END)
    return graph.compile()


def run_triage() -> str | None:
    """Run the agent. Returns the report path, or None if the last dbt run had no failures."""
    result = build_graph().invoke({})
    return result.get("report_path")


if __name__ == "__main__":
    report = run_triage()
    print(f"Report written: {report}" if report else "No failures in the latest dbt run.")