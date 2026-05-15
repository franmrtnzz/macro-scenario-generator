"""Generate a scenario report and CSV from Python."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from quant.macro_engine import scenario_from_preset, simulate_scenario, result_to_long_frame
from quant.narrative import generate_markdown_report


def main() -> None:
    shocks, horizon = scenario_from_preset("Soft landing")
    result = simulate_scenario(shocks, horizon=horizon)

    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    result_to_long_frame(result).to_csv(output_dir / "soft_landing_data.csv", index=False)
    (output_dir / "soft_landing_report.md").write_text(
        generate_markdown_report(result, "Soft landing scenario report"),
        encoding="utf-8",
    )

    print("Exported output/soft_landing_data.csv")
    print("Exported output/soft_landing_report.md")


if __name__ == "__main__":
    main()
