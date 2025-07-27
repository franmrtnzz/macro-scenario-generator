# utils/export.py
"""
Módulo para exportar resultados de simulaciones VAR a diferentes formatos.
"""

import pandas as pd
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path


def export_simulation_to_csv(
    simulation_df: pd.DataFrame,
    scenario_name: str,
    output_dir: str = "output",
    include_metadata: bool = True
) -> str:
    """
    Exporta una simulación VAR a CSV con metadatos opcionales.
    
    Args:
        simulation_df: DataFrame con los resultados de la simulación
        scenario_name: Nombre del escenario simulado
        output_dir: Directorio de salida
        include_metadata: Si incluir metadatos en el archivo
    
    Returns:
        str: Ruta del archivo CSV generado
    """
    # Crear directorio de salida si no existe
    os.makedirs(output_dir, exist_ok=True)
    
    # Generar nombre de archivo con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{scenario_name}_{timestamp}.csv"
    filepath = os.path.join(output_dir, filename)
    
    # Exportar DataFrame principal
    simulation_df.to_csv(filepath, index=True, index_label='date')
    
    # Añadir metadatos si se solicita
    if include_metadata:
        metadata = {
            "scenario_name": scenario_name,
            "export_date": datetime.now().isoformat(),
            "variables": list(simulation_df.columns),
            "time_horizon": len(simulation_df),
            "data_points": simulation_df.size,
            "value_range": {
                "min": float(simulation_df.min().min()),
                "max": float(simulation_df.max().max())
            }
        }
        
        # Guardar metadatos en archivo JSON separado
        metadata_file = filepath.replace('.csv', '_metadata.json')
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    print(f"✅ Simulación exportada a: {filepath}")
    if include_metadata:
        print(f"📋 Metadatos guardados en: {metadata_file}")
    
    return filepath


def export_multiple_scenarios(
    scenarios_dict: Dict[str, pd.DataFrame],
    output_dir: str = "output"
) -> Dict[str, str]:
    """
    Exporta múltiples escenarios a archivos CSV separados.
    
    Args:
        scenarios_dict: Diccionario con nombre_escenario -> DataFrame
        output_dir: Directorio de salida
    
    Returns:
        Dict[str, str]: Mapeo de nombres de escenario a rutas de archivo
    """
    exported_files = {}
    
    for scenario_name, simulation_df in scenarios_dict.items():
        filepath = export_simulation_to_csv(
            simulation_df, 
            scenario_name, 
            output_dir
        )
        exported_files[scenario_name] = filepath
    
    return exported_files


def create_summary_report(
    scenarios_dict: Dict[str, pd.DataFrame],
    output_dir: str = "output"
) -> str:
    """
    Crea un reporte resumido de todos los escenarios simulados.
    
    Args:
        scenarios_dict: Diccionario con nombre_escenario -> DataFrame
        output_dir: Directorio de salida
    
    Returns:
        str: Ruta del archivo de reporte
    """
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = os.path.join(output_dir, f"scenarios_summary_{timestamp}.csv")
    
    # Crear DataFrame resumido
    summary_data = []
    
    for scenario_name, df in scenarios_dict.items():
        for variable in df.columns:
            summary_data.append({
                'scenario': scenario_name,
                'variable': variable,
                'initial_value': float(df[variable].iloc[0]),
                'final_value': float(df[variable].iloc[-1]),
                'total_change': float(df[variable].iloc[-1] - df[variable].iloc[0]),
                'max_value': float(df[variable].max()),
                'min_value': float(df[variable].min()),
                'volatility': float(df[variable].std())
            })
    
    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv(report_file, index=False)
    
    print(f"📊 Reporte resumido creado: {report_file}")
    return report_file


def export_complete_analysis(
    var_results,
    scenarios_dict: Dict[str, pd.DataFrame],
    narrative: Optional[str] = None,
    output_dir: str = "output"
) -> Dict[str, str]:
    """
    Exporta un análisis completo incluyendo modelo, simulaciones y narrativa.
    
    Args:
        var_results: Objeto VARResults del modelo entrenado
        scenarios_dict: Diccionario con simulaciones
        narrative: Narrativa generada (opcional)
        output_dir: Directorio de salida
    
    Returns:
        Dict[str, str]: Rutas de todos los archivos generados
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    analysis_dir = os.path.join(output_dir, f"analysis_{timestamp}")
    os.makedirs(analysis_dir, exist_ok=True)
    
    exported_files = {}
    
    # 1. Exportar simulaciones
    for scenario_name, df in scenarios_dict.items():
        filepath = export_simulation_to_csv(
            df, scenario_name, analysis_dir, include_metadata=True
        )
        exported_files[f"simulation_{scenario_name}"] = filepath
    
    # 2. Crear reporte resumido
    summary_file = create_summary_report(scenarios_dict, analysis_dir)
    exported_files["summary"] = summary_file
    
    # 3. Guardar narrativa si existe
    if narrative:
        narrative_file = os.path.join(analysis_dir, "narrative.md")
        with open(narrative_file, 'w', encoding='utf-8') as f:
            f.write(f"# Análisis Macroeconómico - {timestamp}\n\n")
            f.write(narrative)
        exported_files["narrative"] = narrative_file
        print(f"📝 Narrativa guardada: {narrative_file}")
    
    # 4. Guardar información del modelo
    model_info = {
        "model_type": "VAR",
        "variables": list(var_results.names),
        "lags": var_results.k_ar,
        "observations": var_results.nobs,
        "aic": float(var_results.aic),
        "bic": float(var_results.bic),
        "export_date": datetime.now().isoformat()
    }
    
    model_file = os.path.join(analysis_dir, "model_info.json")
    with open(model_file, 'w') as f:
        json.dump(model_info, f, indent=2)
    exported_files["model_info"] = model_file
    
    print(f"🎯 Análisis completo exportado a: {analysis_dir}")
    return exported_files 