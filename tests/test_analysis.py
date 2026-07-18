from pathlib import Path

import numpy as np
import pytest

from automotive_body_fit.analysis import (
    analyze_capability, generate_centered_capability_sample, load_measurements,
)

DATA = Path(__file__).parents[1] / "data" / "automotive_body_fit_100_samples.csv"


def test_reference_dataset_is_mathematically_correct():
    values = load_measurements(DATA)
    result = analyze_capability(values, lsl=3.0, target=3.5, usl=4.0)
    assert result.n == 100
    assert result.mean == pytest.approx(3.5, abs=5e-7)
    assert result.sample_stdev == pytest.approx(0.196, abs=5e-7)
    assert result.cp == pytest.approx(1 / 1.176, rel=1e-6)
    assert result.cpk == pytest.approx(result.cp, abs=1e-6)
    assert result.observed_rejects == 1
    assert result.observed_ppm == 10_000


def test_sample_and_population_stdev_are_not_confused():
    values = load_measurements(DATA)
    result = analyze_capability(values, lsl=3.0, target=3.5, usl=4.0)
    assert result.sample_stdev == pytest.approx(np.std(values, ddof=1))
    assert result.population_stdev == pytest.approx(np.std(values, ddof=0))
    assert result.sample_stdev > result.population_stdev


def test_invalid_specification_order_is_rejected():
    with pytest.raises(ValueError, match="LSL < target < USL"):
        analyze_capability([3.4, 3.5], lsl=4.0, target=3.5, usl=3.0)


def test_generated_sample_hits_requested_centered_cpk():
    values = generate_centered_capability_sample(
        n=100, lsl=3.0, target=3.5, usl=4.0, target_cpk=1.33, seed=7,
    )
    result = analyze_capability(values, lsl=3.0, target=3.5, usl=4.0)
    assert result.mean == pytest.approx(3.5, abs=1e-12)
    assert result.cpk == pytest.approx(1.33, rel=1e-12)


def test_generated_sample_hits_requested_cpk_for_asymmetric_target():
    values = generate_centered_capability_sample(
        n=80, lsl=0.0, target=4.0, usl=10.0, target_cpk=1.67, seed=9,
    )
    result = analyze_capability(values, lsl=0.0, target=4.0, usl=10.0)
    assert result.mean == pytest.approx(4.0, abs=1e-12)
    assert result.cpk == pytest.approx(1.67, rel=1e-12)
