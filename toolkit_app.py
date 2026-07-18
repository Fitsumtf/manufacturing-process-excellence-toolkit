"""All-in-one Streamlit manufacturing process excellence portfolio."""

from pathlib import Path
import re
import tempfile

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from automotive_body_fit.analysis import (
    analyze_capability, generate_centered_capability_sample, load_measurements,
)
from automotive_body_fit.plots import capability_histogram, run_chart
from automotive_body_fit.report import build_report
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
    st.subheader("Interactive Process Capability Sandbox")
    st.caption(
        "Analyze real measurements, paste values, retain the verified reference case, or "
        "generate a clearly labeled educational comparison sample. Specifications must come "
        "from approved engineering or customer requirements."
    )
    c1, c2, c3 = st.columns(3)
    lsl = c1.number_input("LSL", value=3.0, format="%.6f")
    target = c2.number_input("Target", value=3.5, format="%.6f")
    usl = c3.number_input("USL", value=4.0, format="%.6f")
    source = st.radio(
        "Measurement source",
        ["Verified reference dataset", "Upload CSV", "Paste measurements", "Generate educational comparison"],
        horizontal=True,
    )
    reference_values = load_measurements(DATA / "automotive_body_fit_100_samples.csv")
    values = reference_values
    dataset_name = "Verified synthetic reference dataset"
    source_error = None

    if source == "Upload CSV":
        uploaded = st.file_uploader("Upload a CSV containing at least one numeric measurement column", type="csv", key="capability_csv")
        if uploaded:
            uploaded_frame = pd.read_csv(uploaded)
            numeric_candidates = [
                column for column in uploaded_frame.columns
                if pd.to_numeric(uploaded_frame[column], errors="coerce").notna().sum() >= 2
            ]
            if not numeric_candidates:
                source_error = "No column contains at least two numeric measurements."
            else:
                column = st.selectbox("Measurement column", numeric_candidates)
                numeric = pd.to_numeric(uploaded_frame[column], errors="coerce")
                if numeric.isna().any():
                    source_error = f"Column '{column}' contains missing or nonnumeric values. Clean the data before capability analysis."
                else:
                    values = numeric.to_numpy(dtype=float)
                    dataset_name = f"Uploaded data: {uploaded.name} / {column}"
        else:
            st.info("Upload a CSV to replace the reference measurements.")

    elif source == "Paste measurements":
        pasted = st.text_area(
            "Paste measurements separated by commas, spaces, semicolons, or new lines",
            placeholder="3.48, 3.51, 3.46, 3.53, ...",
            height=120,
        )
        if pasted.strip():
            try:
                tokens = [token for token in re.split(r"[,;\s]+", pasted.strip()) if token]
                values = np.asarray([float(token) for token in tokens], dtype=float)
                if values.size < 2 or not np.isfinite(values).all():
                    raise ValueError
                dataset_name = "Manually pasted measurements"
            except ValueError:
                source_error = "Paste at least two finite numeric measurements using commas, spaces, semicolons, or new lines."
        else:
            st.info("Paste measurements to replace the reference dataset.")

    elif source == "Generate educational comparison":
        g1, g2, g3 = st.columns(3)
        requested_cpk = g1.selectbox("Target centered Cpk", [1.00, 1.33, 1.67, 2.00], index=1)
        sample_count = g2.number_input("Number of samples", min_value=30, max_value=10000, value=100, step=10)
        seed = g3.number_input("Random seed", min_value=0, value=42, step=1)
        try:
            values = generate_centered_capability_sample(
                n=int(sample_count), lsl=lsl, target=target, usl=usl,
                target_cpk=float(requested_cpk), seed=int(seed),
            )
            dataset_name = f"Educational simulation targeting centered Cpk {requested_cpk:.2f}"
            st.warning("Simulation only: generated values are not evidence of real process capability.")
        except ValueError as exc:
            source_error = str(exc)

    if source_error:
        st.error(source_error)
    else:
        try:
            cap = analyze_capability(values, lsl=lsl, target=target, usl=usl)
        except ValueError as exc:
            st.error(str(exc))
        else:
            st.markdown(f"**Active dataset:** {dataset_name} · **n = {cap.n:,}**")
            cols = st.columns(8)
            labels = ["Mean", "Sample STDEV", "Cp", "Cpu", "Cpl", "Cpk", "Observed PPM", "Normal-est. PPM"]
            results = [
                f"{cap.mean:.6f}", f"{cap.sample_stdev:.6f}", f"{cap.cp:.3f}",
                f"{cap.cpu:.3f}", f"{cap.cpl:.3f}", f"{cap.cpk:.3f}",
                f"{cap.observed_ppm:,.0f}", f"{cap.expected_ppm_normal:,.0f}",
            ]
            for col, label, result in zip(cols, labels, results):
                col.metric(label, result)
            if cap.cpk < 1.0:
                st.error(cap.status)
            elif cap.cpk < 1.33:
                st.warning(f"{cap.status}: above 1.00 but below the illustrative 1.33 criterion")
            else:
                st.success(cap.status)
            st.caption("Capability thresholds are illustrative. Use the applicable customer or program requirement.")

            reference_cap = analyze_capability(reference_values, lsl=lsl, target=target, usl=usl)
            comparison = pd.DataFrame([
                ["Reference", reference_cap.n, reference_cap.mean, reference_cap.sample_stdev, reference_cap.cp, reference_cap.cpk, reference_cap.observed_ppm],
                ["Active", cap.n, cap.mean, cap.sample_stdev, cap.cp, cap.cpk, cap.observed_ppm],
            ], columns=["Dataset", "n", "Mean", "Sample STDEV", "Cp", "Cpk", "Observed PPM"])
            st.subheader("Reference versus active dataset")
            st.dataframe(comparison.style.format({"Mean": "{:.6f}", "Sample STDEV": "{:.6f}", "Cp": "{:.3f}", "Cpk": "{:.3f}", "Observed PPM": "{:,.0f}"}), width="stretch", hide_index=True)

            with tempfile.TemporaryDirectory() as temp_dir:
                temp_dir = Path(temp_dir)
                hist = capability_histogram(values, cap, temp_dir / "capability_histogram.png")
                sequence = run_chart(values, cap, temp_dir / "measurement_run_chart.png")
                p1, p2 = st.columns(2)
                p1.image(str(hist), caption="Capability distribution")
                p2.image(str(sequence), caption="Time-ordered run chart")
                report = build_report(
                    values, cap, hist, sequence,
                    temp_dir / "Process_Capability_Report.docx",
                    report_title="Interactive Process Capability Study",
                    context=f"{dataset_name} | User-selected specification limits",
                    characteristic="the selected process characteristic",
                    disclaimer=(
                        "This report was generated from the active user-selected dataset. The user is "
                        "responsible for data authorization, confidentiality, specification validity, "
                        "process stability, and measurement-system adequacy."
                    ),
                )
                d1, d2 = st.columns(2)
                active_frame = pd.DataFrame({"sample_id": np.arange(1, cap.n + 1), "measurement_mm": values})
                d1.download_button(
                    "Download analyzed measurements CSV", active_frame.to_csv(index=False).encode(),
                    "capability_measurements.csv", "text/csv",
                )
                d2.download_button(
                    "Download capability Word report", report.read_bytes(),
                    "Process_Capability_Report.docx",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )
            failures = active_frame[(active_frame.measurement_mm < lsl) | (active_frame.measurement_mm > usl)]
            with st.expander(f"Out-of-specification measurements ({len(failures)})"):
                if failures.empty:
                    st.success("No observed measurements are outside the specification limits.")
                else:
                    st.dataframe(failures, width="stretch", hide_index=True)

with tabs[1]:
    pfmea = analyze_pfmea(pd.read_csv(DATA / "synthetic_pfmea.csv"))
    st.caption("Portfolio priority is educational triage, not the AIAG-VDA Action Priority table.")
    st.dataframe(pfmea, use_container_width=True)
    st.bar_chart(pfmea.set_index("failure_mode")[["rpn", "revised_rpn"]])

with tabs[2]:
    oee_data = pd.read_csv(DATA / "synthetic_oee_data.csv")
    rows = []
    for row in oee_data.to_dict("records"):
        date = row.pop("date"); result = calculate_oee(**row)
        rows.append({"date": date, "availability": result.availability, "performance": result.performance, "quality": result.quality, "oee": result.oee})
    trend = pd.DataFrame(rows).set_index("date")
    st.dataframe(trend.style.format("{:.1%}"), use_container_width=True); st.line_chart(trend)

with tabs[3]:
    grr_data = pd.read_csv(DATA / "synthetic_gage_rr_data.csv"); grr = crossed_gage_rr(grr_data)
    g1, g2, g3 = st.columns(3)
    g1.metric("Total GR&R", f"{grr.percent_study_variation_grr:.2f}%")
    g2.metric("ndc", grr.ndc); g3.metric("Result", grr.interpretation)
    st.dataframe(grr_data, use_container_width=True)

with tabs[4]:
    defects = pd.read_csv(DATA / "synthetic_defect_data.csv")
    pareto = pareto_summary(defects, "defect_category", "count")
    st.dataframe(pareto, use_container_width=True); st.bar_chart(pareto.set_index("defect_category")["count"])
    ordered = load_measurements(DATA / "automotive_body_fit_100_samples.csv")
    limits = imr_chart_data(ordered)
    st.write(f"I-chart center: {limits['center']:.4f}; UCL: {limits['i_ucl']:.4f}; LCL: {limits['i_lcl']:.4f}")

with tabs[5]:
    for path in sorted(Path("case_studies").glob("*.md")):
        with st.expander(path.stem.replace("_", " ").title()): st.markdown(path.read_text())
