# scripts/generate_narrative_simple.py
"""
Versión simplificada de generación de narrativa para el dashboard.
"""

import os
import sys
import pandas as pd
from typing import Dict, Any

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import openai
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def generate_narrative(simulation_df: pd.DataFrame, scenario_info: Dict[str, Any]) -> str:
    """
    Genera una narrativa económica basada en los datos de simulación.
    
    Args:
        simulation_df: DataFrame con los resultados de la simulación
        scenario_info: Diccionario con información del escenario
    
    Returns:
        str: Narrativa generada
    """
    
    # Verificar que tenemos la API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "❌ Error: OPENAI_API_KEY no está configurada en el archivo .env"
    
    try:
        # Configurar cliente OpenAI
        client = openai.OpenAI(api_key=api_key)
        
        # Construir prompt simplificado
        prompt = build_simple_prompt(simulation_df, scenario_info)
        
        # Llamar a la API
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Usar modelo más económico
            messages=[
                {"role": "system", "content": "You are a macroeconomic analyst. Write clear, concise analysis in English."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        return f"❌ Error generando narrativa: {str(e)}"


def build_simple_prompt(simulation_df: pd.DataFrame, scenario_info: Dict[str, Any]) -> str:
    """
    Construye un prompt simplificado para la narrativa.
    """
    
    scenario_name = scenario_info.get("scenario_name", "Escenario Personalizado")
    
    # Resumen estadístico de los datos
    stats = []
    for column in simulation_df.columns:
        initial = simulation_df[column].iloc[0]
        final = simulation_df[column].iloc[-1]
        change = final - initial
        stats.append(f"{column}: {initial:.3f} → {final:.3f} (change: {change:+.3f})")
    
    stats_text = "\n".join(stats)
    
    prompt = f"""
Analyze this macroeconomic simulation scenario:

**Scenario:** {scenario_name}
**Time Horizon:** {len(simulation_df)} months
**Variables:** {', '.join(simulation_df.columns)}

**Key Statistics:**
{stats_text}

**Data Summary:**
- GDP range: {simulation_df['gdp'].min():.3f} to {simulation_df['gdp'].max():.3f}
- Inflation range: {simulation_df['inflation'].min():.3f} to {simulation_df['inflation'].max():.3f}
- Policy rate range: {simulation_df['policy_rate'].min():.3f} to {simulation_df['policy_rate'].max():.3f}
- Real rate range: {simulation_df['real_rate'].min():.3f} to {simulation_df['real_rate'].max():.3f}

Write a brief economic analysis (200-300 words) that includes:
1. What the simulation shows about economic dynamics
2. Whether the effects are persistent or transitory
3. Policy implications for central banks
4. A key takeaway

Write in clear, professional English.
"""
    
    return prompt


def generate_fallback_narrative(simulation_df: pd.DataFrame, scenario_info: Dict[str, Any]) -> str:
    """
    Genera una narrativa de respaldo sin usar la API de OpenAI.
    """
    
    scenario_name = scenario_info.get("scenario_name", "Escenario Personalizado")
    
    # Calcular estadísticas básicas
    gdp_change = simulation_df['gdp'].iloc[-1] - simulation_df['gdp'].iloc[0]
    inflation_change = simulation_df['inflation'].iloc[-1] - simulation_df['inflation'].iloc[0]
    policy_change = simulation_df['policy_rate'].iloc[-1] - simulation_df['policy_rate'].iloc[0]
    real_change = simulation_df['real_rate'].iloc[-1] - simulation_df['real_rate'].iloc[0]
    
    # Determinar el tipo de escenario
    if gdp_change < -0.05:
        scenario_type = "recesión"
    elif inflation_change > 0.1:
        scenario_type = "inflacionario"
    elif policy_change > 0.1:
        scenario_type = "restrictivo"
    else:
        scenario_type = "estable"
    
    narrative = f"""
**Análisis Macroeconómico: {scenario_name}**

Esta simulación VAR muestra un escenario de tipo {scenario_type} con las siguientes características:

**Evolución de Variables:**
- **PIB**: {gdp_change:+.3f} (de {simulation_df['gdp'].iloc[0]:.3f} a {simulation_df['gdp'].iloc[-1]:.3f})
- **Inflación**: {inflation_change:+.3f} (de {simulation_df['inflation'].iloc[0]:.3f} a {simulation_df['inflation'].iloc[-1]:.3f})
- **Tasa de Política**: {policy_change:+.3f} (de {simulation_df['policy_rate'].iloc[0]:.3f} a {simulation_df['policy_rate'].iloc[-1]:.3f})
- **Tasa Real**: {real_change:+.3f} (de {simulation_df['real_rate'].iloc[0]:.3f} a {simulation_df['real_rate'].iloc[-1]:.3f})

**Interpretación:**
El modelo VAR indica que los shocks aplicados tienen efectos {scenario_type} en la economía. Las variables convergen a un nuevo equilibrio después del período de ajuste inicial.

**Implicaciones de Política:**
Los bancos centrales deberían monitorear de cerca la evolución de estas variables y ajustar la política monetaria según sea necesario para mantener la estabilidad económica.

**Conclusión Clave:**
Este escenario sugiere un período de {scenario_type} que requiere atención cuidadosa de las autoridades monetarias.
"""
    
    return narrative 