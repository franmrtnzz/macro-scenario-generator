"""Run the full scenario flow from Python."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from quant.macro_engine import scenario_from_preset, simulate_scenario, result_to_long_frame
from quant.narrative import generate_analyst_note


def main() -> None:
    shocks, horizon = scenario_from_preset("Energy price shock")
    result = simulate_scenario(shocks, horizon=horizon)

    print("Macro Scenario Generator")
    print(f"Regime: {result.metrics['regime']}")
    print(f"Peak inflation: {result.metrics['inflation_peak']:.2f}%")
    print(f"GDP growth trough: {result.metrics['growth_trough']:.2f}%")
    print()
    print(generate_analyst_note(result))
    print()
    print(result_to_long_frame(result).head().to_string(index=False))


if __name__ == "__main__":
    main()
