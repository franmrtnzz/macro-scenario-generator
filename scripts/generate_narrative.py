"""Command-line report generation for Macro Scenario Generator."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from quant.macro_engine import PRESET_SCENARIOS, scenario_from_preset, simulate_scenario
from quant.narrative import generate_markdown_report


def build_report(preset: str) -> str:
    shocks, horizon = scenario_from_preset(preset)
    result = simulate_scenario(shocks, horizon=horizon)
    return generate_markdown_report(result, title=f"{preset} scenario report")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a macro scenario report.")
    parser.add_argument("--preset", choices=sorted(PRESET_SCENARIOS), default="Energy price shock")
    parser.add_argument("--output", default="output/summary.md")
    args = parser.parse_args()

    report = build_report(args.preset)
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    print(f"Report written to {output_path}")


if __name__ == "__main__":
    main()
