# demo_with_export.py
"""
Demostración completa del Macro Scenario Generator con exportación de resultados.
"""

import sys
import os
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.append(str(Path(__file__).parent))

from quant.var_model import train_var_model, simulate_var_shock
from scripts.generate_narrative import generate_narrative
from utils.export import export_complete_analysis


def main():
    print("🚀 MACRO SCENARIO GENERATOR - DEMO CON EXPORTACIÓN")
    print("=" * 60)
    
    # Paso 1: Entrenar modelo VAR
    print("\n📊 PASO 1: Entrenando modelo VAR...")
    try:
        var_results = train_var_model("data/series.pkl", lags=1)
        print(f"✅ Modelo entrenado con {len(var_results.names)} variables: {var_results.names}")
        print(f"   - Lags: {var_results.k_ar}")
        print(f"   - Observaciones: {var_results.nobs}")
    except Exception as e:
        print(f"❌ Error entrenando modelo: {e}")
        return
    
    # Paso 2: Definir escenarios
    print("\n🎯 PASO 2: Definir escenarios...")
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
    
    # Paso 3: Simular escenarios
    print("\n🎯 PASO 3: Simulando escenarios...")
    simulations = {}
    
    for scenario_name, shocks in scenarios.items():
        print(f"\n   📈 Escenario: {scenario_name}")
        try:
            simulation_df = simulate_var_shock(var_results, shocks, steps=12)
            simulations[scenario_name] = simulation_df
            print(f"   ✅ Simulación exitosa: {simulation_df.shape}")
            
            # Mostrar resumen
            print(f"   📊 Resumen de {scenario_name}:")
            for var in simulation_df.columns:
                initial = simulation_df[var].iloc[0]
                final = simulation_df[var].iloc[-1]
                change = final - initial
                print(f"      {var}: {change:+.3f} (inicial: {initial:.3f} → final: {final:.3f})")
                
        except Exception as e:
            print(f"   ❌ Error en simulación: {e}")
    
    # Paso 4: Generar narrativa para el primer escenario
    print("\n🤖 PASO 4: Generando narrativa...")
    try:
        first_scenario = list(simulations.keys())[0]
        first_simulation = simulations[first_scenario]
        
        narrative = generate_narrative(first_simulation, {"scenario_name": first_scenario})
        print(f"✅ Narrativa generada para {first_scenario}")
        print(f"📝 Extracto: {narrative[:200]}...")
        
    except Exception as e:
        print(f"❌ Error generando narrativa: {e}")
        narrative = None
    
    # Paso 5: Exportar análisis completo
    print("\n💾 PASO 5: Exportando análisis completo...")
    try:
        exported_files = export_complete_analysis(
            var_results,
            simulations,
            narrative
        )
        
        print("✅ Análisis exportado exitosamente")
        print("📁 Archivos generados:")
        for file_type, filepath in exported_files.items():
            print(f"   - {file_type}: {filepath}")
            
    except Exception as e:
        print(f"❌ Error exportando: {e}")
    
    # Resumen final
    print("\n🎉 RESUMEN FINAL")
    print("=" * 60)
    print(f"✅ Modelo VAR entrenado con {len(var_results.names)} variables")
    print(f"✅ {len(simulations)} escenarios simulados exitosamente")
    print(f"✅ Narrativa generada: {'Sí' if narrative else 'No'}")
    print(f"✅ Análisis exportado a directorio output/")
    
    print("\n🔧 Próximos pasos:")
    print("   1. Ejecutar 'streamlit run dashboard/app.py' para el dashboard")
    print("   2. Revisar archivos exportados en output/")
    print("   3. Personalizar escenarios en input/shock.json")


if __name__ == "__main__":
    main() 