"""Version 2: live manufacturing intelligence and knowledge retrieval."""

from __future__ import annotations

from datetime import date
from pathlib import Path
import sys

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from v2_manufacturing_intelligence.analytics import (
    RECORD_COLUMNS, add_kpis, executive_summary, validate_records,
)
from v2_manufacturing_intelligence.bm25_engine import BM25LessonsIndex
from v2_manufacturing_intelligence.briefing import build_engineering_brief
from v2_manufacturing_intelligence.reporting import build_v2_report


DATA = ROOT / "data"
DISCLAIMER = (
    "This public portfolio uses synthetic educational records and generalized engineering "
    "lessons. It contains no proprietary or confidential manufacturing data."
)


def demo_records() -> pd.DataFrame:
    rows = [
        ["2026-07-14", "A", "Body Fit", "Pitch 1", 480, 42, 72, 342, 338, 315, 330, 15, 8, "Gap/flush", "Fixture checks initiated"],
        ["2026-07-14", "A", "Body Fit", "Pitch 2", 480, 31, 72, 338, 334, 321, 329, 8, 5, "Door alignment", "Standard work audit"],
        ["2026-07-14", "A", "Body Fit", "Pitch 3", 480, 28, 72, 334, 331, 319, 326, 7, 5, "Closure fit", "Torque audit"],
        ["2026-07-15", "B", "Body Fit", "Pitch 1", 480, 29, 72, 354, 350, 337, 345, 8, 5, "Gap/flush", "Locator cleaned"],
        ["2026-07-15", "B", "Body Fit", "Pitch 2", 480, 24, 72, 350, 347, 339, 343, 4, 4, "Door alignment", "Training refreshed"],
        ["2026-07-15", "B", "Body Fit", "Pitch 3", 480, 20, 72, 347, 345, 338, 342, 4, 3, "Closure fit", "Stable run"],
    ]
    return pd.DataFrame(rows, columns=RECORD_COLUMNS)


st.set_page_config(page_title="Manufacturing Process Intelligence", page_icon="🏭", layout="wide")
st.title("🏭 Manufacturing Process Intelligence System")
st.caption("Version 2 — live yield analytics, BM25 lessons retrieval, and evidence-grounded engineering reports")
st.info(DISCLAIMER)

if "production_records" not in st.session_state:
    st.session_state.production_records = demo_records()
if "problem_query" not in st.session_state:
    st.session_state.problem_query = "Gap variation increases after fixture maintenance"

lessons = pd.read_csv(DATA / "engineering_lessons.csv")
index = BM25LessonsIndex(lessons)
records = validate_records(st.session_state.production_records)
metrics = executive_summary(records)

tabs = st.tabs([
    "Executive Dashboard", "Live Record Entry", "Yield & OEE",
    "Engineering Lessons", "Engineering Brief", "Report Center", "V1 vs V2",
])

with tabs[0]:
    a, b, c, d, e = st.columns(5)
    a.metric("First Pass Yield", f"{metrics['fpy']:.1%}")
    b.metric("Rolled Throughput Yield", f"{metrics['rty']:.1%}")
    c.metric("Weighted OEE", f"{metrics['weighted_oee']:.1%}")
    d.metric("Reworked", f"{metrics['reworked']:,}")
    e.metric("Scrapped", f"{metrics['scrapped']:,}")
    kpis = add_kpis(records)
    trend = kpis.groupby("date")[["fpy", "oee", "availability", "performance", "quality"]].mean()
    st.subheader("Daily performance trend")
    st.line_chart(trend)
    st.subheader("Defect concentration")
    st.bar_chart(records.groupby("defect_category").scrapped.sum().sort_values(ascending=False))

with tabs[1]:
    st.subheader("Add a production record")
    with st.form("record_form", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns(4)
        record_date = c1.date_input("Date", value=date.today())
        shift = c2.selectbox("Shift", ["A", "B", "C"])
        line = c3.text_input("Line", value="Body Fit")
        station = c4.text_input("Station", value="Pitch 1")
        c1, c2, c3 = st.columns(3)
        planned = c1.number_input("Planned minutes", min_value=1.0, value=480.0)
        downtime = c2.number_input("Downtime minutes", min_value=0.0, value=25.0)
        ideal_cycle = c3.number_input("Ideal cycle seconds", min_value=.1, value=72.0)
        c1, c2, c3, c4, c5 = st.columns(5)
        started = c1.number_input("Units started", min_value=0, value=350)
        completed = c2.number_input("Units completed", min_value=0, value=345)
        first_pass = c3.number_input("First-pass good", min_value=0, value=335)
        final_good = c4.number_input("Final good", min_value=0, value=341)
        reworked = c5.number_input("Reworked", min_value=0, value=6)
        c1, c2, c3 = st.columns(3)
        scrapped = c1.number_input("Scrapped", min_value=0, value=4)
        defect = c2.text_input("Primary defect", value="Gap/flush")
        comment = c3.text_input("Engineering comment", value="")
        submitted = st.form_submit_button("Add verified record", type="primary")
        if submitted:
            row = pd.DataFrame([[
                str(record_date), shift, line, station, planned, downtime, ideal_cycle,
                started, completed, first_pass, final_good, reworked, scrapped, defect, comment,
            ]], columns=RECORD_COLUMNS)
            try:
                updated = validate_records(pd.concat([records, row], ignore_index=True))
                st.session_state.production_records = updated
                st.success("Record added. Dashboard metrics are updated.")
                st.rerun()
            except ValueError as exc:
                st.error(str(exc))
    st.subheader("Current session records")
    edited = st.data_editor(records, width="stretch", num_rows="dynamic")
    c1, c2 = st.columns(2)
    if c1.button("Apply table edits"):
        try:
            st.session_state.production_records = validate_records(edited)
            st.success("Edits validated and applied."); st.rerun()
        except ValueError as exc: st.error(str(exc))
    c2.download_button(
        "Download production records CSV", records.to_csv(index=False).encode(),
        "v2_production_records.csv", "text/csv",
    )
    uploaded = st.file_uploader("Restore or analyze a production-record CSV", type="csv")
    if uploaded and st.button("Load uploaded records"):
        try:
            st.session_state.production_records = validate_records(pd.read_csv(uploaded))
            st.success("CSV validated and loaded."); st.rerun()
        except ValueError as exc: st.error(str(exc))

with tabs[2]:
    st.subheader("Station-level yield and equipment effectiveness")
    kpis = add_kpis(records)
    display = kpis[["date", "shift", "station", "fpy", "availability", "performance", "quality", "oee"]]
    st.dataframe(display.style.format({c: "{:.1%}" for c in ["fpy", "availability", "performance", "quality", "oee"]}), width="stretch")
    station = kpis.groupby("station")[["fpy", "oee"]].mean()
    st.bar_chart(station)
    st.caption("RTY multiplies station-level first-pass yields. Final yield can hide rework; RTY exposes accumulated process loss.")

with tabs[3]:
    st.subheader("BM25 engineering lessons retrieval")
    query = st.text_area("Describe the technical problem", value=st.session_state.problem_query)
    top_k = st.slider("Number of lessons", 1, 8, 5)
    if st.button("Search engineering lessons", type="primary") or query:
        st.session_state.problem_query = query
        matches = index.search(query, top_k=top_k)
        if matches.empty:
            st.warning("No matching lesson found. Broaden the problem description.")
        for row in matches.itertuples():
            with st.expander(f"{row.lesson_id} · {row.problem} · BM25 {row.bm25_score:.2f}", expanded=True):
                st.markdown(f"**Component:** {row.component}")
                st.markdown(f"**Root cause:** {row.root_cause}")
                st.markdown(f"**Containment:** {row.containment}")
                st.markdown(f"**Corrective action:** {row.corrective_action}")
                st.markdown(f"**Verification:** {row.verification}")

with tabs[4]:
    query = st.session_state.problem_query
    matches = index.search(query, top_k=5)
    brief = build_engineering_brief(query, matches, metrics)
    st.markdown(brief)
    st.warning("Human approval required: this is decision support, not an automatic production disposition.")
    st.caption("The current public version uses traceable BM25 evidence and deterministic briefing. An optional credentialed LLM layer can be added later without changing the KPI or retrieval authority.")

with tabs[5]:
    query = st.session_state.problem_query
    matches = index.search(query, top_k=5)
    brief = build_engineering_brief(query, matches, metrics)
    report = build_v2_report(records, metrics, query, matches, brief)
    st.subheader("Integrated report package")
    st.write("The Word report combines live-session KPIs, production records, retrieved lessons, corrective-action evidence, and the engineering brief.")
    st.download_button(
        "Download Manufacturing Intelligence Report", report,
        "Manufacturing_Process_Intelligence_Report.docx",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        type="primary",
    )

with tabs[6]:
    st.subheader("Recommended application level")
    comparison = pd.DataFrame([
        ["Purpose", "Validated engineering analytics", "Integrated production intelligence"],
        ["Data", "Synthetic/uploaded study data", "Session-based live records + CSV backup"],
        ["Core methods", "Cp/Cpk, PFMEA, OEE, GR&R, SPC", "FPY, RTY, OEE, BM25, reports"],
        ["Knowledge retrieval", "No", "Traceable BM25 lessons"],
        ["Engineering brief", "Statistical interpretation", "Evidence-grounded investigation brief"],
        ["Best use", "Calculation authority", "Decision-support and management visibility"],
    ], columns=["Decision factor", "Version 1", "Version 2"])
    st.dataframe(comparison, width="stretch", hide_index=True)
    st.success("Recommended architecture: Version 1 remains the validated analytical core; Version 2 adds intelligence and decision support.")
