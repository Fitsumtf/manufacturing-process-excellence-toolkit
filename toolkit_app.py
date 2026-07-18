"""Classic V1 all-in-one manufacturing process excellence portfolio."""

from pathlib import Path

import pandas as pd
import streamlit as st

from automotive_body_fit.analysis import analyze_capability, load_measurements
from manufacturing_toolkit.gage_rr import crossed_gage_rr
from manufacturing_toolkit.oee import calculate_oee
from manufacturing_toolkit.pfmea import analyze_pfmea
from manufacturing_toolkit.process_data import imr_chart_data, pareto_summary
from manufacturing_toolkit.report import DISCLAIMER

DATA = Path("data")
st.set_page_config(page_title="Manufacturing Process Excellence Toolkit", layout="wide")
st.title("Manufacturing Process Excellence Toolkit")
st.caption("Cp/Cpk • PFMEA • OEE • Gauge R&R • SPC • Process Improvement")
st.info(DISCLAIMER)

tabs = st.tabs(["Capability", "PFMEA", "OEE", "Gauge R&R", "Process Data", "Case Studies"])

with tabs[0]:
    values = load_measurements(DATA / "automotive_body_fit_100_samples.csv")
    c1, c2, c3 = st.columns(3)
    lsl = c1.number_input("LSL", value=3.0)
    target = c2.number_input("Target", value=3.5)
    usl = c3.number_input("USL", value=4.0)
    cap = analyze_capability(values, lsl=lsl, target=target, usl=usl)
    cols = st.columns(4)
    labels = ["Mean", "Sample STDEV", "Cp", "Cpk"]
    results = [f"{cap.mean:.6f}", f"{cap.sample_stdev:.6f}", f"{cap.cp:.3f}", f"{cap.cpk:.3f}"]
    for col, label, result in zip(cols, labels, results):
        col.metric(label, result)
    st.warning(cap.status)
    st.line_chart(pd.DataFrame({"measurement_mm": values}))

with tabs[1]:
    pfmea = analyze_pfmea(pd.read_csv(DATA / "synthetic_pfmea.csv"))
    st.caption("Portfolio priority is educational triage, not the AIAG-VDA Action Priority table.")
    st.dataframe(pfmea, width="stretch")
    st.bar_chart(pfmea.set_index("failure_mode")[["rpn", "revised_rpn"]])

with tabs[2]:
    oee_data = pd.read_csv(DATA / "synthetic_oee_data.csv")
    rows = []
    for row in oee_data.to_dict("records"):
        date = row.pop("date")
        result = calculate_oee(**row)
        rows.append({
            "date": date, "availability": result.availability,
            "performance": result.performance, "quality": result.quality,
            "oee": result.oee,
        })
    trend = pd.DataFrame(rows).set_index("date")
    st.dataframe(trend.style.format("{:.1%}"), width="stretch")
    st.line_chart(trend)

with tabs[3]:
    grr_data = pd.read_csv(DATA / "synthetic_gage_rr_data.csv")
    grr = crossed_gage_rr(grr_data)
    g1, g2, g3 = st.columns(3)
    g1.metric("Total GR&R", f"{grr.percent_study_variation_grr:.2f}%")
    g2.metric("ndc", grr.ndc)
    g3.metric("Result", grr.interpretation)
    st.dataframe(grr_data, width="stretch")

with tabs[4]:
    defects = pd.read_csv(DATA / "synthetic_defect_data.csv")
    pareto = pareto_summary(defects, "defect_category", "count")
    st.dataframe(pareto, width="stretch")
    st.bar_chart(pareto.set_index("defect_category")["count"])
    ordered = load_measurements(DATA / "automotive_body_fit_100_samples.csv")
    limits = imr_chart_data(ordered)
    st.write(
        f"I-chart center: {limits['center']:.4f}; "
        f"UCL: {limits['i_ucl']:.4f}; LCL: {limits['i_lcl']:.4f}"
    )

with tabs[5]:
    for path in sorted(Path("case_studies").glob("*.md")):
        with st.expander(path.stem.replace("_", " ").title()):
            st.markdown(path.read_text())
