
# 📊 Macro Scenario Generator

**Macro Scenario Generator** es una herramienta que permite simular escenarios macroeconómicos a partir de shocks definidos por el usuario, generando series temporales coherentes y una narrativa explicativa automática mediante modelos LLM (GPT-4o).

---

## 🧠 Objetivo

Desarrollar una herramienta académica que integre datos reales, modelos cuantitativos y lenguaje natural para analizar cómo se propagan los shocks en variables clave como:

- PIB  
- Inflación  
- Tipos de interés  
- Spreads soberanos  
- Divisas (FX)  
- Equity (índice bursátil)

---

## ⚙️ Estructura del proyecto

```
macro-scenario-generator/
│
├── data/                  # Datos crudos y procesados (ETL)
├── API/                   # Llamadas a APIs externas (FRED, ECB, OpenAI)
├── engine/                # Modelo cuantitativo y funciones de propagación
├── dashboard/             # App Streamlit para visualización
├── output/                # Escenarios generados (CSV, narrativa, Markdown)
├── .env                   # Claves API (NO subir a GitHub)
├── requirements.txt       # Dependencias del proyecto
├── run_scenario.py        # Script principal de orquestación
└── README.md              # Este documento
```

---

## 🚀 Instalación y uso

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu_usuario/macro-scenario-generator.git
cd macro-scenario-generator
```

### 2. Crear y activar entorno virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar claves API

Crea un archivo `.env` con tus claves:

```
FRED_API_KEY=tu_clave_fred
OPENAI_API_KEY=tu_clave_openai
```

---

## 📦 Ejecutar un escenario

Ejecuta el script principal con un archivo de entrada JSON:

```bash
python run_scenario.py shocks/input_example.json
```

Esto generará:

- Series temporales simuladas en CSV  
- Narrativa macroeconómica (ES/EN)  
- Tabla resumen en Markdown  
- Gráficos interactivos en el dashboard

---

## 🖥️ Dashboard (opcional)

Puedes lanzar la interfaz Streamlit con:

```bash
streamlit run dashboard/app.py
```

---

## 📚 Documentación técnica

El proyecto sigue una estructura modular por fases:

1. **ETL** → APIs de FRED y ECB + limpieza de datos  
2. **Modelo cuantitativo** → propagación de shocks  
3. **Narrativa automática** → GPT-4o con tabla in-context  
4. **Exportador** → CSV, Markdown y Google Sheets  
5. **Visualización** → Streamlit dashboard con descarga  

---


>>>>>>> 2332758 (Initial commit: estructura base, .gitignore y dependencias)
