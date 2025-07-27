# Macro Scenario Generator

A comprehensive macroeconomic scenario generation system using Vector Autoregression (VAR) models and AI-powered narrative generation.

## 🌐 Live Demo

**Access the live application:** [Macro Scenario Generator on Streamlit Cloud](https://macro-scenario-generator.streamlit.app)

## 📋 Project Overview

This project simulates macroeconomic scenarios using VAR models and generates AI-powered narratives for economic analysis. It's designed for central banks, financial institutions, and economic researchers.

## 🏗️ Project Structure

```
macro-scenario-generator/
├── api/                    # External API integrations (ECB, FRED)
├── config/                 # Configuration files and shock rules
├── dashboard/              # Streamlit dashboard components
├── data/                   # Economic time series data
├── docs/                   # Documentation and architecture
├── etl/                    # Data pipeline and transformations
├── figs/                   # Generated figures and charts
├── input/                  # Input templates and scenarios
├── output/                 # Simulation results and exports
├── pruebas/                # Test suite and validation
├── quant/                  # VAR model and quantitative engine
├── scripts/                # Narrative generation and utilities
├── utils/                  # Helper functions and utilities
├── streamlit_app.py        # Main Streamlit application
└── requirements.txt        # Python dependencies
```

## 🚀 Quick Start

### Local Development

1. **Clone the repository:**
```bash
git clone https://github.com/your-username/macro-scenario-generator.git
cd macro-scenario-generator
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the dashboard:**
```bash
streamlit run streamlit_app.py
```

5. **Access the application:**
   - Open your browser and go to `http://localhost:8501`

### Cloud Deployment

The application is automatically deployed on Streamlit Cloud and accessible at:
**https://macro-scenario-generator.streamlit.app**

## 🎯 Core Features

### 1. **Quantitative Engine (VAR Model)**
- **Vector Autoregression (VAR)** with robust preprocessing
- **Automatic variable selection** based on collinearity analysis
- **Intelligent transformations** (diff/level) based on data characteristics
- **Noise injection** for constant variables to ensure model stability

### 2. **Interactive Dashboard**
- **Real-time scenario configuration** with custom shocks
- **Pre-defined scenarios** (recession, inflation, recovery)
- **Dynamic visualizations** with Plotly charts
- **Statistical summaries** and data tables
- **CSV export** functionality

### 3. **AI-Powered Narrative Generation**
- **GPT-4o integration** for economic analysis
- **Automatic narrative generation** based on simulation results
- **Fallback narratives** when API is unavailable
- **Professional economic analysis** in English

### 4. **Data Management**
- **Real economic data** from ECB and FRED APIs
- **Automatic data preprocessing** and frequency conversion
- **Robust error handling** and validation
- **Export capabilities** for further analysis

## 📊 Technical Specifications

- **Model:** VAR(1) with 4 variables (GDP, Inflation, Policy Rate, Real Rate)
- **Data:** Monthly frequency, 353+ observations
- **Framework:** Streamlit for web interface
- **AI:** OpenAI GPT-4o for narrative generation
- **Visualization:** Plotly for interactive charts
- **Testing:** pytest framework with comprehensive test suite

## 🔧 Configuration

### Environment Variables
Create a `.env` file with:
```
OPENAI_API_KEY=your_openai_api_key_here
```

### Model Parameters
- **Lags:** 1 (configurable)
- **Minimum variables:** 2
- **Correlation threshold:** 0.85
- **Standard deviation threshold:** 0.0001

## 📈 Example Outputs

### Simulation Results
- **Time series forecasts** for all variables
- **Statistical summaries** (initial/final values, changes, volatility)
- **Interactive visualizations** with multiple timeframes

### AI Narratives
Professional economic analysis including:
- **Shock impact assessment**
- **Policy implications**
- **Economic interpretation**
- **Key takeaways**

## 🧪 Testing Framework

Run the test suite:
```bash
python -m pytest pruebas/
```

Test coverage includes:
- VAR model training and validation
- Shock simulation accuracy
- Data preprocessing robustness
- Export functionality

## 📚 Dependencies

### Core Libraries
- **pandas** (≥1.5.0): Data manipulation
- **numpy** (≥1.21.0): Numerical computations
- **statsmodels** (≥0.14.0): VAR model implementation
- **scikit-learn** (≥1.3.0): Data preprocessing

### Web Framework
- **streamlit** (≥1.28.0): Web application framework
- **plotly** (≥5.15.0): Interactive visualizations

### AI Integration
- **openai** (≥1.14.0): GPT-4o API integration
- **python-dotenv** (≥1.0.0): Environment variable management

### Visualization
- **matplotlib** (≥3.7.0): Static plotting
- **seaborn** (≥0.12.0): Statistical visualizations

## 🎓 Academic Context

This project was developed as a Master's Final Project (TFM) demonstrating:
- **Advanced econometric modeling** with VAR techniques
- **AI integration** in economic analysis
- **Web application development** for financial tools
- **Professional software engineering** practices

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👨‍💻 Author

**Francisco** - Master's Final Project (TFM)

## 🔗 Links

- **Live Application:** https://macro-scenario-generator.streamlit.app
- **GitHub Repository:** https://github.com/your-username/macro-scenario-generator
- **Documentation:** See `docs/` folder for detailed architecture and usage guides

---

**Status:** Production Ready - All core functionalities operational and tested ✅
