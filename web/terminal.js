const CHANNELS = ["Demand", "Supply / energy", "Monetary policy", "Financial risk", "Fiscal impulse"];

const VARIABLES = {
  gdp_growth: { label: "GDP growth", unit: "% y/y", color: "#22ff72" },
  inflation: { label: "Inflation", unit: "% y/y", color: "#ff9f1a" },
  policy_rate: { label: "Policy rate", unit: "%", color: "#19d9ff" },
  real_rate: { label: "Real rate", unit: "%", color: "#ff13d1" },
  output_gap: { label: "Output gap", unit: "% potential GDP", color: "#d7dde0" },
};

const DISPLAY_VARIABLES = ["gdp_growth", "inflation", "policy_rate", "real_rate", "output_gap"];

// Mock market data. A live API can replace this array while preserving the same shape.
const MARKET_TICKER = [
  { symbol: "ES1", name: "S&P Fut", price: 5318.25, change: 18.5, pct: 0.35 },
  { symbol: "NQ1", name: "Nasdaq Fut", price: 18742.75, change: 92.25, pct: 0.49 },
  { symbol: "DAX", name: "Germany 40", price: 18631.4, change: -41.8, pct: -0.22 },
  { symbol: "SX5E", name: "Euro Stoxx", price: 5037.18, change: 14.21, pct: 0.28 },
  { symbol: "US10Y", name: "UST 10Y", price: 4.41, change: 0.03, pct: 0.68 },
  { symbol: "EURUSD", name: "Euro", price: 1.0832, change: -0.0021, pct: -0.19 },
  { symbol: "WTI", name: "Crude Oil", price: 78.64, change: 1.14, pct: 1.47 },
  { symbol: "XAU", name: "Gold", price: 2348.9, change: -7.8, pct: -0.33 },
  { symbol: "AAPL", name: "Apple", price: 228.75, change: 0.73, pct: 0.32 },
  { symbol: "MSFT", name: "Microsoft", price: 415.57, change: -2.04, pct: -0.49 },
  { symbol: "NVDA", name: "Nvidia", price: 146.73, change: 4.21, pct: 2.95 },
  { symbol: "BTC", name: "Bitcoin", price: 93299.0, change: 213.4, pct: 0.23 },
];

const BASELINE = {
  trend_growth: 1.3,
  initial_gdp_growth: 1.1,
  target_inflation: 2.0,
  initial_inflation: 2.4,
  neutral_real_rate: 1.0,
  initial_policy_rate: 3.25,
  initial_output_gap: -0.2,
};

const RESPONSE_PROFILES = {
  Demand: {
    gdp_growth: [0.75, 0.55, 0.36, 0.2, 0.1],
    output_gap: [0.6, 0.5, 0.36, 0.22, 0.1],
    inflation: [0.06, 0.11, 0.16, 0.14, 0.09, 0.04],
    policy_rate: [0.02, 0.05, 0.09, 0.1, 0.07, 0.03],
  },
  "Supply / energy": {
    inflation: [0.72, 0.62, 0.48, 0.33, 0.2, 0.1],
    gdp_growth: [-0.24, -0.3, -0.23, -0.14, -0.06],
    output_gap: [-0.18, -0.24, -0.2, -0.12, -0.05],
    policy_rate: [0.07, 0.16, 0.24, 0.24, 0.16, 0.08],
  },
  "Monetary policy": {
    policy_rate: [1.0, 0.92, 0.78, 0.58, 0.38, 0.2],
    gdp_growth: [0.0, -0.05, -0.14, -0.22, -0.22, -0.16, -0.08],
    output_gap: [0.0, -0.04, -0.1, -0.18, -0.2, -0.16, -0.09],
    inflation: [0.0, 0.0, -0.03, -0.08, -0.12, -0.12, -0.07, -0.03],
  },
  "Financial risk": {
    gdp_growth: [-0.56, -0.45, -0.28, -0.14, -0.06],
    output_gap: [-0.42, -0.36, -0.24, -0.12, -0.05],
    inflation: [-0.03, -0.06, -0.08, -0.06, -0.03],
    policy_rate: [-0.04, -0.1, -0.16, -0.18, -0.12, -0.06],
  },
  "Fiscal impulse": {
    gdp_growth: [0.52, 0.45, 0.3, 0.16, 0.06],
    output_gap: [0.42, 0.36, 0.25, 0.12, 0.05],
    inflation: [0.04, 0.08, 0.11, 0.09, 0.04],
    policy_rate: [0.0, 0.03, 0.07, 0.08, 0.05],
  },
};

const PRESETS = {
  "Energy price shock": {
    description: "Inflationary supply shock with a negative activity impulse.",
    horizon: 24,
    shocks: [{ name: "Energy price shock", channel: "Supply / energy", magnitude: 1.6, duration: 5, persistence: 0.82, start_month: 1 }],
  },
  "Monetary tightening": {
    description: "Front-loaded policy tightening transmitted to output and inflation with lags.",
    horizon: 24,
    shocks: [{ name: "Rate shock", channel: "Monetary policy", magnitude: 1.0, duration: 4, persistence: 0.8, start_month: 1 }],
  },
  "Demand slowdown": {
    description: "Broad demand deterioration with disinflationary pressure.",
    horizon: 24,
    shocks: [{ name: "Demand slowdown", channel: "Demand", magnitude: -1.1, duration: 4, persistence: 0.78, start_month: 1 }],
  },
  "Soft landing": {
    description: "Moderate demand cooling paired with a contained policy response.",
    horizon: 24,
    shocks: [
      { name: "Demand cooling", channel: "Demand", magnitude: -0.45, duration: 4, persistence: 0.7, start_month: 1 },
      { name: "Policy support", channel: "Monetary policy", magnitude: -0.35, duration: 3, persistence: 0.75, start_month: 4 },
    ],
  },
  "Risk-off stress": {
    description: "Financial conditions shock with weaker activity and easier policy path.",
    horizon: 24,
    shocks: [{ name: "Risk-off shock", channel: "Financial risk", magnitude: 1.2, duration: 4, persistence: 0.8, start_month: 1 }],
  },
};

let state = {
  preset: "Energy price shock",
  horizon: 24,
  shocks: structuredClone(PRESETS["Energy price shock"].shocks),
  baseline: { ...BASELINE },
  selectedVariables: ["gdp_growth", "inflation", "policy_rate", "real_rate"],
  result: null,
};

const $ = (id) => document.getElementById(id);

function init() {
  hydratePresetSelect();
  hydrateBaselineInputs();
  hydrateVariableToggles();
  bindGlobalEvents();
  renderStockTicker(MARKET_TICKER);
  updateClock();
  setInterval(updateClock, 1000);
  renderAll();
}

function hydratePresetSelect() {
  const select = $("presetSelect");
  select.innerHTML = Object.keys(PRESETS).map((name) => `<option value="${name}">${name}</option>`).join("");
  select.value = state.preset;
}

function hydrateBaselineInputs() {
  const map = {
    trendGrowth: "trend_growth",
    initialGrowth: "initial_gdp_growth",
    initialInflation: "initial_inflation",
    targetInflation: "target_inflation",
    initialPolicy: "initial_policy_rate",
    neutralReal: "neutral_real_rate",
    initialGap: "initial_output_gap",
  };
  for (const [inputId, key] of Object.entries(map)) {
    $(inputId).value = state.baseline[key];
    $(inputId).addEventListener("input", (event) => {
      state.baseline[key] = Number(event.target.value);
      renderAll();
    });
  }
}

function hydrateVariableToggles() {
  $("variableToggles").innerHTML = DISPLAY_VARIABLES.map((variable) => {
    const checked = state.selectedVariables.includes(variable) ? "checked" : "";
    return `<label class="variable-toggle"><input type="checkbox" value="${variable}" ${checked} />${VARIABLES[variable].label}</label>`;
  }).join("");

  $("variableToggles").addEventListener("change", () => {
    state.selectedVariables = [...document.querySelectorAll("#variableToggles input:checked")].map((input) => input.value);
    if (state.selectedVariables.length === 0) {
      state.selectedVariables = ["inflation"];
    }
    renderCharts();
  });
}

function bindGlobalEvents() {
  $("presetSelect").addEventListener("change", (event) => {
    const preset = PRESETS[event.target.value];
    state.preset = event.target.value;
    state.horizon = preset.horizon;
    state.shocks = structuredClone(preset.shocks);
    renderAll();
  });

  $("horizonInput").addEventListener("input", (event) => {
    state.horizon = Number(event.target.value);
    renderAll();
  });

  $("addShockButton").addEventListener("click", () => {
    state.shocks.push({ name: "Custom shock", channel: "Demand", magnitude: 0.5, duration: 3, persistence: 0.75, start_month: 1 });
    renderAll();
  });

  document.querySelectorAll(".tab-button").forEach((button) => {
    button.addEventListener("click", () => setTab(button.dataset.tab));
  });

  $("downloadCsv").addEventListener("click", downloadCsv);
  $("downloadReport").addEventListener("click", downloadReport);
}

function renderAll() {
  $("presetSelect").value = state.preset;
  $("presetDescription").textContent = PRESETS[state.preset].description;
  $("horizonInput").value = state.horizon;
  $("horizonOutput").textContent = `${state.horizon} months`;
  state.result = simulateScenario(state.shocks, state.horizon, state.baseline);
  renderMarketStrip();
  renderShockList();
  renderMetrics();
  renderScenarioMatrix();
  renderCharts();
  renderWarnings();
  renderNote();
  renderTable();
}

function renderStockTicker(items) {
  const cells = [...items, ...items].map((asset) => {
    const direction = asset.change >= 0 ? "up" : "down";
    const arrow = asset.change >= 0 ? "▲" : "▼";
    return `
      <span class="ticker-item ${direction}">
        <strong>${asset.symbol}</strong>
        <em>${asset.name}</em>
        <b>${formatMarketPrice(asset.price)}</b>
        <i>${arrow} ${signed(asset.change)} (${signed(asset.pct)}%)</i>
      </span>
    `;
  }).join("");
  $("stockTickerTrack").innerHTML = cells;
}

function renderShockList() {
  $("shockList").innerHTML = state.shocks.map((shock, index) => {
    const channelOptions = CHANNELS.map((channel) => `<option value="${channel}" ${channel === shock.channel ? "selected" : ""}>${channel}</option>`).join("");
    return `
      <article class="shock-card" data-index="${index}">
        <div class="shock-card-header">
          <div class="shock-card-title">${escapeHtml(shock.name || "Shock")}</div>
          <button class="icon-button" type="button" data-remove="${index}" aria-label="Remove shock">x</button>
        </div>
        <div class="shock-grid">
          <label class="shock-field"><span>Name</span><input data-key="name" value="${escapeHtml(shock.name)}" /></label>
          <label class="shock-field"><span>Channel</span><select data-key="channel">${channelOptions}</select></label>
          <label class="shock-field"><span>Magnitude</span><input data-key="magnitude" type="number" step="0.1" value="${shock.magnitude}" /></label>
          <label class="shock-field"><span>Duration</span><input data-key="duration" type="number" min="1" max="60" step="1" value="${shock.duration}" /></label>
          <label class="shock-field"><span>Persistence</span><input data-key="persistence" type="number" min="0" max="0.98" step="0.05" value="${shock.persistence}" /></label>
          <label class="shock-field"><span>Start month</span><input data-key="start_month" type="number" min="1" max="60" step="1" value="${shock.start_month}" /></label>
        </div>
      </article>
    `;
  }).join("");

  $("shockList").querySelectorAll("[data-key]").forEach((input) => {
    input.addEventListener("change", (event) => {
      const card = event.target.closest(".shock-card");
      const index = Number(card.dataset.index);
      const key = event.target.dataset.key;
      state.shocks[index][key] = key === "name" || key === "channel" ? event.target.value : Number(event.target.value);
      renderAll();
    });
  });

  $("shockList").querySelectorAll("[data-remove]").forEach((button) => {
    button.addEventListener("click", (event) => {
      state.shocks.splice(Number(event.target.dataset.remove), 1);
      renderAll();
    });
  });
}

function simulateScenario(shocks, horizon, baseline) {
  const frame = baselinePath(horizon, baseline);
  const contributions = Object.fromEntries(DISPLAY_VARIABLES.map((variable) => [variable, Array(horizon).fill(0)]));

  shocks.filter((shock) => Math.abs(Number(shock.magnitude || 0)) > 1e-9).forEach((shock) => applyShock(contributions, normalizeShock(shock), horizon));

  for (const variable of DISPLAY_VARIABLES) {
    if (variable === "real_rate") continue;
    frame.forEach((row, index) => {
      row[`${variable}_delta`] = contributions[variable][index];
      row[`${variable}_scenario`] = row[`${variable}_baseline`] + row[`${variable}_delta`];
    });
  }

  frame.forEach((row) => {
    row.real_rate_scenario = row.policy_rate_scenario - row.inflation_scenario;
    row.real_rate_delta = row.real_rate_scenario - row.real_rate_baseline;
  });

  const metrics = scenarioMetrics(frame);
  const warnings = coherenceWarnings(frame, shocks);
  return { frame, shocks, baseline, metrics, warnings };
}

function baselinePath(horizon, baseline) {
  const rows = [];
  const neutralPolicyRate = baseline.target_inflation + baseline.neutral_real_rate;
  const startDate = new Date(Date.UTC(2026, 5, 1));

  for (let t = 0; t < horizon; t += 1) {
    const date = new Date(startDate);
    date.setUTCMonth(startDate.getUTCMonth() + t);
    const outputGap = baseline.initial_output_gap * 0.91 ** t;
    const inflationGap = (baseline.initial_inflation - baseline.target_inflation) * 0.94 ** t;
    const inflation = baseline.target_inflation + inflationGap + 0.08 * outputGap;
    const policyGap = (baseline.initial_policy_rate - neutralPolicyRate) * 0.92 ** t;
    const policyRate = neutralPolicyRate + policyGap + 0.22 * inflationGap + 0.08 * outputGap;
    const gdpGrowth = baseline.trend_growth + 0.35 * outputGap;

    rows.push({
      date,
      gdp_growth_baseline: gdpGrowth,
      inflation_baseline: inflation,
      policy_rate_baseline: policyRate,
      real_rate_baseline: policyRate - inflation,
      output_gap_baseline: outputGap,
    });
  }
  return rows;
}

function normalizeShock(shock) {
  return {
    name: shock.name || shock.channel,
    channel: CHANNELS.includes(shock.channel) ? shock.channel : "Demand",
    magnitude: clamp(Number(shock.magnitude), -6, 6),
    duration: Math.max(1, Math.round(Number(shock.duration) || 1)),
    persistence: clamp(Number(shock.persistence), 0, 0.98),
    start_month: Math.max(1, Math.round(Number(shock.start_month) || 1)),
  };
}

function applyShock(contributions, shock, horizon) {
  const profile = RESPONSE_PROFILES[shock.channel];
  const start = shock.start_month - 1;
  const stop = Math.min(horizon, start + shock.duration);

  for (let t = start; t < stop; t += 1) {
    const impulse = shock.magnitude * shock.persistence ** (t - start);
    for (const [variable, coefficients] of Object.entries(profile)) {
      coefficients.forEach((coefficient, lag) => {
        const target = t + lag;
        if (target < horizon) {
          contributions[variable][target] += impulse * coefficient;
        }
      });
    }
  }
}

function scenarioMetrics(frame) {
  const inflationPeak = max(frame, "inflation_scenario");
  const inflationPeakDelta = max(frame, "inflation_delta");
  const growthTrough = min(frame, "gdp_growth_scenario");
  const growthTroughDelta = min(frame, "gdp_growth_delta");
  const policyPeak = max(frame, "policy_rate_scenario");
  const realRatePeak = max(frame, "real_rate_scenario");
  const outputGapTrough = min(frame, "output_gap_scenario");

  let regime = "Contained adjustment";
  if (inflationPeak >= 3.5 && outputGapTrough <= -1.0) regime = "Stagflation stress";
  else if (growthTrough < 0.0) regime = "Recession risk";
  else if (inflationPeakDelta > 0.7) regime = "Inflation pressure";
  else if (realRatePeak > 2.0) regime = "Restrictive policy";

  return { regime, inflationPeak, inflationPeakDelta, growthTrough, growthTroughDelta, policyPeak, realRatePeak, outputGapTrough };
}

function coherenceWarnings(frame, shocks) {
  const warnings = [];
  const inflationDeltaPeak = max(frame, "inflation_delta");
  const policyDeltaPeak = max(frame, "policy_rate_delta");
  const growthDeltaTrough = min(frame, "gdp_growth_delta");
  const outputGapTrough = min(frame, "output_gap_scenario");
  const realRatePeak = max(frame, "real_rate_scenario");

  if (inflationDeltaPeak > 0.7 && policyDeltaPeak < 0.05) warnings.push("Inflation rises materially while the policy path barely responds.");
  if (inflationDeltaPeak > 0.7 && outputGapTrough < -1.0) warnings.push("The scenario combines above-baseline inflation with a negative output gap.");
  if (realRatePeak > 2.5 && growthDeltaTrough < -0.5) warnings.push("Real rates enter a clearly restrictive zone and activity weakens.");
  if (outputGapTrough < -2.0) warnings.push("The output gap falls below -2%, so recession risk dominates the scenario.");
  if (shocks.length === 0) warnings.push("No active shock is configured; the scenario equals the baseline path.");

  return warnings;
}

function renderMetrics() {
  const metrics = state.result.metrics;
  const cards = [
    ["Regime", metrics.regime, "", "#ff9f1a"],
    ["Peak inflation", `${fmt(metrics.inflationPeak)}%`, `${signed(metrics.inflationPeakDelta)} pp`, "#ff9f1a"],
    ["GDP trough", `${fmt(metrics.growthTrough)}%`, `${signed(metrics.growthTroughDelta)} pp`, "#22ff72"],
    ["Policy peak", `${fmt(metrics.policyPeak)}%`, "", "#19d9ff"],
    ["Real-rate peak", `${fmt(metrics.realRatePeak)}%`, "", "#ff13d1"],
  ];

  $("metricGrid").innerHTML = cards.map(([label, value, subvalue, color]) => `
    <article class="metric-card" style="border-left-color:${color}">
      <div class="metric-label">${label}</div>
      <div class="metric-value">${value}</div>
      <div class="metric-subvalue">${subvalue}</div>
    </article>
  `).join("");
}

function renderMarketStrip() {
  const frame = state.result.frame;
  const first = frame[0];
  const last = frame[frame.length - 1];
  const cells = [
    ["GDPG", last.gdp_growth_scenario, last.gdp_growth_delta, "% y/y"],
    ["CPI", max(frame, "inflation_scenario"), max(frame, "inflation_delta"), "peak"],
    ["POLR", max(frame, "policy_rate_scenario"), max(frame, "policy_rate_delta"), "peak"],
    ["REAL", max(frame, "real_rate_scenario"), max(frame, "real_rate_delta"), "peak"],
    ["OGAP", min(frame, "output_gap_scenario"), min(frame, "output_gap_delta"), "trough"],
    ["HORIZ", state.horizon, state.horizon - 24, "months"],
  ];

  $("marketStrip").innerHTML = cells.map(([code, value, change, unit]) => {
    const direction = Number(change) >= 0 ? "up" : "down";
    return `
      <article class="market-cell">
        <span><em>${code}</em><b class="${direction}">${signed(change)}</b></span>
        <strong>${fmt(value)}</strong>
        <span><em>${unit}</em><b>${formatDate(first.date).slice(0, 7)} - ${formatDate(last.date).slice(0, 7)}</b></span>
      </article>
    `;
  }).join("");
}

function renderScenarioMatrix() {
  const frame = state.result.frame;
  const metrics = state.result.metrics;
  $("regimeLabel").textContent = metrics.regime;

  const rows = DISPLAY_VARIABLES.map((variable) => {
    const info = VARIABLES[variable];
    const baseline = frame[frame.length - 1][`${variable}_baseline`];
    const scenario = frame[frame.length - 1][`${variable}_scenario`];
    const delta = frame[frame.length - 1][`${variable}_delta`];
    const peak = max(frame, `${variable}_scenario`);
    const trough = min(frame, `${variable}_scenario`);
    const cls = delta >= 0 ? "pos" : "neg";
    return `
      <tr>
        <td>${info.label}</td>
        <td>${fmt(baseline)}</td>
        <td>${fmt(scenario)}</td>
        <td class="${cls}">${signed(delta)}</td>
        <td>${fmt(peak)}</td>
        <td>${fmt(trough)}</td>
        <td>${info.unit}</td>
      </tr>
    `;
  }).join("");

  $("scenarioMatrix").innerHTML = `
    <thead>
      <tr><th>Variable</th><th>Base</th><th>Scenario</th><th>Chg</th><th>High</th><th>Low</th><th>Unit</th></tr>
    </thead>
    <tbody>${rows}</tbody>
  `;
}

function renderCharts() {
  const frame = state.result.frame;
  const dates = frame.map((row) => row.date);
  const traces = [];

  state.selectedVariables.forEach((variable) => {
    const info = VARIABLES[variable];
    traces.push({
      x: dates,
      y: frame.map((row) => row[`${variable}_baseline`]),
      name: `${info.label} baseline`,
      type: "scatter",
      mode: "lines",
      line: { color: info.color, width: 1.6, dash: "dot" },
    });
    traces.push({
      x: dates,
      y: frame.map((row) => row[`${variable}_scenario`]),
      name: `${info.label} scenario`,
      type: "scatter",
      mode: "lines",
      line: { color: info.color, width: 2.7 },
    });
  });

  Plotly.react("pathsChart", traces, chartLayout("Macro paths"), { responsive: true, displayModeBar: false });

  const deltaTraces = DISPLAY_VARIABLES.map((variable) => ({
    x: dates,
    y: frame.map((row) => row[`${variable}_delta`]),
    name: `${VARIABLES[variable].label} (${VARIABLES[variable].unit})`,
    type: "scatter",
    mode: "lines",
    line: { color: VARIABLES[variable].color, width: 2.6 },
  }));
  Plotly.react("impactChart", deltaTraces, { ...chartLayout("Deviation from baseline"), shapes: [{ type: "line", xref: "paper", x0: 0, x1: 1, y0: 0, y1: 0, line: { color: "#9ba59d", width: 1 } }] }, { responsive: true, displayModeBar: false });
}

function chartLayout(title) {
  return {
    title: { text: title, font: { size: 14, color: "#d7dde0" } },
    height: 460,
    margin: { l: 52, r: 28, t: 38, b: 42 },
    paper_bgcolor: "#020202",
    plot_bgcolor: "#020202",
    font: { family: "IBM Plex Mono, Roboto Mono, SFMono-Regular, Consolas, monospace", color: "#d7dde0" },
    hovermode: "x unified",
    legend: { orientation: "h", y: -0.22, font: { color: "#d7dde0" } },
    xaxis: { showgrid: true, gridcolor: "rgba(120, 141, 154, 0.28)", zerolinecolor: "#3a3a3a", color: "#aeb5b9" },
    yaxis: { gridcolor: "rgba(120, 141, 154, 0.28)", zerolinecolor: "#616161", color: "#aeb5b9" },
  };
}

function renderWarnings() {
  const warnings = state.result.warnings;
  $("warningList").innerHTML = warnings.length
    ? warnings.map((warning) => `<div class="warning">${warning}</div>`).join("")
    : `<div class="warning">No coherence flags triggered.</div>`;
}

function renderNote() {
  $("analystNote").innerHTML = markdownParagraphs(generateAnalystNote(state.result));
}

function generateAnalystNote(result) {
  const frame = result.frame;
  const metrics = result.metrics;
  const inflationPeakMonth = monthOfExtreme(frame, "inflation_scenario", "max");
  const growthTroughMonth = monthOfExtreme(frame, "gdp_growth_scenario", "min");
  const policyPeakMonth = monthOfExtreme(frame, "policy_rate_scenario", "max");
  const shockText = shockSummary(result.shocks);
  const transmission = transmissionParagraph(result);
  const policy = policyInterpretation(result);
  const risk = result.warnings.length
    ? `**Risk flags.** ${result.warnings.join(" ")}`
    : "**Risk flags.** No hard coherence flag is triggered. The scenario is internally consistent, but should still be read as a calibrated sensitivity exercise rather than a forecast.";
  const takeaway = keyTakeaway(metrics.regime);

  return [
    `**Executive read.** The scenario is classified as **${metrics.regime}**. ${shockText} The largest inflation reading is ${fmt(metrics.inflationPeak)}% in ${inflationPeakMonth}, while GDP growth bottoms at ${fmt(metrics.growthTrough)}% in ${growthTroughMonth}.`,
    transmission,
    `**Policy read.** The policy-rate path peaks at ${fmt(metrics.policyPeak)}% in ${policyPeakMonth}; the real rate reaches ${fmt(metrics.realRatePeak)}%. ${policy}`,
    risk,
    `**Key takeaway.** ${takeaway}`,
  ].join("\n\n");
}

function shockSummary(shocks) {
  if (!shocks.length) return "No active shock is configured.";
  if (shocks.length === 1) {
    const shock = normalizeShock(shocks[0]);
    return `The active shock is **${shock.name}**, a ${shock.channel.toLowerCase()} impulse of ${signed(shock.magnitude)} pp lasting ${shock.duration} months.`;
  }
  const channels = [...new Set(shocks.map((shock) => normalizeShock(shock).channel))].sort().join(", ");
  return `The scenario combines ${shocks.length} shocks across ${channels} channels.`;
}

function transmissionParagraph(result) {
  const frame = result.frame;
  const dominant = DISPLAY_VARIABLES
    .map((variable) => [variable, dominantDelta(frame, variable)])
    .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
    .slice(0, 3)
    .map(([variable, value]) => `${VARIABLES[variable].label} moves by ${signed(value)} ${VARIABLES[variable].unit}`)
    .join("; ");
  const policy = max(frame, "policy_rate_delta") > Math.abs(min(frame, "policy_rate_delta")) ? "tightens" : "eases";
  const activity = min(frame, "gdp_growth_delta") < -0.2 ? "weakens" : "stays broadly resilient";
  const inflation = max(frame, "inflation_delta") > Math.abs(min(frame, "inflation_delta")) ? "rises" : "falls";
  return `**Transmission.** The impulse propagates through prices, activity and policy with lagged effects. Inflation ${inflation}, activity ${activity}, and the policy stance ${policy}. The largest contributions are: ${dominant}.`;
}

function policyInterpretation(result) {
  const frame = result.frame;
  const inflationPeakDelta = max(frame, "inflation_delta");
  const growthTroughDelta = min(frame, "gdp_growth_delta");
  const policyPeakDelta = max(frame, "policy_rate_delta");
  const hasMonetaryShock = result.shocks.some((shock) => shock.channel === "Monetary policy");

  if (hasMonetaryShock && policyPeakDelta > 0.4) return "This is a deliberately restrictive path; the disinflation benefit arrives only after activity softens.";
  if (inflationPeakDelta > 0.6 && policyPeakDelta > 0.2) return "The reaction function leans against the inflation impulse without fully neutralising the growth cost.";
  if (growthTroughDelta < -0.5 && policyPeakDelta <= 0.0) return "The policy path provides partial cushioning, but the demand loss remains visible.";
  return "The policy stance remains close to baseline, so most of the adjustment comes through private-demand and price channels.";
}

function keyTakeaway(regime) {
  if (regime === "Stagflation stress") return "The key risk is an uncomfortable mix of weaker activity and above-target inflation.";
  if (regime === "Recession risk") return "The main macro signal is activity downside, with policy support only partly offsetting the shock.";
  if (regime === "Inflation pressure") return "The scenario is dominated by price pressure and the credibility of the policy response.";
  if (regime === "Restrictive policy") return "The transmission channel is primarily real-rate tightening and delayed demand destruction.";
  return "The adjustment remains contained and does not create a dominant macro stress regime.";
}

function renderTable() {
  const rows = longFrame(state.result);
  const preview = rows.slice(0, 160);
  $("dataTable").innerHTML = `
    <thead><tr><th>Date</th><th>Variable</th><th>Baseline</th><th>Scenario</th><th>Delta</th><th>Unit</th></tr></thead>
    <tbody>
      ${preview.map((row) => `
        <tr>
          <td>${formatDate(row.date)}</td>
          <td>${row.label}</td>
          <td>${fmt(row.baseline)}</td>
          <td>${fmt(row.scenario)}</td>
          <td class="${row.delta >= 0 ? "pos" : "neg"}">${signed(row.delta)}</td>
          <td>${row.unit}</td>
        </tr>
      `).join("")}
    </tbody>
  `;
}

function longFrame(result) {
  return result.frame.flatMap((row) => DISPLAY_VARIABLES.map((variable) => ({
    date: row.date,
    variable,
    label: VARIABLES[variable].label,
    unit: VARIABLES[variable].unit,
    baseline: row[`${variable}_baseline`],
    scenario: row[`${variable}_scenario`],
    delta: row[`${variable}_delta`],
  })));
}

function setTab(name) {
  document.querySelectorAll(".tab-button").forEach((button) => button.classList.toggle("active", button.dataset.tab === name));
  document.querySelectorAll(".tab-panel").forEach((panel) => panel.classList.remove("active"));
  $(`${name}Tab`).classList.add("active");
  setTimeout(renderCharts, 0);
}

function downloadCsv() {
  const rows = longFrame(state.result);
  const header = ["date", "variable", "label", "unit", "baseline", "scenario", "delta"];
  const csv = [header.join(","), ...rows.map((row) => header.map((key) => {
    const value = key === "date" ? formatDate(row[key]) : row[key];
    return `"${String(value).replaceAll('"', '""')}"`;
  }).join(","))].join("\n");
  downloadBlob(csv, "macro_scenario_data.csv", "text/csv");
}

function downloadReport() {
  downloadBlob(generateMarkdownReport(state.result), "macro_scenario_report.md", "text/markdown");
}

function generateMarkdownReport(result) {
  const shocks = result.shocks.length
    ? result.shocks.map((shock) => `- ${shock.name}: ${shock.channel}, ${signed(shock.magnitude)} pp, ${shock.duration}m duration, ${fmt(shock.persistence)} persistence, starts month ${shock.start_month}`).join("\n")
    : "- No active shock.";
  const metrics = result.metrics;
  const warnings = result.warnings.length ? result.warnings.map((warning) => `- ${warning}`).join("\n") : "- None.";
  return [
    "# Macro scenario report",
    "## Analyst note",
    generateAnalystNote(result),
    "## Shocks",
    shocks,
    "## Key metrics",
    `- Regime: ${metrics.regime}\n- Peak inflation: ${fmt(metrics.inflationPeak)}%\n- GDP growth trough: ${fmt(metrics.growthTrough)}%\n- Policy-rate peak: ${fmt(metrics.policyPeak)}%\n- Real-rate peak: ${fmt(metrics.realRatePeak)}%\n- Output-gap trough: ${fmt(metrics.outputGapTrough)}%`,
    "## Coherence checks",
    warnings,
  ].join("\n\n");
}

function downloadBlob(content, filename, type) {
  const blob = new Blob([content], { type });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

function markdownParagraphs(text) {
  return text.split("\n\n").map((paragraph) => `<p>${escapeHtml(paragraph).replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")}</p>`).join("");
}

function dominantDelta(frame, variable) {
  const low = min(frame, `${variable}_delta`);
  const high = max(frame, `${variable}_delta`);
  return Math.abs(high) >= Math.abs(low) ? high : low;
}

function monthOfExtreme(frame, column, direction) {
  const target = direction === "max" ? max(frame, column) : min(frame, column);
  const row = frame.find((item) => item[column] === target);
  return row.date.toLocaleDateString("en-US", { month: "short", year: "numeric", timeZone: "UTC" });
}

function max(rows, key) {
  return Math.max(...rows.map((row) => row[key]));
}

function min(rows, key) {
  return Math.min(...rows.map((row) => row[key]));
}

function fmt(value) {
  return Number(value).toFixed(2);
}

function signed(value) {
  const number = Number(value);
  return `${number >= 0 ? "+" : ""}${fmt(number)}`;
}

function formatDate(date) {
  return date.toISOString().slice(0, 10);
}

function formatMarketPrice(value) {
  const number = Number(value);
  if (Math.abs(number) >= 1000) return number.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  if (Math.abs(number) >= 10) return number.toFixed(2);
  return number.toFixed(4);
}

function clamp(value, low, high) {
  if (Number.isNaN(value)) return low;
  return Math.min(high, Math.max(low, value));
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  })[char]);
}

function updateClock() {
  const clock = $("clockDisplay");
  if (!clock) return;
  clock.textContent = new Date().toLocaleTimeString("en-GB", { hour12: false });
}

document.addEventListener("DOMContentLoaded", init);
