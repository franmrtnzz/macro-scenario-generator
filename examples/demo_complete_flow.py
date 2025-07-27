#!/usr/bin/env python3
"""
Demo completo del Macro Scenario Generator
==========================================

Este script demuestra todo el flujo del proyecto:
1. Entrenamiento del modelo VAR
2. Simulación de shocks
3. Generación de narrativa con IA
"""

import os
import sys
import pickle
import pandas as pd
from datetime import datetime

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from quant.var_model import train_var_model, simulate_var_shock


def main():
    print("🚀 MACRO SCENARIO GENERATOR - DEMO COMPLETO")
    print("=" * 50)
    
    # 1. Entrenar modelo VAR
    print("\n📊 PASO 1: Entrenando modelo VAR...")
    try:
        results = train_var_model("data/series.pkl", lags=1)
        print(f"✅ Modelo entrenado con {len(results.names)} variables: {results.names}")
        print(f"   - Lags: {results.k_ar}")
        print(f"   - Observaciones: {results.nobs}")
    except Exception as e:
        print(f"❌ Error entrenando modelo: {e}")
        return
    
    # 2. Guardar modelo
    print("\n💾 PASO 2: Guardando modelo...")
    os.makedirs("data/scenarios", exist_ok=True)
    with open("data/scenarios/var_run.pkl", "wb") as f:
        pickle.dump(results, f)
    print("✅ Modelo guardado en data/scenarios/var_run.pkl")
    
    # 3. Simular diferentes escenarios
    print("\n🎯 PASO 3: Simulando escenarios...")
    
    scenarios = {
        "Recesión": {
            "gdp": {"magnitude": -0.2},
            "inflation": {"magnitude": -0.1}
        },
        "Inflación": {
            "inflation": {"magnitude": 0.3},
            "policy_rate": {"magnitude": 0.1}
        },
        "Recuperación": {
            "gdp": {"magnitude": 0.15},
            "inflation": {"magnitude": 0.05}
        }
    }
    
    for scenario_name, shocks in scenarios.items():
        print(f"\n   📈 Escenario: {scenario_name}")
        try:
            forecast = simulate_var_shock(results, shocks, steps=12)
            print(f"   ✅ Simulación exitosa: {forecast.shape}")
            
            # Mostrar resumen de la simulación
            print(f"   📊 Resumen de {scenario_name}:")
            for var in forecast.columns:
                change = forecast[var].iloc[-1] - forecast[var].iloc[0]
                print(f"      {var}: {change:+.3f} (inicial: {forecast[var].iloc[0]:.3f} → final: {forecast[var].iloc[-1]:.3f})")
                
        except Exception as e:
            print(f"   ❌ Error en simulación: {e}")
    
    # 4. Generar narrativa (si OpenAI está disponible)
    print("\n🤖 PASO 4: Generando narrativa con IA...")
    try:
        from scripts.generate_narrative import generate_narrative, build_prompt
        
        # Crear un escenario de ejemplo
        scenario_dict = {
            "scenario_name": "Demo Scenario",
            "author": "Macro Scenario Generator",
            "date_created": datetime.now().strftime("%Y-%m-%d"),
            "shocks": [
                {
                    "variable": "gdp",
                    "magnitude": -0.1,
                    "start_date": "2025-01-01",
                    "duration_months": 6,
                    "shock_type": "demand"
                },
                {
                    "variable": "inflation",
                    "magnitude": 0.2,
                    "start_date": "2025-02-01",
                    "duration_months": 4,
                    "shock_type": "supply"
                }
            ]
        }
        
        # Simular para narrativa
        demo_shocks = {"gdp": {"magnitude": -0.1}, "inflation": {"magnitude": 0.2}}
        sim_df = simulate_var_shock(results, demo_shocks, steps=12)
        
        # Generar narrativa
        prompt = build_prompt(sim_df, scenario_dict)
        narrative = generate_narrative(prompt, temperature=0.3)
        
        print("✅ Narrativa generada exitosamente:")
        print("-" * 40)
        print(narrative[:300] + "..." if len(narrative) > 300 else narrative)
        print("-" * 40)
        
    except ImportError:
        print("⚠️  OpenAI no disponible - saltando generación de narrativa")
    except Exception as e:
        print(f"❌ Error generando narrativa: {e}")
    
    # 5. Resumen final
    print("\n🎉 RESUMEN FINAL")
    print("=" * 50)
    print(f"✅ Modelo VAR entrenado con {len(results.names)} variables")
    print(f"✅ {len(scenarios)} escenarios simulados exitosamente")
    print(f"✅ Modelo guardado en data/scenarios/var_run.pkl")
    print(f"✅ Narrativa generada (si OpenAI disponible)")
    
    print(f"\n📁 Archivos generados:")
    print(f"   - data/scenarios/var_run.pkl (modelo VAR)")
    print(f"   - output/summary.md (narrativa, si aplica)")
    
    print(f"\n🔧 Próximos pasos:")
    print(f"   1. Ajustar parámetros en quant/var_model.py")
    print(f"   2. Crear escenarios personalizados en input/shock.json")
    print(f"   3. Ejecutar scripts/generate_narrative.py para narrativas")
    print(f"   4. Ejecutar python pruebas/test_var_model.py para tests")


if __name__ == "__main__":
    main() 