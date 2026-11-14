"""Plain-Python tools for the dbt triage agent.

Every function here works without any LLM, so you can test each one on its own:
    python -c "import agent_tools as t; print(t.get_failures())"

Read-only by design: SQL goes through the AGENT_RO role, and propose_patch only
writes a review file under patches/ (it never edits the dbt project).
"""
import difflib
import json
import re
from datetime import datetime
from pathlib import Path

from common import DBT_DIR, PATCHES_DIR, get_connection

TARGET_DIR = DBT_DIR / "target"
MAX_ROWS = 50
MAX_PROFILE_COLUMNS = 40


# ----------------------------------------------------------------- artifacts
def _latest_run_results() -> Path | None:
    """Newest run_results.json. Dagster runs write to target/<invocation>/, so search recursively."""
    files = list(TARGET_DIR.rglob("run_results.json"))
    return max(files, key=lambda p: p.stat().st_mtime) if files else None


def _load_manifest(run_results_path: Path | None = None) -> dict:
    run_results_path = run_results_path or _latest_run_results()
    candidates = []
    if run_results_path:
        candidates.append(run_results_path.parent / "manifest.json")
    candidates.append(TARGET_DIR / "manifest.json")
    for path in candidates:
        if path.exists():
            return json.loads(path.read_text())
    return {}


def _find_node(manifest: dict, name: str) -> tuple[str | None, dict]:
    for uid, node in manifest.get("nodes", {}).items():
        if node.get("name") == name or uid == name:
            return uid, node
    return None, {}


def _jsonable(value):
    return value if isinstance(value, (int, float, str, bool, type(None))) else str(value)


# --------------------------------------------------------------------- tools
def get_failures() -> list[dict]:
    """Failed or warned nodes from the most recent dbt run (errors, failed tests, warnings)."""
    rr_path = _latest_run_results()
    if rr_path is None:
        return []
    run_results = json.loads(rr_path.read_text())
    nodes = _load_manifest(rr_path).get("nodes", {})

    failures = []
    for result in run_results.get("results", []):
        if result.get("status") not in ("error", "fail", "warn"):
            continue
        uid = result["unique_id"]
        node = nodes.get(uid, {})
        item = {
            "unique_id": uid,
            "name": node.get("name"),
            "resource_type": node.get("resource_type"),
            "status": result["status"],
            "message": result.get("message"),
            "failing_rows": result.get("failures"),
            "file": node.get("original_file_path"),
            "compiled_code": (result.get("compiled_code") or "")[:1500],
            "depends_on": node.get("depends_on", {}).get("nodes", []),
        }
        meta = node.get("test_metadata")
        if meta:
            item["test"] = {
                "type": meta.get("name"),
                "kwargs": meta.get("kwargs"),
                "column": node.get("column_name"),
                "attached_node": node.get("attached_node"),
            }
        failures.append(item)
    return failures


def get_model_sql(name: str) -> dict:
    """Raw SQL and file path for a dbt model, snapshot or test, looked up by name."""
    manifest = _load_manifest()
    uid, node = _find_node(manifest, name)
    if not node:
        return {"found": False, "error": f"No dbt node named {name!r}"}
    return {
        "found": True,
        "unique_id": uid,
        "resource_type": node.get("resource_type"),
        "file": node.get("original_file_path"),
        "raw_code": node.get("raw_code"),
    }


def get_lineage(name: str) -> dict:
    """Direct parents and children of a dbt node."""
    manifest = _load_manifest()
    uid, node = _find_node(manifest, name)
    if not node:
        return {"found": False, "error": f"No dbt node named {name!r}"}
    children = manifest.get("child_map", {}).get(uid, [])
    child_nodes = [c for c in children if not c.startswith("test.")]
    return {
        "found": True,
        "unique_id": uid,
        "parents": manifest.get("parent_map", {}).get(uid, []),
        "children": child_nodes,
        "attached_tests": len(children) - len(child_nodes),
    }


_FORBIDDEN = re.compile(
    r"\b(insert|update|delete|merge|drop|alter|create|grant|revoke|copy|put|get|remove|truncate|call|use)\b",
    re.IGNORECASE,
)


def check_sql_is_read_only(sql: str) -> str | None:
    """Return an error message if the SQL is not a single read-only SELECT/WITH, else None."""
    query = sql.strip().rstrip(";").strip()
    if not query:
        return "Empty query"
    if ";" in query:
        return "Only a single statement is allowed"
    if not re.match(r"(?is)^(select|with)\b", query):
        return "Only SELECT or WITH queries are allowed"
    if _FORBIDDEN.search(query):
        return "Query contains a forbidden keyword (read-only access only)"
    return None


def run_sql(sql: str) -> dict:
    """Run a read-only query as AGENT_RO. Returns at most 50 rows."""
    error = check_sql_is_read_only(sql)
    if error:
        return {"error": error}
    query = sql.strip().rstrip(";").strip()
    conn = None
    try:
        conn = get_connection(role="AGENT_RO")
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM ({query}) LIMIT {MAX_ROWS}")
        return {
            "columns": [c[0] for c in cur.description],
            "rows": [[_jsonable(v) for v in row] for row in cur.fetchall()],
            "row_limit": MAX_ROWS,
        }
    except Exception as exc:  # noqa: BLE001 - surface the DB error to the agent
        return {"error": str(exc)}
    finally:
        if conn:
            conn.close()


_IDENTIFIER = re.compile(r"^[A-Za-z0-9_$]+(\.[A-Za-z0-9_$]+){0,2}$")


def profile_table(table: str) -> dict:
    """Row count plus nulls, distinct count, min and max for each column of a table or view."""
    if not _IDENTIFIER.match(table):
        return {"error": "Table must look like DATABASE.SCHEMA.NAME (letters, digits, _ and $ only)"}
    conn = None
    try:
        conn = get_connection(role="AGENT_RO")
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {table} LIMIT 0")
        columns = [c[0] for c in cur.description][:MAX_PROFILE_COLUMNS]

        parts = ["COUNT(*) AS ROW_COUNT"]
        for col in columns:
            parts += [
                f'COUNT_IF("{col}" IS NULL) AS "{col}__NULLS"',
                f'COUNT(DISTINCT "{col}") AS "{col}__DISTINCT"',
                f'MIN("{col}") AS "{col}__MIN"',
                f'MAX("{col}") AS "{col}__MAX"',
            ]
        cur.execute(f"SELECT {', '.join(parts)} FROM {table}")
        names = [c[0] for c in cur.description]
        row = dict(zip(names, cur.fetchone()))

        return {
            "table": table,
            "row_count": row["ROW_COUNT"],
            "columns": {
                col: {
                    "nulls": row[f"{col}__NULLS"],
                    "distinct": row[f"{col}__DISTINCT"],
                    "min": _jsonable(row[f"{col}__MIN"]),
                    "max": _jsonable(row[f"{col}__MAX"]),
                }
                for col in columns
            },
        }
    except Exception as exc:  # noqa: BLE001
        return {"error": str(exc)}
    finally:
        if conn:
            conn.close()


def propose_patch(file: str, new_content: str, rationale: str) -> dict:
    """Write a proposed change to patches/ for human review. Never edits the dbt project."""
    target = (DBT_DIR / file).resolve()
    if not target.is_relative_to(DBT_DIR.resolve()):
        return {"error": "File must be inside the dbt project folder"}
    if target.suffix not in {".sql", ".yml", ".yaml"}:
        return {"error": "Only .sql, .yml and .yaml files can be patched"}

    current = target.read_text() if target.exists() else ""
    diff = "".join(
        difflib.unified_diff(
            current.splitlines(keepends=True),
            new_content.splitlines(keepends=True),
            fromfile=f"a/{file}",
            tofile=f"b/{file}",
        )
    )
    fence = "`" * 3
    PATCHES_DIR.mkdir(parents=True, exist_ok=True)
    out = PATCHES_DIR / f"{datetime.now():%Y%m%d_%H%M%S}_{target.name}.md"
    out.write_text(
        f"# Proposed patch: `{file}`\n\n"
        f"## Rationale\n{rationale}\n\n"
        f"## Diff\n{fence}diff\n{diff or '(no changes)'}\n{fence}\n\n"
        f"## Full proposed file\n{fence}\n{new_content}\n{fence}\n\n"
        f"_Review before applying. The agent never modifies the project itself._\n"
    )
    return {"patch_file": str(out)}