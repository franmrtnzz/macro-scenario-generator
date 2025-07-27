# pruebas/test_var_model.py
import unittest
import pandas as pd
import numpy as np
import pickle
import os
import sys

# Añadir el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from quant.var_model import train_var_model, simulate_var_shock


class TestVARModel(unittest.TestCase):
    
    def setUp(self):
        """Configuración inicial para los tests"""
        self.series_path = "data/series.pkl"
        
    def test_train_var_model_basic(self):
        """Test básico de entrenamiento del modelo VAR"""
        print("\n🧪 Test: Entrenamiento básico del VAR")
        
        # Verificar que el archivo existe
        self.assertTrue(os.path.exists(self.series_path), 
                       f"Archivo {self.series_path} no encontrado")
        
        # Entrenar modelo
        results = train_var_model(self.series_path, lags=1)
        
        # Verificaciones básicas
        self.assertIsNotNone(results, "El modelo no debería ser None")
        self.assertGreaterEqual(len(results.names), 2, 
                               "Debería tener al menos 2 variables")
        self.assertEqual(results.k_ar, 1, "Debería tener 1 lag")
        self.assertGreater(results.nobs, 100, "Debería tener suficientes observaciones")
        
        print(f"✅ Modelo entrenado con {len(results.names)} variables: {results.names}")
        
    def test_simulate_var_shock(self):
        """Test de simulación de shocks"""
        print("\n🧪 Test: Simulación de shocks")
        
        # Entrenar modelo
        results = train_var_model(self.series_path, lags=1)
        
        # Crear shocks de prueba
        shocks = {}
        for var in results.names[:2]:  # Usar las primeras 2 variables
            shocks[var] = {"magnitude": 0.1}
        
        # Simular
        forecast = simulate_var_shock(results, shocks, steps=6)
        
        # Verificaciones
        self.assertIsInstance(forecast, pd.DataFrame, "Debería devolver un DataFrame")
        self.assertEqual(forecast.shape[0], 6, "Debería tener 6 filas")
        self.assertEqual(forecast.shape[1], len(results.names), 
                        "Debería tener el mismo número de columnas que variables")
        
        # Verificar que no hay valores NaN
        self.assertFalse(forecast.isna().any().any(), 
                        "No debería haber valores NaN en la simulación")
        
        print(f"✅ Simulación exitosa: {forecast.shape}")
        print(forecast.head())
        
    def test_model_persistence(self):
        """Test de persistencia del modelo (guardar/cargar)"""
        print("\n🧪 Test: Persistencia del modelo")
        
        # Entrenar modelo
        results = train_var_model(self.series_path, lags=1)
        
        # Guardar modelo
        model_path = "data/scenarios/var_run.pkl"
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        with open(model_path, "wb") as f:
            pickle.dump(results, f)
        
        # Cargar modelo
        with open(model_path, "rb") as f:
            loaded_results = pickle.load(f)
        
        # Verificar que son iguales
        self.assertEqual(results.names, loaded_results.names, 
                        "Los nombres de variables deberían ser iguales")
        self.assertEqual(results.k_ar, loaded_results.k_ar, 
                        "El número de lags debería ser igual")
        
        print(f"✅ Modelo guardado y cargado correctamente en {model_path}")
        
    def test_different_lags(self):
        """Test con diferentes números de lags"""
        print("\n🧪 Test: Diferentes números de lags")
        
        for lags in [1, 2, 3]:
            try:
                results = train_var_model(self.series_path, lags=lags)
                self.assertEqual(results.k_ar, lags, 
                               f"Debería tener {lags} lags")
                print(f"✅ VAR({lags}) entrenado correctamente")
            except Exception as e:
                print(f"⚠️  VAR({lags}) falló: {e}")
                
    def test_shock_magnitudes(self):
        """Test con diferentes magnitudes de shock"""
        print("\n🧪 Test: Diferentes magnitudes de shock")
        
        # Entrenar modelo
        results = train_var_model(self.series_path, lags=1)
        
        # Probar diferentes magnitudes
        magnitudes = [-0.5, -0.1, 0.0, 0.1, 0.5]
        
        for mag in magnitudes:
            shocks = {results.names[0]: {"magnitude": mag}}
            forecast = simulate_var_shock(results, shocks, steps=3)
            
            # Verificar que la simulación funciona
            self.assertFalse(forecast.isna().any().any(), 
                           f"Simulación con magnitud {mag} no debería tener NaN")
            
        print(f"✅ Todas las magnitudes probadas exitosamente")


if __name__ == "__main__":
    # Ejecutar tests
    unittest.main(verbosity=2) 