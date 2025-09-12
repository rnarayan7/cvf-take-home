"""
CVF Data Pipeline Implementation
Based on the Jupyter notebook exercises
"""

import pandas as pd
import numpy as np
from typing import List, Dict
from datetime import date


def payment_df_to_cohort_df(payment_df: pd.DataFrame) -> pd.DataFrame:
    """
    Convert raw payments DataFrame to cohort matrix.

    Args:
        payment_df: DataFrame with columns ['customer_id', 'payment_date', 'amount']

    Returns:
        DataFrame with cohorts as index and payment periods as columns
    """
    df = payment_df.copy()

    # Ensure payment_date is datetime
    if not pd.api.types.is_datetime64_any_dtype(df["payment_date"]):
        df["payment_date"] = pd.to_datetime(df["payment_date"])

    # Calculate cohort month for each customer (first payment month)
    cohort_df = df.groupby("customer_id")["payment_date"].min().reset_index()
    cohort_df["cohort"] = cohort_df["payment_date"].dt.to_period("M").dt.to_timestamp()

    # Merge cohort info back to payments
    df = df.merge(cohort_df[["customer_id", "cohort"]], on="customer_id")

    # Round payments to nearest month
    df["payment_month"] = df["payment_date"].dt.to_period("M").dt.to_timestamp()

    # Calculate payment period (months since cohort)
    df["payment_period"] = (df["payment_month"].dt.year - df["cohort"].dt.year) * 12 + (
        df["payment_month"].dt.month - df["cohort"].dt.month
    )

    # Filter out negative periods (shouldn't happen, but safety)
    df = df[df["payment_period"] >= 0]

    # Group and pivot to create cohort matrix
    grouped_df = df.groupby(["cohort", "payment_period"])["amount"].sum()
    cohort_matrix = (
        grouped_df.reset_index().pivot(index="cohort", columns="payment_period", values="amount").fillna(0.0)
    )

    # Rename axes for clarity
    cohort_matrix.index.name = None
    cohort_matrix.columns.name = None

    return cohort_matrix


def apply_predictions_to_cohort_df(
    predictions_dict: Dict[str, Dict[str, float]],
    spend_df: pd.DataFrame,
    cohort_df: pd.DataFrame,
    horizon_months: int = 24,
    scenario: str = None,
) -> pd.DataFrame:
    """
    Apply predictions to extend cohort matrix with predicted values.

    Args:
        predictions_dict: Dict with cohort dates as keys, prediction params as values
        spend_df: DataFrame with spend by cohort
        cohort_df: Actual payments cohort matrix
        horizon_months: Total months to project
        scenario: Filter predictions by scenario if specified

    Returns:
        Extended cohort matrix with predictions
    """
    # Prepare spend data
    spend = spend_df.copy()
    if "cohort" in spend.columns:
        spend["cohort"] = pd.to_datetime(spend["cohort"]).dt.to_period("M").dt.to_timestamp()
        spend = spend.set_index("cohort")
    spend = spend.sort_index()

    # Initialize output matrix
    pred_cols = list(range(horizon_months))
    result = cohort_df.copy()

    # Ensure we have all columns up to horizon
    for col in pred_cols:
        if col not in result.columns:
            result[col] = 0.0

    result = result[pred_cols]  # Reorder columns

    # Apply predictions for each cohort
    for cohort in result.index:
        cohort_str = cohort.strftime("%Y-%m-%d")

        if cohort_str not in predictions_dict:
            continue  # No predictions for this cohort

        pred_config = predictions_dict[cohort_str]

        # Skip if scenario doesn't match
        if scenario and "scenario" in pred_config and pred_config["scenario"] != scenario:
            continue

        m0 = float(pred_config["m0"])
        churn = float(pred_config["churn"])

        # Get spend for this cohort
        spend_amount = float(spend.loc[cohort, "spend"]) if cohort in spend.index else 0.0

        # Find last actual payment period
        cohort_row = result.loc[cohort].fillna(0.0)
        last_actual_period = -1

        # Find the last period with actual (non-zero) data from original cohort_df
        for period in sorted(cohort_df.columns.intersection(result.columns)):
            if pd.notna(cohort_df.at[cohort, period]) and cohort_df.at[cohort, period] != 0:
                last_actual_period = max(last_actual_period, period)

        # Set m0 prediction for period 0 if no actual and we have spend
        if result.at[cohort, 0] == 0 and spend_amount > 0:
            result.at[cohort, 0] = m0 * spend_amount
            if last_actual_period < 0:
                last_actual_period = 0

        # Apply decay from last actual value
        if last_actual_period >= 0:
            reference_value = result.at[cohort, last_actual_period]

            for period in range(last_actual_period + 1, horizon_months):
                # Don't override existing actuals
                if (
                    period in cohort_df.columns
                    and pd.notna(cohort_df.at[cohort, period])
                    and cohort_df.at[cohort, period] != 0
                ):
                    result.at[cohort, period] = cohort_df.at[cohort, period]
                    reference_value = result.at[cohort, period]  # Update reference for decay
                else:
                    # Apply geometric decay
                    decay_periods = period - last_actual_period
                    result.at[cohort, period] = reference_value * ((1.0 - churn) ** decay_periods)

    result.columns.name = "payment_period"
    return result.sort_index()


def apply_threshold_to_cohort_df(
    cohort_df: pd.DataFrame, spend_df: pd.DataFrame, thresholds: List[Dict[str, float]]
) -> pd.DataFrame:
    """
    Apply threshold checks to cohort payments.

    Args:
        cohort_df: Cohort payment matrix
        spend_df: Spend by cohort
        thresholds: List of threshold rules

    Returns:
        Boolean DataFrame indicating threshold failures (True = failed)
    """
    # Prepare spend data
    spend = spend_df.copy()
    if "cohort" in spend.columns:
        spend["cohort"] = pd.to_datetime(spend["cohort"]).dt.to_period("M").dt.to_timestamp()
        spend = spend.set_index("cohort")
    spend = spend.sort_index()

    # Create threshold lookup
    threshold_by_period = {int(t["payment_period_month"]): float(t["minimum_payment_percent"]) for t in thresholds}

    # Initialize failure mask (False = passed, True = failed)
    failure_mask = pd.DataFrame(False, index=cohort_df.index, columns=cohort_df.columns)

    for period in cohort_df.columns:
        if period not in threshold_by_period:
            continue

        required_percent = threshold_by_period[period]

        # Calculate payment ratio vs spend for each cohort
        spend_reindexed = spend.reindex(cohort_df.index)["spend"]

        # Avoid division by zero
        payment_ratios = cohort_df[period] / spend_reindexed.replace({0: np.nan})

        # Mark as failed if below threshold
        failure_mask[period] = (payment_ratios < required_percent).fillna(False)

    failure_mask.columns.name = "payment_period"
    return failure_mask


def get_cvf_cashflows_df(
    predicted_cohort_df: pd.DataFrame,
    spend_df: pd.DataFrame,
    thresholds: List[Dict[str, float]],
    trades: List[Dict[str, float]],
) -> pd.DataFrame:
    """
    Calculate CVF cashflows based on trades, sharing rates, thresholds, and caps.

    Args:
        predicted_cohort_df: Cohort matrix with predictions
        spend_df: Spend by cohort
        thresholds: Threshold rules
        trades: Trade definitions

    Returns:
        DataFrame with CVF collections by cohort and period
    """
    # Get threshold failure mask
    threshold_mask = apply_threshold_to_cohort_df(predicted_cohort_df, spend_df, thresholds)

    def normalize_date(date_str: str) -> pd.Timestamp:
        return pd.to_datetime(date_str).to_period("M").to_timestamp()

    # Initialize output DataFrame
    periods = list(predicted_cohort_df.columns)
    result = pd.DataFrame(0.0, index=pd.Index([], name="cohort"), columns=periods)

    for trade in trades:
        cohort = normalize_date(trade["cohort_start_at"])

        if cohort not in predicted_cohort_df.index:
            # Add empty row for missing cohort
            empty_row = pd.Series(0.0, index=periods, name=cohort)
            result = pd.concat([result, empty_row.to_frame().T])
            continue

        base_share = float(trade["sharing_percentage"])
        cash_cap = float(trade["cash_cap"])

        # Get payments and threshold failures for this cohort
        payments = predicted_cohort_df.loc[cohort, periods].fillna(0.0)
        failures = (
            threshold_mask.loc[cohort, periods] if cohort in threshold_mask.index else pd.Series(False, index=periods)
        )

        # Calculate collections period by period
        collections = []
        cumulative = 0.0

        for period in periods:
            if cumulative >= cash_cap:
                collections.append(0.0)
                continue

            # Determine sharing rate (100% if threshold failed, otherwise base rate)
            share_rate = 1.0 if bool(failures[period]) else base_share

            # Calculate collection amount
            payment_amount = payments[period]
            collection_amount = payment_amount * share_rate

            # Apply cash cap
            remaining_cap = max(0.0, cash_cap - cumulative)
            final_collection = min(collection_amount, remaining_cap)

            collections.append(final_collection)
            cumulative += final_collection

        # Add trade row to result
        trade_row = pd.Series(collections, index=periods, name=cohort)
        result = pd.concat([result, trade_row.to_frame().T])

    # Group by cohort (in case of multiple trades per cohort) and sum
    result = result.groupby(result.index).sum().sort_index()
    result.columns.name = "payment_period"

    return result


# Helper functions for improved calculation
def calculate_ltv_cac_metrics(
    cohort_df: pd.DataFrame, spend_df: pd.DataFrame, horizon_months: int = 24
) -> Dict[str, float]:
    """Calculate LTV, CAC, and MOIC metrics"""

    # Calculate total customer acquisition cost
    total_spend = spend_df["spend"].sum() if "spend" in spend_df.columns else 0.0

    # Calculate total lifetime value (sum of all payments)
    total_payments = cohort_df.sum().sum()

    # Calculate number of cohorts/campaigns
    num_cohorts = len(cohort_df)

    # Basic metrics
    ltv_estimate = total_payments / num_cohorts if num_cohorts > 0 else 0.0
    cac_estimate = total_spend / num_cohorts if num_cohorts > 0 else 0.0
    moic = total_payments / total_spend if total_spend > 0 else 0.0

    return {
        "ltv_estimate": ltv_estimate,
        "cac_estimate": cac_estimate,
        "moic_to_date": moic,
        "total_payments": total_payments,
        "total_spend": total_spend,
    }


def calculate_current_month_owed(cashflows_df: pd.DataFrame, as_of_month: date) -> float:
    """Calculate total amount owed for current month"""

    # Convert as_of_month to period index if needed
    current_period = pd.Timestamp(as_of_month).to_period("M").to_timestamp()

    # Find matching column (this would need refinement based on your cashflow structure)
    # For now, return sum of latest period's collections
    if len(cashflows_df.columns) > 0:
        latest_period = cashflows_df.columns[-1]
        return cashflows_df[latest_period].sum()

    return 0.0
