# Coherence Rules

The engine applies soft coherence checks after each simulation. These checks do not block the scenario; they flag cases that deserve analyst attention.

## Current Checks

1. Inflation rises materially while policy barely responds.
2. Real rates become clearly restrictive while activity weakens.
3. The output gap falls below a recession-risk threshold.
4. No active shock is configured.

## Regime Classification

Each result receives one regime label:

- `Stagflation stress`: high inflation pressure and a materially negative output gap.
- `Recession risk`: GDP growth falls below zero.
- `Inflation pressure`: inflation impulse dominates.
- `Restrictive policy`: real-rate tightening dominates.
- `Contained adjustment`: no single macro stress dominates.

## Interpretation

The checks are designed as product guardrails, not econometric tests. Their role is to help the user understand whether a scenario is internally plausible, uncomfortable, or analytically trivial.
