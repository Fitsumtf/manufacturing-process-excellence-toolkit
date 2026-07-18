from pathlib import Path

from .report import build_toolkit_report


def main() -> None:
    report = build_toolkit_report(Path("data"), Path("output/Manufacturing_Process_Excellence_Toolkit_Report.docx"))
    print(f"Generated: {report}")


if __name__ == "__main__":
    main()
