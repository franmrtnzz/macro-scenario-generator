# pruebas/test_var_model_pytest.py
import pytest
import pandas as pd
import numpy as np
import pickle
import os
import sys
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from quant.var_model import train_var_model, simulate_var_shock, simulate_var_shock_persistent


class TestVARModel:
    """Test suite for VAR model functionality."""
    
    @pytest.fixture
    def series_path(self):
        """Path to the series data file."""
        return "data/series.pkl"
    
    @pytest.fixture
    def var_results(self, series_path):
        """Trained VAR model results."""
        return train_var_model(series_path, lags=1)
    
    def test_data_file_exists(self, series_path):
        """Test that the data file exists and is readable."""
        assert os.path.exists(series_path), f"Data file {series_path} not found"
        
        with open(series_path, "rb") as f:
            data = pickle.load(f)
        
        assert isinstance(data, dict), "Data should be a dictionary"
        assert len(data) > 0, "Data should not be empty"
    
    def test_train_var_model_basic(self, series_path):
        """Test basic VAR model training."""
        results = train_var_model(series_path, lags=1)
        
        # Basic assertions
        assert results is not None, "Model should not be None"
        assert hasattr(results, 'names'), "Model should have variable names"
        assert hasattr(results, 'k_ar'), "Model should have lag information"
        assert hasattr(results, 'nobs'), "Model should have observation count"
        
        # Specific assertions
        assert len(results.names) >= 2, "Should have at least 2 variables"
        assert results.k_ar == 1, "Should have 1 lag"
        assert results.nobs > 100, "Should have sufficient observations"
        
        print(f"✅ Model trained with {len(results.names)} variables: {results.names}")
    
    def test_train_var_model_different_lags(self, series_path):
        """Test VAR model training with different lag specifications."""
        for lags in [1, 2, 3]:
            try:
                results = train_var_model(series_path, lags=lags)
                assert results.k_ar == lags, f"Should have {lags} lags"
                print(f"✅ VAR({lags}) trained successfully")
            except Exception as e:
                pytest.fail(f"VAR({lags}) failed: {e}")
    
    def test_simulate_var_shock_basic(self, var_results):
        """Test basic shock simulation."""
        # Create test shocks
        shocks = {
            'gdp': {'magnitude': -0.1},
            'inflation': {'magnitude': 0.2}
        }
        
        forecast = simulate_var_shock(var_results, shocks, steps=6)
        
        # Basic assertions
        assert isinstance(forecast, pd.DataFrame), "Should return DataFrame"
        assert forecast.shape[0] == 6, "Should have 6 rows (steps)"
        assert forecast.shape[1] == len(var_results.names), "Should have same columns as model"
        
        # Check for valid values
        assert not forecast.isna().any().any(), "Should not have NaN values"
        assert not (forecast == 0).all().all(), "Should not be all zeros"
        
        print(f"✅ Simulation successful: {forecast.shape}")
    
    def test_simulate_var_shock_different_magnitudes(self, var_results):
        """Test shock simulation with different magnitudes."""
        magnitudes = [-0.5, -0.1, 0.0, 0.1, 0.5]
        
        for mag in magnitudes:
            shocks = {var_results.names[0]: {'magnitude': mag}}
            forecast = simulate_var_shock(var_results, shocks, steps=3)
            
            assert not forecast.isna().any().any(), f"Magnitude {mag} should not produce NaN"
            assert not (forecast == 0).all().all(), f"Magnitude {mag} should not be all zeros"
        
        print(f"✅ All magnitudes tested successfully")
    
    def test_simulate_var_shock_invalid_variable(self, var_results):
        """Test that invalid variable names raise appropriate errors."""
        shocks = {'invalid_var': {'magnitude': 0.1}}
        
        with pytest.raises(ValueError, match="'invalid_var' no está en el VAR"):
            simulate_var_shock(var_results, shocks, steps=6)
        
        print("✅ Invalid variable error handled correctly")
    
    def test_model_persistence(self, var_results, tmp_path):
        """Test model save and load functionality."""
        # Save model
        model_path = tmp_path / "test_model.pkl"
        with open(model_path, "wb") as f:
            pickle.dump(var_results, f)
        
        # Load model
        with open(model_path, "rb") as f:
            loaded_results = pickle.load(f)
        
        # Verify model integrity
        assert loaded_results.names == var_results.names, "Variable names should match"
        assert loaded_results.k_ar == var_results.k_ar, "Lag count should match"
        assert loaded_results.nobs == var_results.nobs, "Observation count should match"
        
        print("✅ Model persistence test passed")
    
    def test_simulation_values_range(self, var_results):
        """Test that simulation values are within reasonable range."""
        shocks = {var_results.names[0]: {'magnitude': 0.1}}
        forecast = simulate_var_shock(var_results, shocks, steps=12)
        
        # Check value ranges (should not be extreme)
        for col in forecast.columns:
            col_min = forecast[col].min()
            col_max = forecast[col].max()
            
            # Values should not be extremely large or small
            assert abs(col_min) < 100, f"Column {col} has extreme min value: {col_min}"
            assert abs(col_max) < 100, f"Column {col} has extreme max value: {col_max}"
            
            # Values should have some variation
            assert col_max - col_min > 0.001, f"Column {col} has no variation"
        
        print("✅ Simulation values are within reasonable range")
    
    def test_multiple_variable_shocks(self, var_results):
        """Test simulation with multiple variable shocks."""
        # Create shocks for all variables
        shocks = {}
        for var in var_results.names:
            shocks[var] = {'magnitude': 0.1}
        
        forecast = simulate_var_shock(var_results, shocks, steps=6)
        
        # All variables should be affected
        for col in forecast.columns:
            assert not (forecast[col] == 0).all(), f"Variable {col} should show some change"
        
        print("✅ Multiple variable shocks work correctly")
    
    def test_data_quality_checks(self, series_path):
        """Test that the model handles data quality issues gracefully."""
        # This test verifies that the model can handle the current data
        # without throwing errors due to constant variables or collinearity
        
        try:
            results = train_var_model(series_path, lags=1)
            assert results is not None, "Model should train successfully"
            print("✅ Data quality issues handled gracefully")
        except Exception as e:
            pytest.fail(f"Model failed to handle data quality issues: {e}")

    def test_simulate_var_shock_persistent_basic(self, var_results):
        """Test básico de shock persistente (sin decaimiento)."""
        shocks = {var_results.names[0]: {'magnitude': 0.5}}
        forecast = simulate_var_shock_persistent(var_results, shocks, steps=6, shock_duration=3, shock_decay=1.0)
        assert isinstance(forecast, pd.DataFrame)
        assert forecast.shape[0] == 6
        assert forecast.shape[1] == len(var_results.names)
        assert not forecast.isna().any().any()
        assert not (forecast == 0).all().all()
        print("✅ Shock persistente básico funciona")

    def test_simulate_var_shock_persistent_decay(self, var_results):
        """Test de shock persistente con decaimiento."""
        shocks = {var_results.names[0]: {'magnitude': 1.0}}
        forecast = simulate_var_shock_persistent(var_results, shocks, steps=6, shock_duration=4, shock_decay=0.5)
        # El primer valor debe ser mayor que el cuarto (por decaimiento)
        col = var_results.names[0]
        assert forecast[col].iloc[0] > forecast[col].iloc[3]
        print("✅ Shock persistente con decaimiento funciona")

    def test_simulate_var_shock_persistent_vs_instant(self, var_results):
        """Comparar persistente vs instantáneo: persistente debe tener efecto acumulado mayor."""
        shocks = {var_results.names[0]: {'magnitude': 0.2}}
        forecast_instant = simulate_var_shock(var_results, shocks, steps=6)
        forecast_persistent = simulate_var_shock_persistent(var_results, shocks, steps=6, shock_duration=3, shock_decay=1.0)
        col = var_results.names[0]
        # El valor final del persistente debe ser mayor (o igual)
        assert forecast_persistent[col].iloc[-1] >= forecast_instant[col].iloc[-1]
        print("✅ Persistente vs instantáneo: efecto acumulado correcto")

    def test_simulate_var_shock_persistent_invalid_var(self, var_results):
        """Test de error con variable inválida en persistente."""
        shocks = {'invalid_var': {'magnitude': 1.0}}
        with pytest.raises(ValueError, match="'invalid_var' no está en el VAR"):
            simulate_var_shock_persistent(var_results, shocks, steps=6, shock_duration=2)
        print("✅ Error de variable inválida en persistente manejado correctamente")


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v"]) 