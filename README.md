# 📊 Macro Scenario Generator

[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://macro-scenario-generator-5tjq2bjtfww7hdkfyspbzg.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen?style=for-the-badge)]()

> **Advanced macroeconomic scenario simulation using Vector Autoregression (VAR) models and AI-powered narrative generation**

## 🌐 Live Demo

**[🚀 Try it now!](https://macro-scenario-generator-5tjq2bjtfww7hdkfyspbzg.streamlit.app/)**

## 📋 Overview

The Macro Scenario Generator is a comprehensive tool for simulating and analyzing macroeconomic scenarios. It combines:

- **🔬 Quantitative Modeling**: Robust VAR models for economic forecasting
- **🤖 AI Integration**: GPT-4o powered narrative generation
- **📊 Interactive Dashboard**: Real-time scenario configuration and visualization
- **📈 Real Data**: Economic time series from ECB and FRED APIs

### Key Features

| Feature | Description |
|---------|-------------|
| 🎯 **VAR Modeling** | Vector Autoregression with 4 key variables (GDP, Inflation, Policy Rate, Real Rate) |
| 📊 **Interactive Charts** | Real-time visualization with Plotly |
| 🤖 **AI Narratives** | Automatic economic analysis with GPT-4o |
| 📁 **Export Capabilities** | CSV export for further analysis |
| 🎮 **Custom Scenarios** | User-defined shocks and parameters |
| ⚡ **Real-time Processing** | Instant simulation results |

## 🏗️ Architecture

```
macro-scenario-generator/
├── 📁 api/                    # External API integrations
│   ├── ecb.py                # European Central Bank API
│   └── fred.py               # Federal Reserve API
├── 📁 quant/                  # Core quantitative engine
│   ├── var_model.py          # VAR model implementation
│   └── shock_propagation.py  # Shock simulation logic
├── 📁 dashboard/              # Web interface components
│   └── simple_app.py         # Streamlit dashboard
├── 📁 scripts/                # Utility scripts
│   └── generate_narrative.py # AI narrative generation
├── 📁 data/                   # Economic time series
│   └── series.pkl            # Preprocessed data
├── 📁 docs/                   # Documentation
│   ├── technical/            # Technical documentation
│   └── user_guide/           # User guides
├── 📁 examples/               # Usage examples
├── 📁 tests/                  # Test suite
├── streamlit_app.py          # Main application
└── requirements.txt          # Dependencies
```

## 🚀 Quick Start

### Option 1: Live Application
Visit **[https://macro-scenario-generator-5tjq2bjtfww7hdkfyspbzg.streamlit.app/](https://macro-scenario-generator-5tjq2bjtfww7hdkfyspbzg.streamlit.app/)** and start using immediately!

### Option 2: Local Installation

```bash
# Clone the repository
git clone https://github.com/franmrtnzz/macro-scenario-generator.git
cd macro-scenario-generator

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run streamlit_app.py
```

Open your browser and go to `http://localhost:8501`

## 🎯 How to Use

### 1. Load the Model
Click "Cargar/Entrenar Modelo VAR" in the sidebar to initialize the VAR model.

### 2. Choose a Scenario
- **Pre-defined scenarios**: Recession, Inflation, Recovery
- **Custom scenario**: Set your own shock values

### 3. Configure Parameters
- Set time horizon (1-36 months)
- Adjust shock magnitudes for each variable

### 4. Run Simulation
Click "Ejecutar Escenario" to generate results.

### 5. Analyze Results
- View interactive charts
- Check statistical summaries
- Generate AI-powered narrative
- Export to CSV

## 📊 Understanding the Model

### Variables
- **GDP**: Gross Domestic Product (economic growth indicator)
- **Inflation**: Consumer price inflation (HICP)
- **Policy Rate**: Central bank interest rate
- **Real Rate**: Inflation-adjusted interest rate

### Model Specifications
- **Type**: Vector Autoregression (VAR)
- **Lags**: 1 period
- **Observations**: 353+ monthly periods
- **Data Source**: ECB and FRED APIs
- **Frequency**: Monthly

## 🔧 Configuration

### Environment Variables
Create a `.env` file for API access:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Model Parameters
- **Lags**: 1 (configurable)
- **Minimum variables**: 2
- **Correlation threshold**: 0.85
- **Standard deviation threshold**: 0.0001

## 📚 Documentation

- **[📖 User Guide](docs/user_guide/)** - Complete user documentation
- **[🔧 Technical Docs](docs/technical/)** - Architecture and implementation details
- **[🚀 Quick Start](docs/user_guide/quick_start.md)** - Get started in 5 minutes
- **[📊 Examples](examples/)** - Usage examples and demonstrations

## 🧪 Testing

Run the comprehensive test suite:
```bash
python -m pytest tests/
```

Test coverage includes:
- ✅ VAR model training and validation
- ✅ Shock simulation accuracy
- ✅ Data preprocessing robustness
- ✅ Export functionality

## 📦 Dependencies

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

## 🎓 Academic Context

This project was developed as a **Master's Final Project (TFM)** demonstrating:
- **Advanced econometric modeling** with VAR techniques
- **AI integration** in economic analysis
- **Web application development** for financial tools
- **Professional software engineering** practices

### Citing This Work
If you use this system in your research, please cite:
```
Macro Scenario Generator: A VAR-based Economic Simulation Tool
Francisco Cervantes Martínez
Master's Final Project, 2025
```

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest pytest-cov

# Run tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=quant --cov=scripts
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Francisco Cervantes Martínez** - Master's Final Project (TFM)

## 🔗 Links

- **🌐 Live Application**: [https://macro-scenario-generator-5tjq2bjtfww7hdkfyspbzg.streamlit.app/](https://macro-scenario-generator-5tjq2bjtfww7hdkfyspbzg.streamlit.app/)
- **📚 Documentation**: [docs/](docs/)
- **🐛 Issues**: [GitHub Issues](https://github.com/franmrtnzz/macro-scenario-generator/issues)
- **💬 Discussions**: [GitHub Discussions](https://github.com/franmrtnzz/macro-scenario-generator/discussions)

---

<div align="center">

**⭐ Star this repository if you find it useful!**

[![GitHub stars](https://img.shields.io/github/stars/franmrtnzz/macro-scenario-generator?style=social)](https://github.com/franmrtnzz/macro-scenario-generator/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/franmrtnzz/macro-scenario-generator?style=social)](https://github.com/franmrtnzz/macro-scenario-generator/network/members)

</div>
