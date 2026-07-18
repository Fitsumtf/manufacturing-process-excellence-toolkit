# Manufacturing Process Excellence Toolkit

**An integrated Python portfolio for manufacturing capability, risk, equipment effectiveness, measurement systems, process data, and hands-on engineering problem solving.**

🚀 **[Launch Version 1 — Statistical Engineering Toolkit](https://manufacturing-process-excellence-toolkit.streamlit.app/)** — validated Cp/Cpk, PFMEA, OEE, Gauge R&R, SPC, and process-data demonstrations.

🧠 **Version 2 deployment target:** `https://manufacturing-process-intelligence.streamlit.app/` — live production records, FPY/RTY, BM25 lessons retrieval, evidence-grounded engineering briefs, and integrated reports.

This repository connects the tools that manufacturing engineers use together rather than treating them as isolated calculations:

`Measurement system → process stability → capability → risk → losses → corrective action → verification`

## Choose the appropriate version

Version 2 does not replace Version 1. Version 1 remains the transparent calculation authority; Version 2 adds workflow integration, retrieval, and decision support.

| Decision factor | Version 1 — Statistical Toolkit | Version 2 — Intelligence System |
|---|---|---|
| Primary purpose | Auditable engineering calculations | Integrated production monitoring and investigation support |
| Data | Synthetic examples or uploaded study data | Session-based live records with CSV backup/restore |
| Capability | Cp, Cpk, Cpu, Cpl, observed and estimated PPM | Uses validated V1 methods when capability is required |
| Risk | PFMEA RPN and revised-risk tracking | Connects live problems and retrieved lessons to risk review |
| Equipment | OEE component and loss calculations | OEE trends by date, shift, line, and station |
| Yield | Quality and defect metrics | FPY, station yield, and Rolled Throughput Yield (RTY) |
| Measurement | Crossed ANOVA Gauge R&R | Uses V1 measurement authority and surfaces action needs |
| Retrieval | Not included | BM25-ranked historical engineering lessons |
| Briefing | Statistical interpretation | Traceable, evidence-grounded investigation brief |
| Reporting | Capability and integrated summary reports | Live KPI, retrieved-evidence, and engineering-brief report |
| Storage | CSV inputs and generated outputs | Session storage plus explicit CSV download/restore |
| Recommended use | Statistical authority and offline analysis | Decision support, shift review, and management visibility |

### Higher-level recommendation

- Use **Version 1** when auditability, offline operation, statistical verification, or a single approved study is the priority.
- Use **Version 2** when teams need live yield visibility, repeated-problem retrieval, cross-functional investigation support, and integrated reporting.
- Use the **hybrid architecture** for professional deployment: V1 remains the calculation authority; V2 retrieves evidence and organizes decisions; qualified engineers approve specifications, safety actions, process changes, and product disposition.

## Version 2 architecture and data boundary

```text
Live production record
        ↓
FPY / RTY / OEE / defects / downtime
        ↓
BM25 retrieves similar engineering lessons
        ↓
Evidence-grounded engineering brief
        ↓
Human-reviewed containment, PFMEA, corrective action, and verification
        ↓
Downloadable Word report and CSV backup
```

The public Streamlit deployment is a portfolio demonstration, not a production historian or MES. Streamlit session state is intentionally paired with CSV download/restore because local files on a community-hosted app should not be treated as durable manufacturing records. A future production deployment would require authenticated users, governed database storage, audit trails, access control, retention rules, cybersecurity review, and validated interfaces to approved source systems.

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

The software implements educational interpretations of established methods. Program- or customer-specific requirements always supersede the example thresholds used here.

### Statistical process control and capability

- [NIST/SEMATECH Engineering Statistics Handbook — Process Capability](https://www.itl.nist.gov/div898/handbook/pmc/section1/pmc16.htm). Defines capability as a comparison between a stable process and specification limits and presents Cp/Cpk equations and assumptions.
- [AIAG Statistical Process Control](https://www.aiag.org/training-and-resources/manuals/details/SPC-3). Automotive-industry guidance for statistical process control and process improvement.
- [ISO 22514 series — Statistical methods in process management](https://www.iso.org/committee/49742/x/catalogue/). International process-capability and performance standards.
- Douglas C. Montgomery, [*Introduction to Statistical Quality Control*, 8th Edition](https://www.wiley.com/en-us/Introduction%2Bto%2BStatistical%2BQuality%2BControl%2C%2B8th%2BEdition-p-9781119399308). Statistical-quality-control reference covering control charts, capability, and improvement methods.

### Measurement systems and risk

- [AIAG Measurement Systems Analysis](https://www.aiag.org/training-and-resources/manuals/details/MSA-4). Automotive guidance for evaluating measurement-system variation, including repeatability and reproducibility.
- [AIAG manuals and AIAG–VDA FMEA resources](https://www.aiag.org/training-and-resources/manuals). Primary automotive Core Tools source. This portfolio calculates RPN and transparent educational priority; it does not reproduce or claim the proprietary AIAG–VDA Action Priority tables.

### Manufacturing KPIs, yield, and problem prioritization

- [ISO 22400-1:2014 — Manufacturing-operations KPI framework](https://www.iso.org/standard/56847.html). Defines an industry-neutral framework and terminology for manufacturing KPIs; the standard was reviewed and confirmed in 2025.
- [ISO 22400-2:2014 — KPI definitions and descriptions](https://www.iso.org/standard/54497.html). Specifies manufacturing KPIs using formulas, elements, time behavior, units, and other characteristics.
- [ASQ — First Pass Yield and Rolled Throughput Yield overview](https://my.asq.org/blogs/barbara-banek/2024/02/22/asq). Describes FPY as output passing without correction and RTY as the combined yield of a multistep process.
- [ASQ — Pareto Chart](https://asq.org/quality-resources/pareto). Defines the Pareto chart as a tool for analyzing the frequency of process problems or causes.

### Information retrieval and engineering knowledge

- Stephen E. Robertson and Hugo Zaragoza, [“The Probabilistic Relevance Framework: BM25 and Beyond”](https://dl.acm.org/doi/10.1561/1500000019), *Foundations and Trends in Information Retrieval*, 3(4), 333–389, 2009. DOI: `10.1561/1500000019`.

## Interpretation limitations

- Capability indices do not prove statistical control, normality, causal control, or measurement-system adequacy.
- Specification limits are engineering requirements; control limits are calculated from process behavior and are not interchangeable.
- FPY, RTY, and OEE depend on consistent operational definitions, count boundaries, time bases, and loss coding.
- BM25 measures lexical relevance; a high score does not prove that two failures share the same physical cause.
- Retrieved lessons and generated briefs are investigation aids, not approved containment, root cause, process change, or product disposition.
- Synthetic portfolio results demonstrate software behavior and must not be represented as production performance from any company.

## License

MIT License.

---

Built by [Dr. Fitsum Taye Feyissa](https://github.com/Fitsumtf) — mechanical, manufacturing, and process engineering, statistical quality, technical documentation, and applied data science.
