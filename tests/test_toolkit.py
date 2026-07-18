import numpy as np
import pandas as pd
import pytest

from manufacturing_toolkit.gage_rr import crossed_gage_rr
from manufacturing_toolkit.oee import calculate_oee
from manufacturing_toolkit.pfmea import analyze_pfmea
from manufacturing_toolkit.process_data import imr_chart_data, pareto_summary


def test_oee_component_product_and_loss_counts():
    r = calculate_oee(planned_minutes=480, downtime_minutes=48, ideal_cycle_seconds=60, total_count=400, good_count=388)
    assert r.availability == pytest.approx(.9)
    assert r.performance == pytest.approx(400 / 432)
    assert r.quality == pytest.approx(.97)
    assert r.oee == pytest.approx(.9 * (400 / 432) * .97)
    assert r.rejected_count == 12


def test_pfmea_rpn_and_revised_rpn():
    frame = pd.DataFrame([{
        "process_step": "Locate", "failure_mode": "Mislocate", "effect": "Variation",
        "cause": "Wear", "current_control": "Inspection", "severity": 8,
        "occurrence": 5, "detection": 4, "revised_severity": 8,
        "revised_occurrence": 2, "revised_detection": 2,
    }])
    result = analyze_pfmea(frame).iloc[0]
    assert result.rpn == 160 and result.revised_rpn == 32
    assert result.risk_reduction_percent == pytest.approx(80)


def test_gage_rr_detects_low_measurement_error():
    rng = np.random.default_rng(5); rows = []
    for part, nominal in enumerate(np.linspace(1, 2, 10), 1):
        for operator, bias in {"A": 0, "B": .001, "C": -.001}.items():
            for _ in range(3): rows.append([part, operator, nominal + bias + rng.normal(0, .002)])
    result = crossed_gage_rr(pd.DataFrame(rows, columns=["part_id", "operator", "measurement_mm"]))
    assert result.percent_study_variation_grr < 10
    assert result.ndc >= 5


def test_pareto_and_imr():
    p = pareto_summary(pd.DataFrame({"defect": ["A", "B", "A"]}), "defect")
    assert list(p["count"]) == [2, 1]
    assert p.cumulative_percent.iloc[-1] == pytest.approx(100)
    chart = imr_chart_data([1.0, 1.1, .9, 1.05])
    assert chart["i_ucl"] > chart["center"] > chart["i_lcl"]
