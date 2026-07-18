import pandas as pd
import pytest

from v2_manufacturing_intelligence.analytics import (
    RECORD_COLUMNS, add_kpis, executive_summary, rolled_throughput_yield,
)
from v2_manufacturing_intelligence.bm25_engine import BM25LessonsIndex
from v2_manufacturing_intelligence.briefing import build_engineering_brief


def records():
    return pd.DataFrame([
        ["2026-07-01", "A", "L1", "S1", 480, 48, 60, 100, 98, 90, 95, 5, 3, "Gap", ""],
        ["2026-07-01", "A", "L1", "S2", 480, 48, 60, 98, 96, 88, 94, 6, 2, "Torque", ""],
    ], columns=RECORD_COLUMNS)


def test_live_kpis_and_rty():
    data = add_kpis(records())
    assert data.fpy.iloc[0] == pytest.approx(.9)
    assert 0 <= data.oee.min() <= data.oee.max() <= 1
    assert rolled_throughput_yield(data) == pytest.approx(.9 * (88 / 98))
    metrics = executive_summary(data)
    assert metrics["scrapped"] == 5 and metrics["reworked"] == 11


def test_bm25_retrieval_and_brief():
    lessons = pd.DataFrame([{
        "lesson_id": "L1", "problem": "fixture gap variation", "symptoms": "drift",
        "root_cause": "locator wear", "containment": "inspect locator",
        "corrective_action": "replace locator", "verification": "confirm Cpk",
        "lesson": "control fixture wear",
    }, {
        "lesson_id": "L2", "problem": "sensor stop", "symptoms": "downtime",
        "root_cause": "dirty sensor", "containment": "clean sensor",
        "corrective_action": "add PM", "verification": "confirm availability",
        "lesson": "track micro stops",
    }])
    matches = BM25LessonsIndex(lessons).search("gap variation after fixture maintenance")
    assert matches.lesson_id.iloc[0] == "L1" and matches.bm25_score.iloc[0] > 0
    brief = build_engineering_brief("gap variation", matches, {"fpy": .9})
    assert "locator wear" in brief and "L1" in brief
