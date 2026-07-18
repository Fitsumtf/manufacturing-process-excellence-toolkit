# Manufacturing Process Excellence Toolkit

**An integrated Python portfolio for manufacturing capability, risk, equipment effectiveness, measurement systems, process data, and hands-on engineering problem solving.**

This repository connects the tools that manufacturing engineers use together rather than treating them as isolated calculations:

`Measurement system → process stability → capability → risk → losses → corrective action → verification`

> **Public portfolio disclaimer**  
> This portfolio uses synthetic educational datasets and generalized manufacturing case studies solely to demonstrate engineering, statistical analysis, and problem-solving methods. It contains no proprietary production records, confidential specifications, internal documents, or company-specific manufacturing data.

## Included modules

| Module | Questions answered | Outputs |
|---|---|---|
| Process capability | Is a stable process able to meet specifications? | Cp, Cpk, Cpu, Cpl, PPM, plots, Word report |
| PFMEA | Where should preventive action be focused? | RPN, transparent portfolio priority, revised risk |
| OEE | Where is productive time being lost? | Availability, performance, quality, OEE, loss minutes |
| Gauge R&R | Can the measurement system distinguish part variation? | ANOVA variance components, %study variation, ndc |
| Process data | What is unstable or dominant? | I-MR limits, Pareto counts and cumulative percentage |
| Process improvement | How was the problem solved and sustained? | Generalized cases using data, root cause, action, validation |
| Line experience | How do analytics connect to physical production? | Launch, balancing, fixtures, controls, vision, commissioning |

## Verified demonstration results

### Capability

- 100 synthetic measurements
- LSL / target / USL: 3.000 / 3.500 / 4.000 mm
- Mean: 3.500000 mm
- Sample standard deviation: 0.196000 mm
- Cp = Cpk = 0.850
- Interpretation: centered but not capable under the illustrative 1.33 criterion

### OEE

The program calculates:

```text
Availability = Run Time / Planned Production Time
Performance  = Ideal Cycle Time × Total Count / Run Time
Quality      = Good Count / Total Count
OEE          = Availability × Performance × Quality
```

Performance greater than 100% is rejected because it normally indicates an incorrect ideal-cycle or production-count basis.

### PFMEA

The module validates 1–10 severity, occurrence, and detection ratings, calculates `RPN = S × O × D`, tracks recommended actions, and compares initial versus revised risk. Its `portfolio_priority` is deliberately transparent educational triage—it is **not** represented as the proprietary AIAG–VDA Action Priority table.

### Gauge R&R

The module performs a balanced crossed random-effects ANOVA study and estimates:

- Equipment variation (repeatability)
- Operator and part-by-operator effects (reproducibility)
- Total Gauge R&R
- Part-to-part variation
- Percent contribution
- Percent study variation
- Number of distinct categories (`ndc`)

Typical interpretation bands are included as educational guidance; actual acceptance depends on measurement purpose, customer requirements, process risk, and cost.

## Run the toolkit

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python scripts/generate_demo_data.py
streamlit run toolkit_app.py
```

Generate the all-in-one Word report:

```bash
python -m manufacturing_toolkit.cli
```

Generate the detailed capability report:

```bash
python -m automotive_body_fit.cli
```

Run tests:

```bash
pytest -q
```

## Repository structure

```text
├── automotive_body_fit/       # Cp/Cpk engine, plots, detailed Word report
├── manufacturing_toolkit/     # PFMEA, OEE, Gauge R&R, Pareto, I-MR, report
├── case_studies/              # Generalized hands-on engineering examples
├── data/                      # Synthetic demonstration datasets
├── scripts/                   # Deterministic dataset generator
├── tests/                     # Mathematical and validation tests
├── toolkit_app.py             # Unified Streamlit dashboard
├── app.py                     # Detailed capability application
└── output/                    # Example reports and charts
```

## Engineering workflow

1. Validate the measurement system with calibration and MSA/Gauge R&R.
2. Plot time-ordered data and confirm statistical stability.
3. Evaluate capability only after the first two conditions are satisfied.
4. Use PFMEA to connect failure causes, controls, risk, and actions.
5. Use OEE and Pareto analysis to focus production improvement.
6. Validate corrective actions with an independent dataset.
7. Sustain results through standardized work, control plans, reaction plans, audits, and preventive maintenance.

## References

- [AIAG Statistical Process Control](https://www.aiag.org/training-and-resources/manuals/details/SPC-3)
- [AIAG Measurement Systems Analysis](https://www.aiag.org/training-and-resources/manuals/details/MSA-4)
- [AIAG manuals and AIAG–VDA FMEA resources](https://www.aiag.org/training-and-resources/manuals)
- [Douglas C. Montgomery, *Introduction to Statistical Quality Control*, 8th Edition](https://www.wiley.com/en-us/Introduction%2Bto%2BStatistical%2BQuality%2BControl%2C%2B8th%2BEdition-p-9781119399308)
- [ISO 22514 — Statistical methods in process management](https://www.iso.org/committee/49742/x/catalogue/)

## License

MIT License.

---

Built by [Dr. Fitsum Taye Feyissa](https://github.com/Fitsumtf) — manufacturing and process engineering, statistical quality, technical documentation, and applied data science.
