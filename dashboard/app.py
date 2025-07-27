# dashboard/app.py
"""
Dashboard Streamlit para el Macro Scenario Generator.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from quant.var_model import train_var_model, simulate_var_shock
from scripts.generate_narrative import generate_narrative
from utils.export import export_complete_analysis


def main():
    st.set_page_config(
        page_title="Macro Scenario Generator",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 Macro Scenario Generator")
    st.markdown("---")
    
    # Sidebar para configuración
    st.sidebar.header("⚙️ Configuración")
    
    # Cargar modelo VAR
    if st.sidebar.button("🔄 Cargar/Entrenar Modelo VAR"):
        with st.spinner("Entrenando modelo VAR..."):
            try:
                var_results = train_var_model("data/series.pkl", lags=1)
                st.session_state['var_results'] = var_results
                st.sidebar.success(f"✅ Modelo entrenado con {len(var_results.names)} variables")
            except Exception as e:
                st.sidebar.error(f"❌ Error: {str(e)}")
    
    # Verificar si el modelo está cargado
    if 'var_results' not in st.session_state:
        st.warning("⚠️ Por favor, carga el modelo VAR desde la barra lateral")
        return
    
    var_results = st.session_state['var_results']
    
    # Mostrar información del modelo
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Variables", len(var_results.names))
    with col2:
        st.metric("Lags", var_results.k_ar)
    with col3:
        st.metric("Observaciones", var_results.nobs)
    
    st.markdown("---")
    
    # Sección de escenarios predefinidos
    st.header("🎯 Escenarios Predefinidos")
    
    scenarios = {
        "Recesión": {
            "gdp": {"magnitude": -0.1},
            "inflation": {"magnitude": 0.05},
            "policy_rate": {"magnitude": -0.02},
            "real_rate": {"magnitude": -0.03}
        },
        "Inflación": {
            "gdp": {"magnitude": -0.05},
            "inflation": {"magnitude": 0.2},
            "policy_rate": {"magnitude": 0.1},
            "real_rate": {"magnitude": 0.05}
        },
        "Recuperación": {
            "gdp": {"magnitude": 0.1},
            "inflation": {"magnitude": 0.02},
            "policy_rate": {"magnitude": 0.05},
            "real_rate": {"magnitude": 0.03}
        }
    }
    
    # Botones para ejecutar escenarios
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📉 Ejecutar Recesión"):
            run_scenario("Recesión", scenarios["Recesión"], var_results)
    
    with col2:
        if st.button("📈 Ejecutar Inflación"):
            run_scenario("Inflación", scenarios["Inflación"], var_results)
    
    with col3:
        if st.button("📊 Ejecutar Recuperación"):
            run_scenario("Recuperación", scenarios["Recuperación"], var_results)
    
    st.markdown("---")
    
    # Sección de escenario personalizado
    st.header("🎛️ Escenario Personalizado")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Configurar Shocks")
        
        custom_shocks = {}
        for var in var_results.names:
            magnitude = st.number_input(
                f"Shock en {var}",
                value=0.0,
                step=0.01,
                format="%.2f"
            )
            if magnitude != 0:
                custom_shocks[var] = {"magnitude": magnitude}
    
    with col2:
        st.subheader("Parámetros")
        steps = st.slider("Horizonte temporal (meses)", 6, 24, 12)
        
        if st.button("🚀 Ejecutar Escenario Personalizado") and custom_shocks:
            run_scenario("Personalizado", custom_shocks, var_results, steps)
    
    # Mostrar resultados si existen
    if 'current_simulation' in st.session_state:
        st.markdown("---")
        st.header("📊 Resultados de la Simulación")
        
        simulation_df = st.session_state['current_simulation']
        scenario_name = st.session_state.get('current_scenario', 'Escenario')
        
        # Gráficos
        plot_simulation_results(simulation_df, scenario_name)
        
        # Estadísticas
        show_simulation_stats(simulation_df)
        
        # Generar narrativa
        if st.button("🤖 Generar Narrativa"):
            with st.spinner("Generando narrativa..."):
                try:
                    narrative = generate_narrative(simulation_df, {"scenario_name": scenario_name})
                    st.session_state['current_narrative'] = narrative
                    st.success("✅ Narrativa generada")
                except Exception as e:
                    st.error(f"❌ Error generando narrativa: {str(e)}")
        
        # Mostrar narrativa si existe
        if 'current_narrative' in st.session_state:
            st.subheader("📝 Narrativa Económica")
            st.markdown(st.session_state['current_narrative'])
        
        # Exportar resultados
        if st.button("💾 Exportar Análisis Completo"):
            with st.spinner("Exportando..."):
                try:
                    narrative = st.session_state.get('current_narrative', None)
                    exported_files = export_complete_analysis(
                        var_results,
                        {scenario_name: simulation_df},
                        narrative
                    )
                    st.success("✅ Análisis exportado exitosamente")
                    st.info(f"📁 Archivos guardados en: {list(exported_files.values())}")
                except Exception as e:
                    st.error(f"❌ Error exportando: {str(e)}")


def run_scenario(scenario_name, shocks, var_results, steps=12):
    """Ejecuta un escenario y guarda los resultados en session_state."""
    with st.spinner(f"Simulando {scenario_name}..."):
        try:
            simulation_df = simulate_var_shock(var_results, shocks, steps=steps)
            st.session_state['current_simulation'] = simulation_df
            st.session_state['current_scenario'] = scenario_name
            st.success(f"✅ Simulación {scenario_name} completada")
        except Exception as e:
            st.error(f"❌ Error en simulación: {str(e)}")


def plot_simulation_results(simulation_df, scenario_name):
    """Crea gráficos interactivos de los resultados de simulación."""
    
    # Gráfico de líneas para todas las variables
    fig = go.Figure()
    
    for column in simulation_df.columns:
        fig.add_trace(go.Scatter(
            x=simulation_df.index,
            y=simulation_df[column],
            mode='lines+markers',
            name=column,
            line=dict(width=2)
        ))
    
    fig.update_layout(
        title=f"Evolución de Variables - {scenario_name}",
        xaxis_title="Tiempo",
        yaxis_title="Valor",
        hovermode='x unified',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Gráficos individuales por variable
    st.subheader("📈 Evolución por Variable")
    
    n_vars = len(simulation_df.columns)
    cols = st.columns(2)
    
    for i, column in enumerate(simulation_df.columns):
        with cols[i % 2]:
            fig_var = px.line(
                simulation_df, 
                y=column,
                title=f"{column} - {scenario_name}",
                markers=True
            )
            fig_var.update_layout(height=300)
            st.plotly_chart(fig_var, use_container_width=True)


def show_simulation_stats(simulation_df):
    """Muestra estadísticas descriptivas de la simulación."""
    st.subheader("📊 Estadísticas de la Simulación")
    
    # Calcular estadísticas
    stats_data = []
    for column in simulation_df.columns:
        stats_data.append({
            'Variable': column,
            'Valor Inicial': simulation_df[column].iloc[0],
            'Valor Final': simulation_df[column].iloc[-1],
            'Cambio Total': simulation_df[column].iloc[-1] - simulation_df[column].iloc[0],
            'Máximo': simulation_df[column].max(),
            'Mínimo': simulation_df[column].min(),
            'Volatilidad': simulation_df[column].std()
        })
    
    stats_df = pd.DataFrame(stats_data)
    st.dataframe(stats_df, use_container_width=True)


if __name__ == "__main__":
    main() 