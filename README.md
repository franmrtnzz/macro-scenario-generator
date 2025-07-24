# 📊 Macro Scenario Generator

**Macro Scenario Generator** is a tool designed to simulate macroeconomic scenarios based on user-defined shocks. It generates consistent time series for key economic variables, provides automatic natural language narratives using LLMs (GPT-4o), and offers a visual dashboard for exploration and export.

---

## 🎯 Objective

To develop an academic and functional tool that integrates real data, a basic quantitative model, and natural language generation to analyze how economic shocks propagate across:

- GDP  
- Inflation  
- Interest rates  
- Sovereign spreads  
- Exchange rates (FX)  
- Equity index

---

## ⚙️ Project Structure

```
macro-scenario-generator/
│
├── data/                  # Raw and processed data (ETL)
├── API/                   # External API calls (FRED, ECB, OpenAI)
├── engine/                # Shock propagation logic and quantitative model
├── dashboard/             # Streamlit app for scenario visualization
├── output/                # Generated scenarios (CSV, markdown, narrative)
├── .env                   # API keys (DO NOT push to GitHub)
├── requirements.txt       # Python dependencies
├── run_scenario.py        # Main script to run full scenario
└── README.md              # Project documentation
```

---

## 🚀 Installation & Usage

### 1. Clone the repository

```bash
git clone https://github.com/your_username/macro-scenario-generator.git
cd macro-scenario-generator
```

### 2. Create and activate virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your API keys

Create a `.env` file in the root directory:

```
FRED_API_KEY=your_fred_key
OPENAI_API_KEY=your_openai_key
```

---

## 📦 Run a scenario

To generate a scenario from a defined shock:

```bash
python run_scenario.py shocks/input_example.json
```

This will produce:

- Time series simulation (CSV)  
- Narrative (Spanish/English)  
- Markdown summary  
- Visual charts for dashboard

---

## 🖥️ Launch the dashboard (optional)

```bash
streamlit run dashboard/app.py
```

---

## 📚 Technical Architecture

The project follows a modular design:

1. **ETL** → Fetch and normalize data from FRED/ECB  
2. **Quant Engine** → Propagate macroeconomic shocks  
3. **Narrative Module** → Generate coherent explanations with GPT-4o  
4. **Export Module** → Write results to CSV, Markdown, Google Sheets  
5. **Dashboard** → Explore output visually with download options  

---

## ✅ Success Metrics (for academic delivery)

- ⏱️ Scenario generation time ≤ 30 seconds  
- ✅ Logical consistency > 95%  
- 📈 Evaluation score ≥ 4/5  
- 💬 At least 50 reactions on LinkedIn when shared as a whitepaper

---
