"""Overall Equipment Effectiveness calculations with loss accounting."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class OEEResult:
    planned_minutes: float
    runtime_minutes: float
    availability: float
    performance: float
    quality: float
    oee: float
    total_count: int
    good_count: int
    rejected_count: int
    theoretical_count: float
    availability_loss_minutes: float
    performance_loss_equivalent_minutes: float
    quality_loss_equivalent_minutes: float

    def to_dict(self) -> dict:
        return asdict(self)


def calculate_oee(
    *, planned_minutes: float, downtime_minutes: float, ideal_cycle_seconds: float,
    total_count: int, good_count: int,
) -> OEEResult:
    """Calculate A x P x Q using the standard OEE definitions.

    Performance above 100% is rejected because it normally indicates an incorrect
    ideal cycle time or count basis rather than extraordinary equipment performance.
    """
    if planned_minutes <= 0 or ideal_cycle_seconds <= 0:
        raise ValueError("Planned time and ideal cycle time must be positive")
    if downtime_minutes < 0 or downtime_minutes >= planned_minutes:
        raise ValueError("Downtime must be >= 0 and less than planned time")
    if total_count <= 0 or not 0 <= good_count <= total_count:
        raise ValueError("Expected total_count > 0 and 0 <= good_count <= total_count")
    runtime = planned_minutes - downtime_minutes
    availability = runtime / planned_minutes
    performance = ideal_cycle_seconds * total_count / (runtime * 60.0)
    if performance > 1.000001:
        raise ValueError("Performance exceeds 100%; verify ideal cycle time, runtime, and count")
    performance = min(performance, 1.0)
    quality = good_count / total_count
    oee = availability * performance * quality
    theoretical = runtime * 60.0 / ideal_cycle_seconds
    perf_loss = runtime * (1.0 - performance)
    quality_loss = runtime * performance * (1.0 - quality)
    return OEEResult(
        planned_minutes=float(planned_minutes), runtime_minutes=float(runtime),
        availability=float(availability), performance=float(performance),
        quality=float(quality), oee=float(oee), total_count=int(total_count),
        good_count=int(good_count), rejected_count=int(total_count-good_count),
        theoretical_count=float(theoretical), availability_loss_minutes=float(downtime_minutes),
        performance_loss_equivalent_minutes=float(perf_loss),
        quality_loss_equivalent_minutes=float(quality_loss),
    )
