import pandas as pd
import pytest

from utils.transform import normalize_series


def test_normalize_series_preserves_raw_units_by_default():
    raw = pd.DataFrame(
        {
            "date": pd.to_datetime(["2025-01-15", "2025-02-15", "2025-03-15"]),
            "value": [2.0, 2.5, 3.0],
        }
    )

    result = normalize_series(raw, "inflation")

    assert list(result.columns) == ["date", "variable", "value"]
    assert result["variable"].unique().tolist() == ["inflation"]
    assert result["value"].iloc[-1] == 3.0


def test_minmax_rejects_constant_series():
    raw = pd.DataFrame(
        {
            "date": pd.to_datetime(["2025-01-01", "2025-02-01"]),
            "value": [1.0, 1.0],
        }
    )

    with pytest.raises(ValueError, match="constant"):
        normalize_series(raw, "constant", minmax=True)
