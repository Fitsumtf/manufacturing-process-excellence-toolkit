from pathlib import Path
import tempfile

import pandas as pd
import streamlit as st

from automotive_body_fit.analysis import analyze_capability
from automotive_body_fit.plots import capability_histogram, run_chart
from automotive_body_fit.report import DISCLAIMER, build_report

st.set_page_config(page_title="Automotive Body Fit Cp/Cpk", layout="wide")
st.title("Automotive Body Fit Cp/Cpk Analyzer")
st.caption("High-Volume Automotive OEM — synthetic educational capability study")
st.info(DISCLAIMER)

uploaded = st.file_uploader("Upload a CSV containing measurement_mm", type="csv")
default_path = Path("data/automotive_body_fit_100_samples.csv")
frame = pd.read_csv(uploaded) if uploaded else pd.read_csv(default_path)

c1, c2, c3 = st.columns(3)
lsl = c1.number_input("LSL (mm)", value=3.000, format="%.3f")
target = c2.number_input("Target (mm)", value=3.500, format="%.3f")
usl = c3.number_input("USL (mm)", value=4.000, format="%.3f")

try:
    values = pd.to_numeric(frame["measurement_mm"], errors="raise").to_numpy(dtype=float)
    result = analyze_capability(values, lsl=lsl, target=target, usl=usl)
except (KeyError, ValueError) as exc:
    st.error(str(exc)); st.stop()

m1, m2, m3, m4 = st.columns(4)
m1.metric("Mean", f"{result.mean:.6f} mm")
m2.metric("Sample STDEV", f"{result.sample_stdev:.6f} mm")
m3.metric("Cp", f"{result.cp:.3f}")
m4.metric("Cpk", f"{result.cpk:.3f}")
st.subheader(result.status)

with tempfile.TemporaryDirectory() as temp:
    temp = Path(temp)
    hist = capability_histogram(values, result, temp / "hist.png")
    run = run_chart(values, result, temp / "run.png")
    p1, p2 = st.columns(2); p1.image(str(hist)); p2.image(str(run))
    report = build_report(values, result, hist, run, temp / "Automotive_Body_Fit_Cp_Cpk_Report.docx")
    st.download_button("Download Word report", report.read_bytes(), "Automotive_Body_Fit_Cp_Cpk_Report.docx")

st.dataframe(frame, use_container_width=True)
