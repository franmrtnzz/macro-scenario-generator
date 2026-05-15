"""Export helpers for scenario outputs."""

from __future__ import annotations

from pathlib import Path

from quant.macro_engine import ScenarioResult, result_to_long_frame
from quant.narrative import generate_markdown_report


def export_scenario(result: ScenarioResult, output_dir: str | Path = "output", stem: str = "scenario") -> dict[str, Path]:
    """Write scenario data and an analyst report to disk."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    csv_path = output_path / f"{stem}_data.csv"
    report_path = output_path / f"{stem}_report.md"

    result_to_long_frame(result).to_csv(csv_path, index=False)
    report_path.write_text(generate_markdown_report(result), encoding="utf-8")

    return {"data": csv_path, "report": report_path}
