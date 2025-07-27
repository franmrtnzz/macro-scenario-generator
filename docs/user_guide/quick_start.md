# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Option 1: Use the Live Application
Visit our live application: **[Macro Scenario Generator](https://macro-scenario-generator-5tjq2bjtfww7hdkfyspbzg.streamlit.app/)**

### Option 2: Run Locally

1. **Clone the repository:**
```bash
git clone https://github.com/franmrtnzz/macro-scenario-generator.git
cd macro-scenario-generator
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the application:**
```bash
streamlit run streamlit_app.py
```

4. **Open your browser:**
   - Go to `http://localhost:8501`

## 🎯 How to Use

### 1. Load the VAR Model
- Click "Cargar/Entrenar Modelo VAR" in the sidebar
- Wait for the model to train (takes ~10 seconds)

### 2. Choose a Scenario
- **Pre-defined scenarios:** Recession, Inflation, Recovery
- **Custom scenario:** Set your own shock values

### 3. Configure Parameters
- Set time horizon (1-36 months)
- Adjust shock magnitudes for each variable

### 4. Run Simulation
- Click "Ejecutar Escenario"
- View results in charts and tables

### 5. Generate Narrative
- Click "Generar Narrativa" for AI analysis
- Export results to CSV

## 📊 Understanding the Results

### Variables Explained
- **GDP:** Gross Domestic Product (economic growth)
- **Inflation:** Consumer price inflation
- **Policy Rate:** Central bank interest rate
- **Real Rate:** Inflation-adjusted interest rate

### Reading the Charts
- **Blue line (GDP):** Economic growth indicator
- **Other lines:** Monetary and price variables
- **Y-axis:** Normalized values (0-1 scale)
- **X-axis:** Time horizon in months

## 🔧 Troubleshooting

### Common Issues
1. **Model won't load:** Check internet connection
2. **Narrative fails:** Verify OpenAI API key in `.env`
3. **Charts look flat:** This is normal for VAR models

### Need Help?
- Check the [Technical Documentation](../technical/)
- Review the [Architecture Guide](../technical/architecture.md)
- Open an issue on GitHub 