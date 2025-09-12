"""
Edge case and stress tests for calc.py functions
"""

import pytest
import pandas as pd
import numpy as np

from src.python.utils.calc import (
    payment_df_to_cohort_df,
    apply_predictions_to_cohort_df,
    get_cvf_cashflows_df,
)


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_very_large_amounts(self):
        """Test with very large payment amounts"""
        large_df = pd.DataFrame(
            {
                "customer_id": ["cust1"],
                "payment_date": ["2024-01-15"],
                "amount": [1e9],  # 1 billion
            }
        )

        result = payment_df_to_cohort_df(large_df)
        assert result.iloc[0, 0] == 1e9

    def test_very_small_amounts(self):
        """Test with very small payment amounts"""
        small_df = pd.DataFrame(
            {
                "customer_id": ["cust1"],
                "payment_date": ["2024-01-15"],
                "amount": [1e-6],  # 0.000001
            }
        )

        result = payment_df_to_cohort_df(small_df)
        assert result.iloc[0, 0] == 1e-6

    def test_zero_amounts(self):
        """Test with zero payment amounts"""
        zero_df = pd.DataFrame(
            {"customer_id": ["cust1", "cust2"], "payment_date": ["2024-01-15", "2024-01-16"], "amount": [0.0, 100.0]}
        )

        result = payment_df_to_cohort_df(zero_df)
        assert result.iloc[0, 0] == 100.0  # Should include zero amounts

    def test_negative_amounts(self):
        """Test with negative payment amounts (refunds)"""
        negative_df = pd.DataFrame(
            {
                "customer_id": ["cust1", "cust1"],
                "payment_date": ["2024-01-15", "2024-01-16"],
                "amount": [100.0, -20.0],  # Payment then refund
            }
        )

        result = payment_df_to_cohort_df(negative_df)
        assert result.iloc[0, 0] == 80.0  # Net amount

    def test_far_future_dates(self):
        """Test with dates far in the future"""
        future_df = pd.DataFrame({"customer_id": ["cust1"], "payment_date": ["2099-12-31"], "amount": [100.0]})

        result = payment_df_to_cohort_df(future_df)
        assert len(result) == 1

    def test_far_past_dates(self):
        """Test with dates far in the past"""
        past_df = pd.DataFrame({"customer_id": ["cust1"], "payment_date": ["1900-01-01"], "amount": [100.0]})

        result = payment_df_to_cohort_df(past_df)
        assert len(result) == 1

    def test_many_customers_single_cohort(self):
        """Test with many customers in single cohort"""
        n_customers = 1000
        data = {
            "customer_id": [f"cust{i}" for i in range(n_customers)],
            "payment_date": ["2024-01-15"] * n_customers,
            "amount": [100.0] * n_customers,
        }

        large_df = pd.DataFrame(data)
        result = payment_df_to_cohort_df(large_df)

        assert len(result) == 1  # Single cohort
        assert result.iloc[0, 0] == 100000.0  # 1000 * 100

    def test_many_cohorts(self):
        """Test with many different cohorts"""
        n_cohorts = 120  # 10 years of monthly cohorts
        dates = pd.date_range("2014-01-01", periods=n_cohorts, freq="MS")

        data = {
            "customer_id": [f"cust{i}" for i in range(n_cohorts)],
            "payment_date": dates.strftime("%Y-%m-%d").tolist(),
            "amount": [100.0] * n_cohorts,
        }

        large_df = pd.DataFrame(data)
        result = payment_df_to_cohort_df(large_df)

        assert len(result) == n_cohorts

    def test_extreme_churn_rates(self):
        """Test predictions with extreme churn rates"""
        cohort_matrix = pd.DataFrame({0: [100.0]}, index=pd.to_datetime(["2024-01-01"]))

        spend_df = pd.DataFrame({"cohort": ["2024-01-01"], "spend": [1000.0]})

        # Test with 99.9% churn (almost complete churn)
        extreme_predictions = {"2024-01-01": {"m0": 0.1, "churn": 0.999}}

        result = apply_predictions_to_cohort_df(
            predictions_dict=extreme_predictions, spend_df=spend_df, cohort_df=cohort_matrix, horizon_months=12
        )

        jan_cohort = pd.to_datetime("2024-01-01")
        # By period 5, should be nearly zero
        assert result.loc[jan_cohort, 5] < 1.0

    def test_zero_churn_rate(self):
        """Test predictions with zero churn (no decay)"""
        cohort_matrix = pd.DataFrame({0: [100.0]}, index=pd.to_datetime(["2024-01-01"]))

        spend_df = pd.DataFrame({"cohort": ["2024-01-01"], "spend": [1000.0]})

        # Test with 0% churn (no decay)
        no_churn_predictions = {"2024-01-01": {"m0": 0.1, "churn": 0.0}}

        result = apply_predictions_to_cohort_df(
            predictions_dict=no_churn_predictions, spend_df=spend_df, cohort_df=cohort_matrix, horizon_months=6
        )

        jan_cohort = pd.to_datetime("2024-01-01")
        # All periods should have same value (no decay)
        for period in range(1, 6):
            assert result.loc[jan_cohort, period] == 100.0

    def test_extreme_cash_caps(self):
        """Test cashflows with extreme cash caps"""
        cohort_matrix = pd.DataFrame({0: [1000.0], 1: [1000.0]}, index=pd.to_datetime(["2024-01-01"]))

        spend_df = pd.DataFrame({"cohort": ["2024-01-01"], "spend": [1000.0]})

        # Very low cap
        low_cap_trade = [
            {
                "cohort_start_at": "2024-01-01",
                "sharing_percentage": 1.0,  # 100% sharing
                "cash_cap": 1.0,  # Very low cap
            }
        ]

        result = get_cvf_cashflows_df(
            predicted_cohort_df=cohort_matrix, spend_df=spend_df, thresholds=[], trades=low_cap_trade
        )

        jan_cohort = pd.to_datetime("2024-01-01")
        total_collected = result.loc[jan_cohort].sum()
        assert total_collected <= 1.0  # Should respect cap

    def test_nan_values_in_input(self):
        """Test handling of NaN values in input data"""
        nan_df = pd.DataFrame(
            {
                "customer_id": ["cust1", "cust2", "cust3"],
                "payment_date": ["2024-01-15", "2024-01-16", "2024-01-17"],
                "amount": [100.0, np.nan, 50.0],
            }
        )

        # Should handle NaN gracefully (pandas will drop NaN by default in groupby.sum())
        result = payment_df_to_cohort_df(nan_df)
        assert len(result) == 1
        # Sum should be 150.0 (100 + 50, NaN ignored)
        assert result.iloc[0, 0] == 150.0

    def test_duplicate_customer_ids_same_date(self):
        """Test duplicate customer payments on same date"""
        duplicate_df = pd.DataFrame(
            {
                "customer_id": ["cust1", "cust1", "cust1"],
                "payment_date": ["2024-01-15", "2024-01-15", "2024-01-15"],
                "amount": [100.0, 50.0, 25.0],
            }
        )

        result = payment_df_to_cohort_df(duplicate_df)
        # Should sum all payments
        assert result.iloc[0, 0] == 175.0

    def test_invalid_date_formats(self):
        """Test various date formats that should be handled"""
        mixed_dates_df = pd.DataFrame(
            {
                "customer_id": ["cust1", "cust2", "cust3"],
                "payment_date": [
                    "2024-01-15",  # YYYY-MM-DD
                    "01/15/2024",  # MM/DD/YYYY
                    "2024-01-15 10:30:00",  # With time
                ],
                "amount": [100.0, 100.0, 100.0],
            }
        )

        # pandas.to_datetime should handle these formats
        result = payment_df_to_cohort_df(mixed_dates_df)
        assert len(result) == 1  # All should be in same cohort (January 2024)


class TestPerformanceConsiderations:
    """Test performance characteristics and memory usage"""

    def test_memory_efficiency_large_dataset(self):
        """Test memory efficiency with large dataset"""
        # Create a reasonably large dataset
        n_customers = 10000
        n_payments_per_customer = 12

        customers = []
        dates = []
        amounts = []

        base_date = pd.Timestamp("2024-01-01")

        for i in range(n_customers):
            for j in range(n_payments_per_customer):
                customers.append(f"cust{i}")
                # Spread payments over 12 months
                payment_date = base_date + pd.DateOffset(months=j)
                dates.append(payment_date)
                amounts.append(100.0)

        large_df = pd.DataFrame({"customer_id": customers, "payment_date": dates, "amount": amounts})

        # Should complete without memory issues
        result = payment_df_to_cohort_df(large_df)
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0

    @pytest.mark.slow
    def test_computation_time_scaling(self):
        """Test that computation scales reasonably with data size"""
        import time

        sizes = [100, 1000, 5000]
        times = []

        for size in sizes:
            df = pd.DataFrame(
                {
                    "customer_id": [f"cust{i}" for i in range(size)],
                    "payment_date": ["2024-01-15"] * size,
                    "amount": [100.0] * size,
                }
            )

            start_time = time.time()
            result = payment_df_to_cohort_df(df)
            end_time = time.time()

            times.append(end_time - start_time)
            assert isinstance(result, pd.DataFrame)

        # Should not have exponential growth (rough check)
        # Time for 5000 should not be more than 100x time for 100
        if times[0] > 0:  # Avoid division by zero
            assert times[2] / times[0] < 100

    def test_data_type_optimization(self):
        """Test that appropriate data types are used for memory efficiency"""
        df = pd.DataFrame(
            {"customer_id": ["cust1"] * 1000, "payment_date": ["2024-01-15"] * 1000, "amount": [100.0] * 1000}
        )

        result = payment_df_to_cohort_df(df)

        # Check that numeric columns use appropriate types
        assert pd.api.types.is_numeric_dtype(result.dtypes[0])
        assert pd.api.types.is_datetime64_any_dtype(result.index)
