"""Live-record validation and manufacturing KPI calculations."""

from __future__ import annotations

import numpy as np
import pandas as pd


RECORD_COLUMNS = [
    "date", "shift", "line", "station", "planned_minutes", "downtime_minutes",
    "ideal_cycle_seconds", "units_started", "units_completed", "first_pass_good",
    "final_good", "reworked", "scrapped", "defect_category", "comment",
]


def validate_records(frame: pd.DataFrame) -> pd.DataFrame:
    missing = set(RECORD_COLUMNS) - set(frame.columns)
    if missing:
        raise ValueError(f"Production records are missing columns: {sorted(missing)}")
    data = frame[RECORD_COLUMNS].copy()
    numeric = [
        "planned_minutes", "downtime_minutes", "ideal_cycle_seconds", "units_started",
        "units_completed", "first_pass_good", "final_good", "reworked", "scrapped",
    ]
    for column in numeric:
        data[column] = pd.to_numeric(data[column], errors="raise")
    if (data[numeric] < 0).any().any():
        raise ValueError("Production quantities and times cannot be negative")
    if (data.downtime_minutes >= data.planned_minutes).any():
        raise ValueError("Downtime must be less than planned production time")
    if (data.first_pass_good > data.units_started).any():
        raise ValueError("First-pass-good units cannot exceed units started")
    if (data.final_good > data.units_completed).any():
        raise ValueError("Final-good units cannot exceed units completed")
    data["date"] = pd.to_datetime(data.date).dt.date.astype(str)
    return data


def add_kpis(frame: pd.DataFrame) -> pd.DataFrame:
    data = validate_records(frame)
    runtime = data.planned_minutes - data.downtime_minutes
    data["availability"] = runtime / data.planned_minutes
    data["performance"] = (
        data.ideal_cycle_seconds * data.units_completed / (runtime * 60)
    ).clip(upper=1.0)
    data["quality"] = np.divide(
        data.final_good, data.units_completed,
        out=np.zeros(len(data), dtype=float), where=data.units_completed.to_numpy() > 0,
    )
    data["oee"] = data.availability * data.performance * data.quality
    data["fpy"] = np.divide(
        data.first_pass_good, data.units_started,
        out=np.zeros(len(data), dtype=float), where=data.units_started.to_numpy() > 0,
    )
    return data


def rolled_throughput_yield(frame: pd.DataFrame) -> float:
    data = add_kpis(frame)
    station_totals = data.groupby("station")[["first_pass_good", "units_started"]].sum()
    station_yields = station_totals.first_pass_good.div(
        station_totals.units_started.replace(0, np.nan)
    ).fillna(0)
    return float(station_yields.prod()) if len(station_yields) else 0.0


def executive_summary(frame: pd.DataFrame) -> dict[str, float | int]:
    data = add_kpis(frame)
    started = int(data.units_started.sum()); completed = int(data.units_completed.sum())
    return {
        "records": len(data), "units_started": started, "units_completed": completed,
        "first_pass_good": int(data.first_pass_good.sum()),
        "final_good": int(data.final_good.sum()), "reworked": int(data.reworked.sum()),
        "scrapped": int(data.scrapped.sum()),
        "fpy": float(data.first_pass_good.sum() / started) if started else 0.0,
        "weighted_oee": float(np.average(data.oee, weights=data.planned_minutes))
        if data.planned_minutes.sum() else 0.0,
        "rty": rolled_throughput_yield(data),
    }
