import pandas as pd
import pytest

from quant.macro_engine import (
    BaselineAssumptions,
    MacroShock,
    ShockChannel,
    scenario_from_preset,
    simulate_scenario,
    result_to_long_frame,
    shocks_from_frame,
)


def test_supply_shock_raises_inflation_and_weakens_growth():
    shock = MacroShock("Energy", ShockChannel.SUPPLY, 1.5, duration=4, persistence=0.8)
    result = simulate_scenario([shock], horizon=24)

    assert result.frame["inflation_delta"].max() > 0.8
    assert result.frame["gdp_growth_delta"].min() < -0.2
    assert result.metrics["regime"] in {"Inflation pressure", "Stagflation stress"}


def test_monetary_tightening_lifts_real_rates_and_lowers_inflation_later():
    shock = MacroShock("Hike", ShockChannel.MONETARY, 1.0, duration=4, persistence=0.8)
    result = simulate_scenario([shock], horizon=24)

    assert result.frame["policy_rate_delta"].max() > 0.8
    assert result.frame["real_rate_delta"].max() > 0.8
    assert result.frame["inflation_delta"].iloc[6:].min() < -0.1


def test_preset_scenarios_are_valid():
    for preset in ["Energy price shock", "Monetary tightening", "Demand slowdown", "Soft landing", "Risk-off stress"]:
        shocks, horizon = scenario_from_preset(preset)
        result = simulate_scenario(shocks, horizon=horizon)
        assert len(result.frame) == horizon
        assert not result.frame.isna().any().any()


def test_long_frame_has_expected_shape():
    shocks, horizon = scenario_from_preset("Soft landing")
    result = simulate_scenario(shocks, horizon=horizon)
    long_frame = result_to_long_frame(result)

    assert set(long_frame.columns) == {"date", "variable", "label", "unit", "baseline", "scenario", "delta"}
    assert len(long_frame) == horizon * 5


def test_validation_rejects_extreme_shocks():
    shock = MacroShock("Too large", ShockChannel.DEMAND, 9.0)

    with pytest.raises(ValueError, match="too large"):
        simulate_scenario([shock], horizon=24)


def test_custom_baseline_is_used():
    assumptions = BaselineAssumptions(initial_inflation=3.0, target_inflation=2.0)
    result = simulate_scenario([], horizon=12, assumptions=assumptions)

    assert isinstance(result.frame["date"].iloc[0], pd.Timestamp)
    assert result.frame["inflation_baseline"].iloc[0] > 2.8
    assert result.warnings == ["No active shock is configured; the scenario equals the baseline path."]


def test_blank_editor_rows_are_ignored():
    frame = pd.DataFrame(
        [
            {"active": True, "name": None, "channel": None, "magnitude": None},
            {"active": True, "name": "Demand", "channel": ShockChannel.DEMAND.value, "magnitude": -0.5},
        ]
    )

    shocks = shocks_from_frame(frame)
    assert len(shocks) == 1
    assert shocks[0].name == "Demand"
