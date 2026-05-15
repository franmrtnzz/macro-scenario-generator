"""Interpretable macro scenario engine.

The product goal is not to pretend precision from a fragile econometric fit.
This module implements a compact semi-structural engine with explicit response
profiles. Shocks are propagated through transparent channels and every output is
kept in user-facing macro units.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import numpy as np
import pandas as pd


class ShockChannel(str, Enum):
    DEMAND = "Demand"
    SUPPLY = "Supply / energy"
    MONETARY = "Monetary policy"
    RISK = "Financial risk"
    FISCAL = "Fiscal impulse"


VARIABLE_LABELS: dict[str, str] = {
    "gdp_growth": "GDP growth",
    "inflation": "Inflation",
    "policy_rate": "Policy rate",
    "real_rate": "Real rate",
    "output_gap": "Output gap",
}

VARIABLE_UNITS: dict[str, str] = {
    "gdp_growth": "% y/y",
    "inflation": "% y/y",
    "policy_rate": "%",
    "real_rate": "%",
    "output_gap": "% potential GDP",
}

DISPLAY_VARIABLES = ["gdp_growth", "inflation", "policy_rate", "real_rate", "output_gap"]


@dataclass(frozen=True)
class BaselineAssumptions:
    """Starting point and medium-term anchors for the scenario."""

    start_date: str = "2026-06-01"
    trend_growth: float = 1.3
    initial_gdp_growth: float = 1.1
    target_inflation: float = 2.0
    initial_inflation: float = 2.4
    neutral_real_rate: float = 1.0
    initial_policy_rate: float = 3.25
    initial_output_gap: float = -0.2

    @property
    def neutral_policy_rate(self) -> float:
        return self.target_inflation + self.neutral_real_rate


@dataclass(frozen=True)
class MacroShock:
    """A user-defined shock in economically meaningful units."""

    name: str
    channel: ShockChannel
    magnitude: float
    duration: int = 3
    persistence: float = 0.75
    start_month: int = 1

    def normalized(self) -> "MacroShock":
        return MacroShock(
            name=self.name.strip() or self.channel.value,
            channel=self.channel,
            magnitude=float(self.magnitude),
            duration=max(1, int(self.duration)),
            persistence=min(0.98, max(0.0, float(self.persistence))),
            start_month=max(1, int(self.start_month)),
        )


@dataclass
class ScenarioResult:
    frame: pd.DataFrame
    shocks: list[MacroShock]
    baseline: BaselineAssumptions
    metrics: dict[str, float | str]
    warnings: list[str] = field(default_factory=list)

    def display_frame(self) -> pd.DataFrame:
        cols: list[str] = []
        for variable in DISPLAY_VARIABLES:
            cols.extend([f"{variable}_baseline", f"{variable}_scenario", f"{variable}_delta"])
        return self.frame[["date", *cols]]


ResponseProfile = dict[str, tuple[float, ...]]


RESPONSE_PROFILES: dict[ShockChannel, ResponseProfile] = {
    ShockChannel.DEMAND: {
        "gdp_growth": (0.75, 0.55, 0.36, 0.20, 0.10),
        "output_gap": (0.60, 0.50, 0.36, 0.22, 0.10),
        "inflation": (0.06, 0.11, 0.16, 0.14, 0.09, 0.04),
        "policy_rate": (0.02, 0.05, 0.09, 0.10, 0.07, 0.03),
    },
    ShockChannel.SUPPLY: {
        "inflation": (0.72, 0.62, 0.48, 0.33, 0.20, 0.10),
        "gdp_growth": (-0.24, -0.30, -0.23, -0.14, -0.06),
        "output_gap": (-0.18, -0.24, -0.20, -0.12, -0.05),
        "policy_rate": (0.07, 0.16, 0.24, 0.24, 0.16, 0.08),
    },
    ShockChannel.MONETARY: {
        "policy_rate": (1.00, 0.92, 0.78, 0.58, 0.38, 0.20),
        "gdp_growth": (0.00, -0.05, -0.14, -0.22, -0.22, -0.16, -0.08),
        "output_gap": (0.00, -0.04, -0.10, -0.18, -0.20, -0.16, -0.09),
        "inflation": (0.00, 0.00, -0.03, -0.08, -0.12, -0.12, -0.07, -0.03),
    },
    ShockChannel.RISK: {
        "gdp_growth": (-0.56, -0.45, -0.28, -0.14, -0.06),
        "output_gap": (-0.42, -0.36, -0.24, -0.12, -0.05),
        "inflation": (-0.03, -0.06, -0.08, -0.06, -0.03),
        "policy_rate": (-0.04, -0.10, -0.16, -0.18, -0.12, -0.06),
    },
    ShockChannel.FISCAL: {
        "gdp_growth": (0.52, 0.45, 0.30, 0.16, 0.06),
        "output_gap": (0.42, 0.36, 0.25, 0.12, 0.05),
        "inflation": (0.04, 0.08, 0.11, 0.09, 0.04),
        "policy_rate": (0.00, 0.03, 0.07, 0.08, 0.05),
    },
}


PRESET_SCENARIOS: dict[str, dict[str, Any]] = {
    "Energy price shock": {
        "description": "Inflationary supply shock with a negative activity impulse.",
        "horizon": 24,
        "shocks": [
            MacroShock("Energy price shock", ShockChannel.SUPPLY, 1.6, duration=5, persistence=0.82),
        ],
    },
    "Monetary tightening": {
        "description": "Front-loaded policy tightening transmitted to output and inflation with lags.",
        "horizon": 24,
        "shocks": [
            MacroShock("Rate shock", ShockChannel.MONETARY, 1.0, duration=4, persistence=0.80),
        ],
    },
    "Demand slowdown": {
        "description": "Broad demand deterioration with disinflationary pressure.",
        "horizon": 24,
        "shocks": [
            MacroShock("Demand slowdown", ShockChannel.DEMAND, -1.1, duration=4, persistence=0.78),
        ],
    },
    "Soft landing": {
        "description": "Moderate demand cooling paired with a contained policy response.",
        "horizon": 24,
        "shocks": [
            MacroShock("Demand cooling", ShockChannel.DEMAND, -0.45, duration=4, persistence=0.70),
            MacroShock("Policy support", ShockChannel.MONETARY, -0.35, duration=3, persistence=0.75, start_month=4),
        ],
    },
    "Risk-off stress": {
        "description": "Financial conditions shock with weaker activity and easier policy path.",
        "horizon": 24,
        "shocks": [
            MacroShock("Risk-off shock", ShockChannel.RISK, 1.2, duration=4, persistence=0.80),
        ],
    },
}


def baseline_path(horizon: int, assumptions: BaselineAssumptions | None = None) -> pd.DataFrame:
    assumptions = assumptions or BaselineAssumptions()
    horizon = _validate_horizon(horizon)
    dates = pd.date_range(pd.Timestamp(assumptions.start_date), periods=horizon, freq="MS")
    rows: list[dict[str, float | pd.Timestamp]] = []

    for t, date in enumerate(dates):
        output_gap = assumptions.initial_output_gap * (0.91**t)
        inflation_gap = (assumptions.initial_inflation - assumptions.target_inflation) * (0.94**t)
        inflation = assumptions.target_inflation + inflation_gap + 0.08 * output_gap
        policy_gap = (assumptions.initial_policy_rate - assumptions.neutral_policy_rate) * (0.92**t)
        policy_rate = assumptions.neutral_policy_rate + policy_gap + 0.22 * inflation_gap + 0.08 * output_gap
        gdp_growth = assumptions.trend_growth + 0.35 * output_gap

        rows.append(
            {
                "date": date,
                "gdp_growth_baseline": gdp_growth,
                "inflation_baseline": inflation,
                "policy_rate_baseline": policy_rate,
                "real_rate_baseline": policy_rate - inflation,
                "output_gap_baseline": output_gap,
            }
        )

    return pd.DataFrame(rows)


def simulate_scenario(
    shocks: list[MacroShock],
    horizon: int = 24,
    assumptions: BaselineAssumptions | None = None,
) -> ScenarioResult:
    assumptions = assumptions or BaselineAssumptions()
    horizon = _validate_horizon(horizon)
    normalized_shocks = [shock.normalized() for shock in shocks if abs(float(shock.magnitude)) > 1e-9]
    _validate_shocks(normalized_shocks, horizon)

    frame = baseline_path(horizon, assumptions)
    contributions = {variable: np.zeros(horizon, dtype=float) for variable in DISPLAY_VARIABLES}

    for shock in normalized_shocks:
        _apply_shock(contributions, shock, horizon)

    for variable in DISPLAY_VARIABLES:
        baseline_col = f"{variable}_baseline"
        scenario_col = f"{variable}_scenario"
        delta_col = f"{variable}_delta"
        if variable == "real_rate":
            continue
        frame[delta_col] = contributions[variable]
        frame[scenario_col] = frame[baseline_col] + frame[delta_col]

    frame["real_rate_scenario"] = frame["policy_rate_scenario"] - frame["inflation_scenario"]
    frame["real_rate_delta"] = frame["real_rate_scenario"] - frame["real_rate_baseline"]

    metrics = _scenario_metrics(frame)
    warnings = _coherence_warnings(frame, normalized_shocks)
    return ScenarioResult(frame=frame, shocks=normalized_shocks, baseline=assumptions, metrics=metrics, warnings=warnings)


def scenario_from_preset(name: str) -> tuple[list[MacroShock], int]:
    if name not in PRESET_SCENARIOS:
        raise ValueError(f"Unknown preset scenario: {name}")
    preset = PRESET_SCENARIOS[name]
    return list(preset["shocks"]), int(preset["horizon"])


def shocks_to_frame(shocks: list[MacroShock]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "active": True,
                "name": shock.name,
                "channel": shock.channel.value,
                "magnitude": shock.magnitude,
                "duration": shock.duration,
                "persistence": shock.persistence,
                "start_month": shock.start_month,
            }
            for shock in shocks
        ]
    )


def shocks_from_frame(frame: pd.DataFrame) -> list[MacroShock]:
    shocks: list[MacroShock] = []
    if frame.empty:
        return shocks

    for _, row in frame.iterrows():
        if "active" in row and not bool(row["active"]):
            continue

        raw_magnitude = row.get("magnitude", 0.0)
        if pd.isna(raw_magnitude) or abs(float(raw_magnitude)) < 1e-9:
            continue

        channel_value = row.get("channel", ShockChannel.DEMAND.value)
        if pd.isna(channel_value):
            channel_value = ShockChannel.DEMAND.value
        channel_value = str(channel_value)
        channel = ShockChannel(channel_value)
        raw_name = row.get("name", channel.value)
        name = channel.value if pd.isna(raw_name) else str(raw_name)
        duration = 1 if pd.isna(row.get("duration", 1)) else int(row.get("duration", 1))
        persistence = 0.75 if pd.isna(row.get("persistence", 0.75)) else float(row.get("persistence", 0.75))
        start_month = 1 if pd.isna(row.get("start_month", 1)) else int(row.get("start_month", 1))
        shocks.append(
            MacroShock(
                name=name,
                channel=channel,
                magnitude=float(raw_magnitude),
                duration=duration,
                persistence=persistence,
                start_month=start_month,
            ).normalized()
        )
    return shocks


def result_to_long_frame(result: ScenarioResult) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    for _, row in result.frame.iterrows():
        for variable in DISPLAY_VARIABLES:
            records.append(
                {
                    "date": row["date"],
                    "variable": variable,
                    "label": VARIABLE_LABELS[variable],
                    "unit": VARIABLE_UNITS[variable],
                    "baseline": row[f"{variable}_baseline"],
                    "scenario": row[f"{variable}_scenario"],
                    "delta": row[f"{variable}_delta"],
                }
            )
    return pd.DataFrame(records)


def _apply_shock(contributions: dict[str, np.ndarray], shock: MacroShock, horizon: int) -> None:
    profile = RESPONSE_PROFILES[shock.channel]
    impulses = _shock_impulses(shock, horizon)

    for t, impulse in enumerate(impulses):
        if abs(impulse) < 1e-12:
            continue
        for variable, coefficients in profile.items():
            for lag, coefficient in enumerate(coefficients):
                target_t = t + lag
                if target_t >= horizon:
                    break
                contributions[variable][target_t] += impulse * coefficient


def _shock_impulses(shock: MacroShock, horizon: int) -> np.ndarray:
    impulses = np.zeros(horizon, dtype=float)
    start = shock.start_month - 1
    if start >= horizon:
        return impulses

    stop = min(horizon, start + shock.duration)
    for t in range(start, stop):
        elapsed = t - start
        impulses[t] = shock.magnitude * (shock.persistence**elapsed)
    return impulses


def _scenario_metrics(frame: pd.DataFrame) -> dict[str, float | str]:
    inflation_peak = float(frame["inflation_scenario"].max())
    inflation_peak_delta = float(frame["inflation_delta"].max())
    growth_trough = float(frame["gdp_growth_scenario"].min())
    growth_trough_delta = float(frame["gdp_growth_delta"].min())
    policy_peak = float(frame["policy_rate_scenario"].max())
    real_rate_peak = float(frame["real_rate_scenario"].max())
    output_gap_trough = float(frame["output_gap_scenario"].min())

    if inflation_peak >= 3.5 and output_gap_trough <= -1.0:
        regime = "Stagflation stress"
    elif growth_trough < 0.0:
        regime = "Recession risk"
    elif inflation_peak_delta > 0.7:
        regime = "Inflation pressure"
    elif real_rate_peak > 2.0:
        regime = "Restrictive policy"
    else:
        regime = "Contained adjustment"

    return {
        "regime": regime,
        "inflation_peak": inflation_peak,
        "inflation_peak_delta": inflation_peak_delta,
        "growth_trough": growth_trough,
        "growth_trough_delta": growth_trough_delta,
        "policy_peak": policy_peak,
        "real_rate_peak": real_rate_peak,
        "output_gap_trough": output_gap_trough,
    }


def _coherence_warnings(frame: pd.DataFrame, shocks: list[MacroShock]) -> list[str]:
    warnings: list[str] = []
    inflation_delta_peak = float(frame["inflation_delta"].max())
    policy_delta_peak = float(frame["policy_rate_delta"].max())
    growth_delta_trough = float(frame["gdp_growth_delta"].min())
    output_gap_trough = float(frame["output_gap_scenario"].min())
    real_rate_peak = float(frame["real_rate_scenario"].max())

    if inflation_delta_peak > 0.7 and policy_delta_peak < 0.05:
        warnings.append("Inflation rises materially while the policy path barely responds.")
    if inflation_delta_peak > 0.7 and output_gap_trough < -1.0:
        warnings.append("The scenario combines above-baseline inflation with a negative output gap.")
    if real_rate_peak > 2.5 and growth_delta_trough < -0.5:
        warnings.append("Real rates enter a clearly restrictive zone and activity weakens.")
    if output_gap_trough < -2.0:
        warnings.append("The output gap falls below -2%, so recession risk dominates the scenario.")
    if not shocks:
        warnings.append("No active shock is configured; the scenario equals the baseline path.")
    return warnings


def _validate_horizon(horizon: int) -> int:
    horizon = int(horizon)
    if horizon < 6 or horizon > 60:
        raise ValueError("Horizon must be between 6 and 60 months.")
    return horizon


def _validate_shocks(shocks: list[MacroShock], horizon: int) -> None:
    for shock in shocks:
        if shock.channel not in RESPONSE_PROFILES:
            raise ValueError(f"Unsupported shock channel: {shock.channel}")
        if abs(shock.magnitude) > 6:
            raise ValueError(f"Shock '{shock.name}' is too large for this calibrated engine.")
        if shock.duration < 1 or shock.duration > horizon:
            raise ValueError(f"Shock '{shock.name}' duration must be between 1 and the horizon.")
        if shock.start_month < 1 or shock.start_month > horizon:
            raise ValueError(f"Shock '{shock.name}' start month must be inside the horizon.")
