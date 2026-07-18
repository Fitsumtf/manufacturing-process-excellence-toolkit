"""Command-line entry point."""

from argparse import ArgumentParser
from pathlib import Path

from .analysis import analyze_capability, load_measurements
from .plots import capability_histogram, run_chart
from .report import build_report


def main() -> None:
    parser = ArgumentParser(description="Generate an automotive body-fit Cp/Cpk report")
    parser.add_argument("--input", type=Path, default=Path("data/automotive_body_fit_100_samples.csv"))
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    parser.add_argument("--lsl", type=float, default=3.0)
    parser.add_argument("--target", type=float, default=3.5)
    parser.add_argument("--usl", type=float, default=4.0)
    args = parser.parse_args()

    values = load_measurements(args.input)
    result = analyze_capability(values, lsl=args.lsl, target=args.target, usl=args.usl)
    histogram = capability_histogram(values, result, args.output_dir / "capability_histogram.png")
    sequence = run_chart(values, result, args.output_dir / "measurement_run_chart.png")
    report = build_report(values, result, histogram, sequence, args.output_dir / "Automotive_Body_Fit_Cp_Cpk_Report.docx")
    print(f"Mean={result.mean:.6f} mm | s={result.sample_stdev:.6f} mm")
    print(f"Cp={result.cp:.5f} | Cpk={result.cpk:.5f} | {result.status}")
    print(f"Report: {report}")


if __name__ == "__main__":
    main()
