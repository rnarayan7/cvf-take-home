"""
Pytest configuration and fixtures for CVF tests
"""

import pytest
import pandas as pd
from typing import Dict, List, Any


@pytest.fixture
def sample_payment_data() -> pd.DataFrame:
    """Sample payment data for testing"""
    return pd.DataFrame(
        {
            "customer_id": ["cust1", "cust1", "cust1", "cust2", "cust2", "cust3"],
            "payment_date": ["2024-01-15", "2024-02-15", "2024-03-15", "2024-01-20", "2024-02-20", "2024-02-10"],
            "amount": [100.0, 80.0, 60.0, 150.0, 120.0, 200.0],
        }
    )


@pytest.fixture
def sample_spend_data() -> pd.DataFrame:
    """Sample spend data for testing"""
    return pd.DataFrame({"cohort": ["2024-01-01", "2024-02-01"], "spend": [1000.0, 800.0]})


@pytest.fixture
def sample_cohort_matrix() -> pd.DataFrame:
    """Sample cohort matrix for testing"""
    data = {
        0: [100.0, 200.0],  # period 0
        1: [80.0, 120.0],  # period 1
        2: [60.0, 0.0],  # period 2
    }
    index = pd.to_datetime(["2024-01-01", "2024-02-01"])
    return pd.DataFrame(data, index=index)


@pytest.fixture
def sample_predictions() -> Dict[str, Dict[str, float]]:
    """Sample prediction parameters for testing"""
    return {"2024-01-01": {"m0": 0.12, "churn": 0.25}, "2024-02-01": {"m0": 0.15, "churn": 0.20}}


@pytest.fixture
def sample_thresholds() -> List[Dict[str, float]]:
    """Sample threshold rules for testing"""
    return [
        {"payment_period_month": 0, "minimum_payment_percent": 0.10},
        {"payment_period_month": 1, "minimum_payment_percent": 0.08},
        {"payment_period_month": 2, "minimum_payment_percent": 0.06},
    ]


@pytest.fixture
def sample_trades() -> List[Dict[str, Any]]:
    """Sample trade definitions for testing"""
    return [
        {"cohort_start_at": "2024-01-01", "sharing_percentage": 0.5, "cash_cap": 500.0},
        {"cohort_start_at": "2024-02-01", "sharing_percentage": 0.4, "cash_cap": 400.0},
    ]


@pytest.fixture
def empty_dataframe() -> pd.DataFrame:
    """Empty DataFrame for edge case testing"""
    return pd.DataFrame()


@pytest.fixture
def single_customer_data() -> pd.DataFrame:
    """Single customer payment data for testing"""
    return pd.DataFrame(
        {"customer_id": ["cust1", "cust1"], "payment_date": ["2024-01-15", "2024-02-15"], "amount": [100.0, 50.0]}
    )
