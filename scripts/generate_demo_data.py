"""Generate deterministic synthetic portfolio datasets. Run from repository root."""

from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path("data")
OUT.mkdir(exist_ok=True)
rng = np.random.default_rng(20260717)

# Balanced 10-part x 3-operator x 3-trial crossed study.
part_nominals = np.linspace(3.25, 3.75, 10)
operator_bias = {"A": -0.003, "B": 0.002, "C": 0.005}
rows = []
for part, nominal in enumerate(part_nominals, 1):
    for operator, bias in operator_bias.items():
        for trial in range(1, 4):
            rows.append((part, operator, trial, nominal + bias + rng.normal(0, 0.006)))
pd.DataFrame(rows, columns=["part_id", "operator", "trial", "measurement_mm"]).to_csv(
    OUT / "synthetic_gage_rr_data.csv", index=False, float_format="%.6f"
)

pfmea = [
    ["Gap measurement", "Incorrect measurement", "False accept or unnecessary adjustment", "Gauge technique varies", "Visual work instruction", 6, 5, 6, "Standardize technique and complete GR&R", "Quality Engineer", 6, 2, 3],
    ["Fixture locate", "Panel located incorrectly", "Gap/flush outside specification", "Locator wear or contamination", "Daily visual inspection", 8, 5, 5, "Add wear limits, cleaning standard, and PM", "Equipment Engineer", 8, 2, 3],
    ["Fastener torque", "Joint under-torqued", "Panel position shifts downstream", "Tool setting or sequence error", "Torque tool OK/NOK", 8, 3, 3, "Add recipe lock and traceability", "Process Engineer", 8, 2, 2],
    ["Final verification", "Defect not detected", "Nonconforming unit advances", "Subjective visual inspection", "Manual inspection", 7, 4, 6, "Introduce calibrated gauge and vision audit", "Quality Engineer", 7, 2, 3],
    ["Material presentation", "Wrong component variant", "Assembly interference", "Mixed material at point of use", "Barcode scan", 7, 2, 3, "Error-proof replenishment and scan interlock", "Production Control", 7, 1, 2],
]
pd.DataFrame(pfmea, columns=[
    "process_step", "failure_mode", "effect", "cause", "current_control",
    "severity", "occurrence", "detection", "recommended_action", "owner",
    "revised_severity", "revised_occurrence", "revised_detection",
]).to_csv(OUT / "synthetic_pfmea.csv", index=False)

oee = pd.DataFrame([
    ["2026-07-01", 480, 58, 72, 320, 305],
    ["2026-07-02", 480, 45, 72, 335, 324],
    ["2026-07-03", 480, 39, 72, 344, 337],
    ["2026-07-04", 480, 31, 72, 353, 348],
    ["2026-07-05", 480, 26, 72, 360, 356],
], columns=["date", "planned_minutes", "downtime_minutes", "ideal_cycle_seconds", "total_count", "good_count"])
oee.to_csv(OUT / "synthetic_oee_data.csv", index=False)

defects = pd.DataFrame([
    ["Gap/flush", 42, 5.5], ["Surface appearance", 27, 3.0],
    ["Fastener", 16, 2.2], ["Electrical check", 9, 4.0],
    ["Material mismatch", 6, 6.0],
], columns=["defect_category", "count", "rework_minutes_each"])
defects["total_rework_minutes"] = defects["count"] * defects["rework_minutes_each"]
defects.to_csv(OUT / "synthetic_defect_data.csv", index=False)
print("Synthetic datasets generated in data/")
