"""Generate an analyst note for the default macro scenario."""

from __future__ import annotations

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from quant.macro_engine import scenario_from_preset, simulate_scenario
from quant.narrative import generate_analyst_note, generate_markdown_report


def generate_default_note(preset_name: str = "Energy price shock") -> str:
    shocks, horizon = scenario_from_preset(preset_name)
    result = simulate_scenario(shocks, horizon=horizon)
    return generate_analyst_note(result)


def generate_default_report(preset_name: str = "Energy price shock") -> str:
    shocks, horizon = scenario_from_preset(preset_name)
    result = simulate_scenario(shocks, horizon=horizon)
    return generate_markdown_report(result, title=f"{preset_name} scenario report")


if __name__ == "__main__":
    print(generate_default_report())
