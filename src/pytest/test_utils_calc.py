"""
Comprehensive unit tests for calc.py functions
"""

import pytest
import pandas as pd
import numpy as np
from datetime import date

from src.python.utils.calc import (
    payment_df_to_cohort_df,
    apply_predictions_to_cohort_df,
    apply_threshold_to_cohort_df,
    get_cvf_cashflows_df,
    calculate_ltv_cac_metrics,
    calculate_current_month_owed,
)


@pytest.mark.unit
class TestPaymentDfToCohortDf:
    """Tests for payment_df_to_cohort_df function"""

    def test_basic_conversion(self, sample_payment_data):
        """Test basic payment to cohort matrix conversion"""
        result = payment_df_to_cohort_df(sample_payment_data)

        # Check structure
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2  # 2 cohorts (Jan, Feb)
        assert 0 in result.columns  # period 0 should exist
        assert 1 in result.columns  # period 1 should exist

        # Check values - cust1 starts in Jan, cust2 starts in Jan, cust3 starts in Feb
        jan_cohort = pd.to_datetime("2024-01-01")
        feb_cohort = pd.to_datetime("2024-02-01")

        # Jan cohort should have cust1 + cust2 payments in period 0
        assert result.loc[jan_cohort, 0] == 250.0  # 100 + 150

        # Feb cohort should have cust3 payment in period 0
        assert result.loc[feb_cohort, 0] == 200.0

    def test_empty_dataframe(self):
        """Test with empty DataFrame"""
        empty_df = pd.DataFrame({"customer_id": [], "payment_date": [], "amount": []})
        result = payment_df_to_cohort_df(empty_df)

        assert isinstance(result, pd.DataFrame)
        assert len(result) == 0

    def test_single_customer(self, single_customer_data):
        """Test with single customer"""
        result = payment_df_to_cohort_df(single_customer_data)

        assert len(result) == 1  # 1 cohort
        assert result.iloc[0, 0] == 100.0  # period 0
        assert result.iloc[0, 1] == 50.0  # period 1

    def test_date_string_conversion(self):
        """Test with string dates (should convert automatically)"""
        df = pd.DataFrame(
            {
                "customer_id": ["cust1"],
                "payment_date": ["2024-01-15"],  # string date
                "amount": [100.0],
            }
        )

        result = payment_df_to_cohort_df(df)
        assert len(result) == 1
        assert result.iloc[0, 0] == 100.0

    def test_multiple_payments_same_period(self):
        """Test customers with multiple payments in same period"""
        df = pd.DataFrame(
            {
                "customer_id": ["cust1", "cust1"],
                "payment_date": ["2024-01-15", "2024-01-25"],  # Same month
                "amount": [100.0, 50.0],
            }
        )

        result = payment_df_to_cohort_df(df)
        assert result.iloc[0, 0] == 150.0  # Should sum both payments


@pytest.mark.unit
class TestApplyPredictionsToCohortDf:
    """Tests for apply_predictions_to_cohort_df function"""

    def test_basic_predictions(self, sample_cohort_matrix, sample_spend_data, sample_predictions):
        """Test basic prediction application"""
        result = apply_predictions_to_cohort_df(
            predictions_dict=sample_predictions,
            spend_df=sample_spend_data,
            cohort_df=sample_cohort_matrix,
            horizon_months=6,
        )

        # Check structure
        assert isinstance(result, pd.DataFrame)
        assert len(result.columns) == 6  # horizon_months
        assert len(result) == 2  # 2 cohorts

        # Check that actual values are preserved
        jan_cohort = pd.to_datetime("2024-01-01")
        assert result.loc[jan_cohort, 0] == 100.0  # Original actual value
        assert result.loc[jan_cohort, 1] == 80.0  # Original actual value

    def test_m0_prediction_for_missing_period_zero(self, sample_spend_data, sample_predictions):
        """Test m0 prediction when period 0 has no actual data"""
        # Create cohort matrix with no period 0 data
        cohort_matrix = pd.DataFrame({1: [80.0], 2: [60.0]}, index=pd.to_datetime(["2024-01-01"]))

        result = apply_predictions_to_cohort_df(
            predictions_dict=sample_predictions, spend_df=sample_spend_data, cohort_df=cohort_matrix, horizon_months=4
        )

        jan_cohort = pd.to_datetime("2024-01-01")
        # Should apply m0 prediction: 0.12 * 1000 = 120
        assert result.loc[jan_cohort, 0] == 120.0

    def test_decay_predictions(self, sample_cohort_matrix, sample_spend_data, sample_predictions):
        """Test geometric decay predictions"""
        result = apply_predictions_to_cohort_df(
            predictions_dict=sample_predictions,
            spend_df=sample_spend_data,
            cohort_df=sample_cohort_matrix,
            horizon_months=6,
        )

        jan_cohort = pd.to_datetime("2024-01-01")
        # Period 3 should be predicted using decay from period 2
        # 60.0 * (1 - 0.25)^1 = 60.0 * 0.75 = 45.0
        assert result.loc[jan_cohort, 3] == 45.0

    def test_no_predictions_for_cohort(self, sample_cohort_matrix, sample_spend_data):
        """Test when no predictions exist for a cohort"""
        empty_predictions = {}

        result = apply_predictions_to_cohort_df(
            predictions_dict=empty_predictions,
            spend_df=sample_spend_data,
            cohort_df=sample_cohort_matrix,
            horizon_months=4,
        )

        # Should return original data with extended columns filled with zeros
        jan_cohort = pd.to_datetime("2024-01-01")
        assert result.loc[jan_cohort, 0] == 100.0  # Original value
        assert result.loc[jan_cohort, 3] == 0.0  # No prediction

    def test_scenario_filtering(self, sample_cohort_matrix, sample_spend_data):
        """Test scenario-based prediction filtering"""
        predictions_with_scenarios = {
            "2024-01-01": {"m0": 0.12, "churn": 0.25, "scenario": "optimistic"},
            "2024-02-01": {"m0": 0.15, "churn": 0.20, "scenario": "conservative"},
        }

        result = apply_predictions_to_cohort_df(
            predictions_dict=predictions_with_scenarios,
            spend_df=sample_spend_data,
            cohort_df=sample_cohort_matrix,
            horizon_months=4,
            scenario="optimistic",
        )

        # Only Jan cohort should get predictions (optimistic scenario)
        jan_cohort = pd.to_datetime("2024-01-01")
        feb_cohort = pd.to_datetime("2024-02-01")

        # Jan should have decay prediction
        assert result.loc[jan_cohort, 3] == 45.0  # 60 * 0.75
        # Feb should remain as original (no matching scenario)
        assert result.loc[feb_cohort, 3] == 0.0


@pytest.mark.unit
class TestApplyThresholdToCohortDf:
    """Tests for apply_threshold_to_cohort_df function"""

    def test_basic_threshold_application(self, sample_cohort_matrix, sample_spend_data, sample_thresholds):
        """Test basic threshold failure detection"""
        result = apply_threshold_to_cohort_df(
            cohort_df=sample_cohort_matrix, spend_df=sample_spend_data, thresholds=sample_thresholds
        )

        # Check structure
        assert isinstance(result, pd.DataFrame)
        assert result.shape == sample_cohort_matrix.shape
        assert result.dtype == bool

    def test_threshold_failure_detection(self, sample_spend_data, sample_thresholds):
        """Test specific threshold failure scenarios"""
        # Create cohort matrix with known failure
        cohort_matrix = pd.DataFrame(
            {0: [50.0], 1: [30.0]},  # 50/1000=5% < 10% (fail), 30/1000=3% < 8% (fail)
            index=pd.to_datetime(["2024-01-01"]),
        )

        result = apply_threshold_to_cohort_df(
            cohort_df=cohort_matrix, spend_df=sample_spend_data, thresholds=sample_thresholds
        )

        jan_cohort = pd.to_datetime("2024-01-01")
        assert result.loc[jan_cohort, 0] == True  # Should fail (5% < 10%)
        assert result.loc[jan_cohort, 1] == True  # Should fail (3% < 8%)

    def test_threshold_pass(self, sample_spend_data, sample_thresholds):
        """Test threshold pass scenarios"""
        # Create cohort matrix that passes thresholds
        cohort_matrix = pd.DataFrame(
            {0: [150.0], 1: [100.0]},  # 150/1000=15% > 10% (pass), 100/1000=10% > 8% (pass)
            index=pd.to_datetime(["2024-01-01"]),
        )

        result = apply_threshold_to_cohort_df(
            cohort_df=cohort_matrix, spend_df=sample_spend_data, thresholds=sample_thresholds
        )

        jan_cohort = pd.to_datetime("2024-01-01")
        assert result.loc[jan_cohort, 0] == False  # Should pass
        assert result.loc[jan_cohort, 1] == False  # Should pass

    def test_no_thresholds(self, sample_cohort_matrix, sample_spend_data):
        """Test with empty thresholds list"""
        result = apply_threshold_to_cohort_df(cohort_df=sample_cohort_matrix, spend_df=sample_spend_data, thresholds=[])

        # All should be False (no failures) when no thresholds
        assert not result.any().any()

    def test_missing_period_in_thresholds(self, sample_cohort_matrix, sample_spend_data):
        """Test when threshold doesn't exist for a period"""
        thresholds = [{"payment_period_month": 5, "minimum_payment_percent": 0.10}]

        result = apply_threshold_to_cohort_df(
            cohort_df=sample_cohort_matrix, spend_df=sample_spend_data, thresholds=thresholds
        )

        # Periods 0,1,2 should all be False (no thresholds)
        assert not result[[0, 1, 2]].any().any()

    def test_zero_spend_handling(self, sample_cohort_matrix):
        """Test handling of zero spend (division by zero)"""
        zero_spend_df = pd.DataFrame({"cohort": ["2024-01-01"], "spend": [0.0]})

        thresholds = [{"payment_period_month": 0, "minimum_payment_percent": 0.10}]

        result = apply_threshold_to_cohort_df(
            cohort_df=sample_cohort_matrix, spend_df=zero_spend_df, thresholds=thresholds
        )

        # Should handle gracefully (no division by zero error)
        assert isinstance(result, pd.DataFrame)


@pytest.mark.unit
class TestGetCvfCashflowsDf:
    """Tests for get_cvf_cashflows_df function"""

    def test_basic_cashflow_calculation(
        self, sample_cohort_matrix, sample_spend_data, sample_thresholds, sample_trades
    ):
        """Test basic CVF cashflow calculation"""
        result = get_cvf_cashflows_df(
            predicted_cohort_df=sample_cohort_matrix,
            spend_df=sample_spend_data,
            thresholds=sample_thresholds,
            trades=sample_trades,
        )

        # Check structure
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 2  # 2 cohorts from trades

        # Check that collections are calculated
        jan_cohort = pd.to_datetime("2024-01-01")
        # Jan cohort: 100 * 0.5 = 50 (base sharing rate)
        assert result.loc[jan_cohort, 0] == 50.0

    def test_threshold_failure_full_sharing(self, sample_spend_data, sample_trades):
        """Test 100% sharing when threshold fails"""
        # Create matrix that fails threshold (5% < 10%)
        failing_matrix = pd.DataFrame({0: [50.0], 1: [30.0]}, index=pd.to_datetime(["2024-01-01"]))

        thresholds = [{"payment_period_month": 0, "minimum_payment_percent": 0.10}]

        result = get_cvf_cashflows_df(
            predicted_cohort_df=failing_matrix, spend_df=sample_spend_data, thresholds=thresholds, trades=sample_trades
        )

        jan_cohort = pd.to_datetime("2024-01-01")
        # Should apply 100% sharing due to threshold failure: 50 * 1.0 = 50
        assert result.loc[jan_cohort, 0] == 50.0

    def test_cash_cap_limit(self, sample_spend_data, sample_thresholds):
        """Test cash cap limiting collections"""
        # Create high payment matrix
        high_payment_matrix = pd.DataFrame(
            {0: [1000.0], 1: [1000.0], 2: [1000.0]}, index=pd.to_datetime(["2024-01-01"])
        )

        # Low cash cap trade
        low_cap_trade = [
            {
                "cohort_start_at": "2024-01-01",
                "sharing_percentage": 0.5,
                "cash_cap": 100.0,  # Low cap
            }
        ]

        result = get_cvf_cashflows_df(
            predicted_cohort_df=high_payment_matrix,
            spend_df=sample_spend_data,
            thresholds=sample_thresholds,
            trades=low_cap_trade,
        )

        jan_cohort = pd.to_datetime("2024-01-01")
        # Total collections should not exceed cap
        total_collections = result.loc[jan_cohort].sum()
        assert total_collections <= 100.0

    def test_missing_cohort_in_matrix(self, sample_cohort_matrix, sample_spend_data, sample_thresholds):
        """Test trade for cohort not in payment matrix"""
        trades_with_missing = [
            {
                "cohort_start_at": "2024-03-01",  # Not in sample_cohort_matrix
                "sharing_percentage": 0.5,
                "cash_cap": 500.0,
            }
        ]

        result = get_cvf_cashflows_df(
            predicted_cohort_df=sample_cohort_matrix,
            spend_df=sample_spend_data,
            thresholds=sample_thresholds,
            trades=trades_with_missing,
        )

        # Should handle gracefully and add empty row
        mar_cohort = pd.to_datetime("2024-03-01")
        assert mar_cohort in result.index
        assert result.loc[mar_cohort].sum() == 0.0

    def test_multiple_trades_same_cohort(self, sample_cohort_matrix, sample_spend_data, sample_thresholds):
        """Test multiple trades for same cohort (should sum)"""
        multiple_trades = [
            {"cohort_start_at": "2024-01-01", "sharing_percentage": 0.3, "cash_cap": 1000.0},
            {"cohort_start_at": "2024-01-01", "sharing_percentage": 0.2, "cash_cap": 1000.0},
        ]

        result = get_cvf_cashflows_df(
            predicted_cohort_df=sample_cohort_matrix,
            spend_df=sample_spend_data,
            thresholds=sample_thresholds,
            trades=multiple_trades,
        )

        jan_cohort = pd.to_datetime("2024-01-01")
        # Should sum both trades: 100*(0.3+0.2) = 50
        assert result.loc[jan_cohort, 0] == 50.0

    def test_empty_trades(self, sample_cohort_matrix, sample_spend_data, sample_thresholds):
        """Test with empty trades list"""
        result = get_cvf_cashflows_df(
            predicted_cohort_df=sample_cohort_matrix,
            spend_df=sample_spend_data,
            thresholds=sample_thresholds,
            trades=[],
        )

        # Should return empty result
        assert len(result) == 0


@pytest.mark.unit
class TestCalculateLtvCacMetrics:
    """Tests for calculate_ltv_cac_metrics function"""

    def test_basic_metrics_calculation(self, sample_cohort_matrix, sample_spend_data):
        """Test basic LTV/CAC metrics calculation"""
        result = calculate_ltv_cac_metrics(cohort_df=sample_cohort_matrix, spend_df=sample_spend_data)

        # Check all expected keys
        expected_keys = ["ltv_estimate", "cac_estimate", "moic_to_date", "total_payments", "total_spend"]
        assert all(key in result for key in expected_keys)

        # Check calculations
        assert result["total_spend"] == 1800.0  # 1000 + 800
        assert result["total_payments"] == 560.0  # Sum of all payments in matrix
        assert result["moic_to_date"] == pytest.approx(460.0 / 1800.0)
        assert result["ltv_estimate"] == pytest.approx(460.0 / 2)  # total_payments / num_cohorts
        assert result["cac_estimate"] == pytest.approx(1800.0 / 2)  # total_spend / num_cohorts

    def test_zero_spend(self):
        """Test metrics with zero spend"""
        cohort_df = pd.DataFrame({0: [100.0]}, index=pd.to_datetime(["2024-01-01"]))
        spend_df = pd.DataFrame({"cohort": ["2024-01-01"], "spend": [0.0]})

        result = calculate_ltv_cac_metrics(cohort_df, spend_df)

        assert result["moic_to_date"] == 0.0  # Avoid division by zero
        assert result["cac_estimate"] == 0.0

    def test_empty_dataframes(self):
        """Test with empty dataframes"""
        empty_cohort = pd.DataFrame()
        empty_spend = pd.DataFrame({"spend": []})

        result = calculate_ltv_cac_metrics(empty_cohort, empty_spend)

        assert result["ltv_estimate"] == 0.0
        assert result["cac_estimate"] == 0.0
        assert result["moic_to_date"] == 0.0

    def test_missing_spend_column(self, sample_cohort_matrix):
        """Test with spend DataFrame missing 'spend' column"""
        bad_spend_df = pd.DataFrame({"not_spend": [1000.0]})

        result = calculate_ltv_cac_metrics(sample_cohort_matrix, bad_spend_df)

        assert result["total_spend"] == 0.0
        assert result["cac_estimate"] == 0.0


@pytest.mark.unit
class TestCalculateCurrentMonthOwed:
    """Tests for calculate_current_month_owed function"""

    def test_basic_current_month_calculation(self):
        """Test basic current month owed calculation"""
        cashflows_df = pd.DataFrame(
            {0: [50.0, 40.0], 1: [30.0, 25.0], 2: [20.0, 15.0]}, index=pd.to_datetime(["2024-01-01", "2024-02-01"])
        )

        result = calculate_current_month_owed(cashflows_df=cashflows_df, as_of_month=date(2024, 3, 1))

        # Should return sum of latest period (period 2): 20 + 15 = 35
        assert result == 35.0

    def test_empty_cashflows(self):
        """Test with empty cashflows DataFrame"""
        empty_df = pd.DataFrame()

        result = calculate_current_month_owed(cashflows_df=empty_df, as_of_month=date(2024, 3, 1))

        assert result == 0.0

    def test_single_period(self):
        """Test with single period cashflows"""
        single_period_df = pd.DataFrame({0: [100.0, 200.0]}, index=pd.to_datetime(["2024-01-01", "2024-02-01"]))

        result = calculate_current_month_owed(single_period_df, as_of_month=date(2024, 1, 1))

        assert result == 300.0  # 100 + 200


@pytest.mark.unit
class TestIntegrationScenarios:
    """Integration tests combining multiple functions"""

    def test_full_pipeline(
        self, sample_payment_data, sample_spend_data, sample_predictions, sample_thresholds, sample_trades
    ):
        """Test full calculation pipeline"""
        # Step 1: Convert payments to cohort matrix
        cohort_matrix = payment_df_to_cohort_df(sample_payment_data)

        # Step 2: Apply predictions
        predicted_matrix = apply_predictions_to_cohort_df(
            predictions_dict=sample_predictions, spend_df=sample_spend_data, cohort_df=cohort_matrix, horizon_months=6
        )

        # Step 3: Calculate cashflows
        cashflows = get_cvf_cashflows_df(
            predicted_cohort_df=predicted_matrix,
            spend_df=sample_spend_data,
            thresholds=sample_thresholds,
            trades=sample_trades,
        )

        # Step 4: Calculate metrics
        metrics = calculate_ltv_cac_metrics(predicted_matrix, sample_spend_data)

        # Verify pipeline completes without errors
        assert isinstance(cohort_matrix, pd.DataFrame)
        assert isinstance(predicted_matrix, pd.DataFrame)
        assert isinstance(cashflows, pd.DataFrame)
        assert isinstance(metrics, dict)

        # Verify some basic properties
        assert len(cohort_matrix) >= 1
        assert len(predicted_matrix.columns) == 6  # horizon_months
        assert "moic_to_date" in metrics

    def test_edge_case_empty_input(self):
        """Test pipeline with empty inputs"""
        empty_payments = pd.DataFrame({"customer_id": [], "payment_date": [], "amount": []})
        empty_spend = pd.DataFrame({"cohort": [], "spend": []})

        # Should handle gracefully
        cohort_matrix = payment_df_to_cohort_df(empty_payments)
        metrics = calculate_ltv_cac_metrics(cohort_matrix, empty_spend)

        assert len(cohort_matrix) == 0
        assert metrics["total_payments"] == 0.0
        assert metrics["total_spend"] == 0.0

    def test_data_type_consistency(self, sample_payment_data, sample_spend_data):
        """Test that data types are preserved through pipeline"""
        cohort_matrix = payment_df_to_cohort_df(sample_payment_data)

        # Check that amounts are float
        assert cohort_matrix.dtypes.apply(lambda x: np.issubdtype(x, np.floating)).all()

        # Check that index is datetime
        assert pd.api.types.is_datetime64_any_dtype(cohort_matrix.index)
