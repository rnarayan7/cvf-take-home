"""
CVF Data Pipeline Implementation
Based on the Jupyter notebook exercises
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from collections import defaultdict
from src.python.db.schemas import Trade, Payment, Spend, Threshold, Date
from src.python.models.models import CashflowResponse, Cohort, FundedCohort, Period, FundedPeriod
from dataclasses import dataclass, field


def _aggregate_payments_by_month(payments: List[Payment]) -> Dict:
    payments_by_month = defaultdict(list)
    for p in payments:
        month_key = p.payment_date.replace(day=1)
        payments_by_month[month_key].append(p)
    return payments_by_month


def compute_company_cohort_cashflows(
    company_id: str, trades: List[Trade], payments: List[Payment], spends: List[Spend], thresholds: List[Threshold]
) -> List[Cohort | FundedCohort]:
    
    @dataclass
    class ConsolidatedCohort:
        spend: Spend
        trade: Optional[Trade] = None
        payments: List[Payment] = field(default_factory=list)

    consolidated = {s.cohort_month: ConsolidatedCohort(spend=s) for s in spends}
    for tr in trades:
        consolidated[tr.cohort_month].trade = tr
    for p in payments:
        consolidated[p.cohort_month].payments.append(p)

    cohorts: List[Cohort | FundedCohort] = []
    for cohort_month, ch in consolidated.items():
        payments_by_month = _aggregate_payments_by_month(payments=ch.payments)
        thresholds_by_period_num = {th.payment_period_month: th for th in thresholds}
        customers = [p.customer_id for p in payments]

        cumulative_payment = 0
        cumulative_collected = 0
        capped = False

        periods = []

        for period_num in range(len(payments_by_month.keys())):
            payment_period_month = list(payments_by_month.keys())[period_num]
            payments = payments_by_month[payment_period_month]

            payment_sum = sum([p.amount for p in payments])
            cumulative_payment += payment_sum

            if ch.trade:
                payment_percentage = payment_sum / ch.spend.spend
                threshold = thresholds_by_period_num.get(period_num, None)
                threshold_failed = threshold is not None and payment_percentage < threshold.minimum_payment_percent
                share_applied = 1 if threshold_failed else ch.trade.sharing_percentage
                collected = min(share_applied * payment_sum, ch.trade.cash_cap - cumulative_collected)
                cumulative_collected += collected
                period_capped = collected == ch.trade.cash_cap
                capped = True if period_capped else capped

                periods.append(
                    FundedPeriod(
                        period=period_num,
                        month=payment_period_month,
                        payment=payment_sum,
                        cumulative_payment=cumulative_payment,
                        threshold_payment_percentage=threshold.minimum_payment_percent if threshold else None,
                        threshold_failed=threshold_failed,
                        share_applied=share_applied,
                        collected=collected,
                        cumulative_collected=cumulative_collected,
                        capped=period_capped,
                    )
                )

            else:
                periods.append(
                    Period(
                        period=period_num,
                        month=payment_period_month,
                        payment=payment_sum,
                        cumulative_payment=cumulative_payment,
                    )
                )

        if ch.trade:
            cohorts.append(
                FundedCohort(
                    cohort_month=cohort_month,
                    company_id=company_id,
                    spend=ch.spend.spend,
                    periods=periods,
                    customers=customers,
                    cumulative_payment=cumulative_payment,
                    trade_id=ch.trade.id,
                    sharing_percentage=ch.trade.sharing_percentage,
                    cash_cap=ch.trade.cash_cap,
                    cumulative_collected=cumulative_collected,
                    capped=capped,
                )
            )
        else:
            cohorts.append(
                Cohort(
                    cohort_month=cohort_month,
                    company_id=company_id,
                    spend=ch.spend.spend,
                    periods=periods,
                    customers=customers,
                    cumulative_payment=cumulative_payment,
                )
            )

    return cohorts


def cohorts_to_cvf_cashflows_df(cohorts: List[Cohort | FundedCohort]) -> pd.DataFrame:
    """
    Convert the output of compute_company_cohort_cashflows to CVF cashflows DataFrame format
    matching the structure from the take_home.ipynb notebook.
    
    Args:
        cohorts: List of Cohort and FundedCohort objects
        
    Returns:
        DataFrame with cohort dates as index, monthly periods as columns, and CVF collections as values
    """
    if not cohorts:
        return pd.DataFrame()
    
    # Convert cohort months to timestamps and find date range
    cohort_dates = []
    max_periods = 0
    
    for cohort in cohorts:
        # Parse cohort_month string to timestamp
        if isinstance(cohort.cohort_month, str):
            cohort_date = pd.to_datetime(cohort.cohort_month)
        else:
            cohort_date = pd.to_datetime(cohort.cohort_month)
        cohort_dates.append(cohort_date)
        
        # Find the maximum number of periods across all cohorts
        if len(cohort.periods) > max_periods:
            max_periods = len(cohort.periods)
    
    if not cohort_dates:
        return pd.DataFrame()
        
    # Create date range for columns (monthly periods)
    start_date = min(cohort_dates)
    # Create enough columns to accommodate all periods from all cohorts
    total_months = max_periods + 12  # Extra buffer for proper display
    date_columns = pd.date_range(start=start_date, periods=total_months, freq='MS')
    
    # Initialize DataFrame with cohort dates as index and monthly periods as columns
    cvf_df = pd.DataFrame(0.0, index=sorted(cohort_dates), columns=date_columns)
    
    # Populate the DataFrame with CVF collection data
    for cohort in cohorts:
        # Parse cohort date
        if isinstance(cohort.cohort_month, str):
            cohort_date = pd.to_datetime(cohort.cohort_month)
        else:
            cohort_date = pd.to_datetime(cohort.cohort_month)
            
        # Only process funded cohorts (those with trades) for CVF collections
        if isinstance(cohort, FundedCohort):
            for period in cohort.periods:
                # Calculate the actual month for this period
                period_month = cohort_date + pd.DateOffset(months=period.period)
                
                # Ensure the period_month exists in our columns
                if period_month in cvf_df.columns:
                    # Use the collected amount for CVF cashflows
                    cvf_df.loc[cohort_date, period_month] = period.collected
        # For unfunded cohorts, we don't collect anything (leave as 0)
    
    return cvf_df


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
