"""Analyst-style narrative generation for macro scenarios."""

from __future__ import annotations

from quant.macro_engine import (
    DISPLAY_VARIABLES,
    VARIABLE_LABELS,
    VARIABLE_UNITS,
    ScenarioResult,
    ShockChannel,
)


def generate_analyst_note(result: ScenarioResult) -> str:
    """Build a concise macro note from simulated paths and diagnostics."""

    metrics = result.metrics
    frame = result.frame
    regime = str(metrics["regime"])

    shock_text = _shock_summary(result)
    peak_inflation_month = _month_of_extreme(frame, "inflation_scenario", "max")
    growth_trough_month = _month_of_extreme(frame, "gdp_growth_scenario", "min")
    policy_peak_month = _month_of_extreme(frame, "policy_rate_scenario", "max")

    opening = (
        f"**Executive read.** The scenario is classified as **{regime}**. "
        f"{shock_text} The largest inflation reading is "
        f"{metrics['inflation_peak']:.2f}% in {peak_inflation_month}, while GDP growth bottoms at "
        f"{metrics['growth_trough']:.2f}% in {growth_trough_month}."
    )

    transmission = _transmission_paragraph(result)
    policy = (
        f"**Policy read.** The policy-rate path peaks at {metrics['policy_peak']:.2f}% "
        f"in {policy_peak_month}; the real rate reaches {metrics['real_rate_peak']:.2f}%. "
        f"{_policy_interpretation(result)}"
    )

    risks = _risk_paragraph(result)
    takeaway = _takeaway(result)

    return "\n\n".join([opening, transmission, policy, risks, takeaway])


def generate_markdown_report(result: ScenarioResult, title: str = "Macro scenario report") -> str:
    """Create a portable markdown report with assumptions and key metrics."""

    shocks = "\n".join(
        [
            f"- {shock.name}: {shock.channel.value}, {shock.magnitude:+.2f} pp, "
            f"{shock.duration}m duration, {shock.persistence:.2f} persistence, starts month {shock.start_month}"
            for shock in result.shocks
        ]
    ) or "- No active shock."

    metrics = "\n".join(
        [
            f"- Regime: {result.metrics['regime']}",
            f"- Peak inflation: {result.metrics['inflation_peak']:.2f}%",
            f"- GDP growth trough: {result.metrics['growth_trough']:.2f}%",
            f"- Policy-rate peak: {result.metrics['policy_peak']:.2f}%",
            f"- Real-rate peak: {result.metrics['real_rate_peak']:.2f}%",
            f"- Output-gap trough: {result.metrics['output_gap_trough']:.2f}%",
        ]
    )

    warnings = "\n".join([f"- {warning}" for warning in result.warnings]) or "- None."

    return "\n\n".join(
        [
            f"# {title}",
            "## Analyst note",
            generate_analyst_note(result),
            "## Shocks",
            shocks,
            "## Key metrics",
            metrics,
            "## Coherence checks",
            warnings,
        ]
    )


def _shock_summary(result: ScenarioResult) -> str:
    if not result.shocks:
        return "No active shock is configured."

    if len(result.shocks) == 1:
        shock = result.shocks[0]
        return (
            f"The active shock is **{shock.name}**, a {shock.channel.value.lower()} impulse "
            f"of {shock.magnitude:+.2f} pp lasting {shock.duration} months."
        )

    channels = ", ".join(sorted({shock.channel.value for shock in result.shocks}))
    return f"The scenario combines {len(result.shocks)} shocks across {channels} channels."


def _transmission_paragraph(result: ScenarioResult) -> str:
    frame = result.frame
    deltas = {
        variable: float(frame[f"{variable}_delta"].iloc[-1] - frame[f"{variable}_delta"].iloc[0])
        for variable in DISPLAY_VARIABLES
    }
    peak_deltas = {
        variable: _dominant_delta(frame, variable)
        for variable in DISPLAY_VARIABLES
    }

    dominant = sorted(
        ["gdp_growth", "inflation", "policy_rate", "real_rate", "output_gap"],
        key=lambda variable: abs(peak_deltas[variable]),
        reverse=True,
    )[:3]

    details = "; ".join(
        [
            f"{VARIABLE_LABELS[var]} moves by {peak_deltas[var]:+.2f} {VARIABLE_UNITS[var]}"
            for var in dominant
        ]
    )

    direction = "tightens" if frame["policy_rate_delta"].max() > abs(frame["policy_rate_delta"].min()) else "eases"
    activity = "weakens" if frame["gdp_growth_delta"].min() < -0.2 else "stays broadly resilient"
    inflation = "rises" if frame["inflation_delta"].max() > abs(frame["inflation_delta"].min()) else "falls"

    return (
        f"**Transmission.** The impulse propagates through prices, activity and policy with lagged effects. "
        f"Inflation {inflation}, activity {activity}, and the policy stance {direction}. "
        f"The largest contributions are: {details}."
    )


def _policy_interpretation(result: ScenarioResult) -> str:
    frame = result.frame
    inflation_peak_delta = float(frame["inflation_delta"].max())
    growth_trough_delta = float(frame["gdp_growth_delta"].min())
    policy_peak_delta = float(frame["policy_rate_delta"].max())

    has_monetary_shock = any(shock.channel == ShockChannel.MONETARY for shock in result.shocks)

    if has_monetary_shock and policy_peak_delta > 0.4:
        return "This is a deliberately restrictive path; the disinflation benefit arrives only after activity softens."
    if inflation_peak_delta > 0.6 and policy_peak_delta > 0.2:
        return "The reaction function leans against the inflation impulse without fully neutralising the growth cost."
    if growth_trough_delta < -0.5 and policy_peak_delta <= 0.0:
        return "The policy path provides partial cushioning, but the demand loss remains visible."
    return "The policy stance remains close to baseline, so most of the adjustment comes through private-demand and price channels."


def _risk_paragraph(result: ScenarioResult) -> str:
    if result.warnings:
        warning_text = " ".join(result.warnings)
        return f"**Risk flags.** {warning_text}"

    return (
        "**Risk flags.** No hard coherence flag is triggered. The scenario is internally consistent, "
        "but should still be read as a calibrated sensitivity exercise rather than a forecast."
    )


def _takeaway(result: ScenarioResult) -> str:
    regime = str(result.metrics["regime"]).lower()
    if result.metrics["regime"] == "Stagflation stress":
        sentence = "The key risk is an uncomfortable mix of weaker activity and above-target inflation."
    elif result.metrics["regime"] == "Recession risk":
        sentence = "The main macro signal is activity downside, with policy support only partly offsetting the shock."
    elif result.metrics["regime"] == "Inflation pressure":
        sentence = "The scenario is dominated by price pressure and the credibility of the policy response."
    elif result.metrics["regime"] == "Restrictive policy":
        sentence = "The transmission channel is primarily real-rate tightening and delayed demand destruction."
    else:
        sentence = "The adjustment remains contained and does not create a dominant macro stress regime."

    return f"**Key takeaway.** {sentence} ({regime})."


def _month_of_extreme(frame, column: str, direction: str) -> str:
    idx = frame[column].idxmax() if direction == "max" else frame[column].idxmin()
    return frame.loc[idx, "date"].strftime("%b %Y")


def _dominant_delta(frame, variable: str) -> float:
    series = frame[f"{variable}_delta"]
    min_value = float(series.min())
    max_value = float(series.max())
    return max_value if abs(max_value) >= abs(min_value) else min_value
