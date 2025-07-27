# config/shock_rules.py

rules = {
    "interest_rate": {
        "equity": -2.0,
        "gdp": -1.0
    },
    "inflation": {
        "gdp": 1.5
    },
    "gdp": {
        "inflation": 0.5
    }
}
