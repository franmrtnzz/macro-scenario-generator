# scripts/generate_narrative.py
import os
import sys
import json
import pickle
import pandas as pd

# Añadir el directorio raíz al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import openai
from dotenv import load_dotenv

# ────────────────────────────────────────────────────────────────────────────────
# 1. Cargar variables de entorno (.env) y API key
# ────────────────────────────────────────────────────────────────────────────────
load_dotenv()  # lee .env que contiene OPENAI_API_KEY
if os.getenv("OPENAI_API_KEY") is None:
    raise RuntimeError("OPENAI_API_KEY no está definida en el archivo .env")

# ────────────────────────────────────────────────────────────────────────────────
# 2. Utilidades
# ────────────────────────────────────────────────────────────────────────────────
def load_data(simulation_path: str, shock_path: str):
    """Carga DataFrame de simulación VAR y escenario de shocks."""
    with open(simulation_path, "rb") as f:
        var_results = pickle.load(f)
    
    # Si es un VARResults, generar una simulación de ejemplo
    if hasattr(var_results, 'names'):
        from quant.var_model import simulate_var_shock
        # Crear shocks de ejemplo usando las 4 variables actuales
        shocks = {}
        for var in var_results.names:
            if var == 'gdp':
                shocks[var] = {"magnitude": -0.1}  # Shock negativo al PIB
            elif var == 'inflation':
                shocks[var] = {"magnitude": 0.2}   # Shock positivo a inflación
            elif var == 'policy_rate':
                shocks[var] = {"magnitude": 0.05}  # Shock positivo a tipo de interés
            elif var == 'real_rate':
                shocks[var] = {"magnitude": 0.03}  # Shock positivo a tipo real
        
        sim_df = simulate_var_shock(var_results, shocks, steps=12)
    else:
        sim_df = var_results  # Si ya es un DataFrame
    
    with open(shock_path, "r") as f:
        scenario_dict = json.load(f)
    return sim_df, scenario_dict


def validate_simulation_data(sim_df: pd.DataFrame) -> bool:
    """Valida que los datos de simulación sean significativos."""
    print("🔍 Validando datos de simulación...")
    
    # Verificar que no sea todo ceros
    if (sim_df == 0).all().all():
        print("❌ ERROR: Todos los valores de simulación son cero")
        return False
    
    # Verificar que no haya demasiados ceros
    zero_count = (sim_df == 0).sum().sum()
    total_values = sim_df.size
    zero_percentage = (zero_count / total_values) * 100
    
    if zero_percentage > 50:
        print(f"⚠️  ADVERTENCIA: {zero_percentage:.1f}% de valores son cero")
        return False
    
    # Verificar que haya variación
    for col in sim_df.columns:
        col_std = sim_df[col].std()
        if col_std < 0.001:
            print(f"⚠️  ADVERTENCIA: Variable {col} tiene muy poca variación (std={col_std:.6f})")
    
    # Verificar rango de valores
    min_val = sim_df.min().min()
    max_val = sim_df.max().max()
    print(f"📊 Rango de valores: {min_val:.4f} a {max_val:.4f}")
    
    print("✅ Datos de simulación válidos")
    return True


def build_prompt(sim_df: pd.DataFrame, scenario_dict: dict) -> str:
    """Construye el prompt para GPT-4o a partir de la simulación y los shocks."""
    
    # Validar datos antes de construir prompt
    if not validate_simulation_data(sim_df):
        raise ValueError("Los datos de simulación no son válidos para generar narrativa")
    
    meta = (
        "You are a senior macroeconomic analyst.\n"
        "Based on the following simulated scenario, write a clear and coherent narrative.\n"
        f'The scenario is titled "{scenario_dict["scenario_name"]}", '
        f'created by {scenario_dict["author"]} on {scenario_dict["date_created"]}.'
    )

    shocks_lines = []
    for shock in scenario_dict["shocks"]:
        sign = "+" if shock["magnitude"] > 0 else "-"
        shocks_lines.append(
            f'- {shock["variable"].upper()}: {sign}{abs(shock["magnitude"])}pp '
            f'starting {shock["start_date"]} for {shock["duration_months"]} months '
            f'({shock["shock_type"]} shock)'
        )
    shocks_text = "The following economic shocks were applied:\n" + "\n".join(shocks_lines)

    # Mejorar la presentación de los datos de simulación
    evolution_text = (
        "The VAR model predicted the following monthly changes for all variables:\n"
        + sim_df.round(3).to_markdown()
    )

    # Prompt mejorado con contexto específico de las 4 variables
    instructions = """
Write an analytical report (max 350 words) that includes:
- What shocks were applied and when
- The effect on all 4 variables (GDP, Inflation, Policy Rate, Real Rate) over time
- Whether the effects were persistent or transitory
- A macroeconomic interpretation (e.g. recovery, recession, stagflation, overheating)
- Policy implications for central banks and governments
- A single-sentence key takeaway at the end

Focus on the interactions between variables and their economic significance.
Write it in fluent, technical English, using a tone similar to central bank reports.
""".strip()

    return f"{meta}\n\n{shocks_text}\n\n{evolution_text}\n\n{instructions}"


def generate_narrative(prompt: str, model: str = "gpt-4o",
                       temperature: float = 0.3, max_tokens: int = 800) -> str:
    """Envía el prompt a la API de OpenAI (nueva interfaz v1.0+) y devuelve la narrativa generada."""
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content.strip()


# ────────────────────────────────────────────────────────────────────────────────
# 3. Script principal
# ────────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Rutas de entrada / salida
    sim_path = "data/scenarios/var_run.pkl"
    shock_path = "input/shock.json"
    output_path = "output/summary.md"

    try:
        # 1️⃣ Cargar datos
        print("📊 Cargando datos de simulación...")
        sim_df, scenario = load_data(sim_path, shock_path)
        print(f"✅ Datos cargados: {sim_df.shape}")

        # 2️⃣ Construir prompt
        print("🔧 Construyendo prompt para GPT-4o...")
        prompt_text = build_prompt(sim_df, scenario)

        # 3️⃣ Generar narrativa con GPT-4o
        print("🤖 Generando narrativa con GPT-4o...")
        narrative_text = generate_narrative(prompt_text)

        # 4️⃣ Mostrar en consola
        print("\n--- NARRATIVE ---\n")
        print(narrative_text)

        # 5️⃣ Guardar en Markdown
        os.makedirs("output", exist_ok=True)
        with open(output_path, "w") as f:
            f.write(narrative_text)
        print(f"\n✅ Narrativa guardada en {output_path}")

    except ValueError as e:
        print(f"❌ Error de validación: {e}")
        print("💡 Sugerencia: Verifica que el modelo VAR esté entrenado correctamente")
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
