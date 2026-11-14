"""Streamlit dashboard: loss ratio, segment performance, and agent triage reports.

Run:  streamlit run src/python/streamlit_app.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd  # noqa: E402
import streamlit as st  # noqa: E402

from common import REPORTS_DIR, get_connection  # noqa: E402

st.set_page_config(page_title="Auto insurance pipeline", layout="wide")


@st.cache_data(ttl=300)
def query(sql: str) -> pd.DataFrame:
    """Read-only query as AGENT_RO, cached for 5 minutes to save warehouse credits."""
    conn = get_connection(role="AGENT_RO")
    try:
        cur = conn.cursor()
        cur.execute(sql)
        df = pd.DataFrame(cur.fetchall(), columns=[c[0].lower() for c in cur.description])
    finally:
        conn.close()
    for col in df.columns:  # Snowflake returns Decimal objects
        try:
            df[col] = pd.to_numeric(df[col])
        except (ValueError, TypeError):
            pass
    return df


def loss_ratio_page() -> None:
    st.title("Estimated loss ratio")
    st.caption(
        "Loss ratio = total claim amount / estimated earned premium "
        "(monthly premium x months since policy inception)."
    )
    df = query("select * from INSURANCE_DB.ANALYTICS.MART_LOSS_RATIO")

    left, right = st.columns(2)
    states = left.multiselect("State", sorted(df["state"].unique()))
    coverages = right.multiselect("Coverage", sorted(df["coverage"].unique()))
    if states:
        df = df[df["state"].isin(states)]
    if coverages:
        df = df[df["coverage"].isin(coverages)]

    claims, premium = df["total_claim_amount"].sum(), df["estimated_earned_premium"].sum()
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Policies", f"{int(df['policy_count'].sum()):,}")
    k2.metric("Total claims", f"${claims:,.0f}")
    k3.metric("Est. earned premium", f"${premium:,.0f}")
    k4.metric("Loss ratio", f"{claims / premium:.1%}" if premium else "n/a")

    def ratio_by(column: str) -> pd.DataFrame:
        grouped = df.groupby(column)[["total_claim_amount", "estimated_earned_premium"]].sum()
        grouped["loss_ratio"] = grouped["total_claim_amount"] / grouped["estimated_earned_premium"]
        return grouped

    c1, c2 = st.columns(2)
    c1.subheader("By state")
    c1.bar_chart(ratio_by("state")["loss_ratio"])
    c2.subheader("By vehicle class")
    c2.bar_chart(ratio_by("vehicle_class")["loss_ratio"])

    st.subheader("Detail")
    st.dataframe(df.sort_values("estimated_loss_ratio", ascending=False))


def segment_page() -> None:
    st.title("Segment performance")
    df = query("select * from INSURANCE_DB.ANALYTICS.MART_SEGMENT_PERFORMANCE")

    c1, c2 = st.columns(2)
    c1.subheader("Renewal response rate by offer type")
    by_offer = df.groupby("renew_offer_type").apply(
        lambda g: (g["renewal_response_rate"] * g["policy_count"]).sum() / g["policy_count"].sum(),
        include_groups=False,
    )
    c1.bar_chart(by_offer)
    c2.subheader("Policies by sales channel")
    c2.bar_chart(df.groupby("sales_channel")["policy_count"].sum())

    st.subheader("Detail")
    st.dataframe(df)


def reports_page() -> None:
    st.title("Agent triage reports")
    reports = sorted(REPORTS_DIR.glob("triage_*.md"), reverse=True)
    if not reports:
        st.info("No reports yet. Run poison_batch.py, then dbt test, then triage_agent.py.")
        return
    chosen = st.selectbox("Report", reports, format_func=lambda p: p.name)
    st.markdown(chosen.read_text())


PAGES = {"Loss ratio": loss_ratio_page, "Segments": segment_page, "Agent reports": reports_page}
PAGES[st.sidebar.radio("Page", list(PAGES))]()