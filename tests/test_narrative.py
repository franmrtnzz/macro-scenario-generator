from quant.macro_engine import MacroShock, ShockChannel, simulate_scenario
from quant.narrative import generate_analyst_note, generate_markdown_report


def test_analyst_note_contains_macro_sections():
    result = simulate_scenario([MacroShock("Energy", ShockChannel.SUPPLY, 1.3)], horizon=18)
    note = generate_analyst_note(result)

    assert "Executive read" in note
    assert "Transmission" in note
    assert "Policy read" in note
    assert "Key takeaway" in note


def test_markdown_report_contains_shocks_and_metrics():
    result = simulate_scenario([MacroShock("Demand", ShockChannel.DEMAND, -0.8)], horizon=18)
    report = generate_markdown_report(result)

    assert "# Macro scenario report" in report
    assert "## Shocks" in report
    assert "Demand" in report
    assert "Peak inflation" in report
