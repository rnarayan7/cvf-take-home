"""
CVF Data Pipeline Implementation
Based on the Jupyter notebook exercises
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from dateutil.relativedelta import relativedelta
from collections import defaultdict
from src.python.db.schemas import Trade, Payment, Spend, Threshold
from src.python.models.models import Cohort, FundedCohort, Period, FundedPeriod, PredictedFundedPeriod
from dataclasses import dataclass, field
import numpy_financial as npf
from decimal import Decimal

PREDICTION_LENGTH_MONTHS = 36


def _aggregate_payments_by_month(payments: List[Payment]) -> Dict:
    payments_by_month = defaultdict(list)
    for p in payments:
        month_key = p.payment_date.replace(day=1)
        payments_by_month[month_key].append(p)
    return payments_by_month

def _calculate_funded_cohort_irr(spend: float, periods: List[FundedPeriod | PredictedFundedPeriod]) -> Optional[float]:                                                        
    """Calculate IRR for a funded cohort using collected amounts"""                                                                                   
    cash_flows = [-spend]
    cash_flows += [p.payment for p in periods]
    monthly_irr = npf.irr(cash_flows)
    annual_irr = (1 + monthly_irr) ** 12 - 1
    return annual_irr

def _is_predicted_period(period_num: int, payments_by_month: Dict, churn: Optional[float]) -> bool:
    return False if churn is None else period_num >= len(payments_by_month)-1

def _compute_prediction_for_period(periods : List[FundedPeriod | PredictedFundedPeriod], churn : float) -> Decimal:
    return Decimal(periods[-1].payment * (1-churn))

def compute_company_cohort_cashflows(
    company_id: str, trades: List[Trade], payments: List[Payment], spends: List[Spend], thresholds: List[Threshold], churn: Optional[float] = None
) -> List[FundedCohort | Cohort]:
    
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

    cohorts: List[FundedCohort | Cohort] = []
    for cohort_month, ch in consolidated.items():
        payments_by_month = _aggregate_payments_by_month(payments=ch.payments)
        thresholds_by_period_num = {th.payment_period_month: th for th in thresholds}
        customers = [p.customer_id for p in payments]

        cumulative_payment = 0
        cumulative_collected = 0
        capped = False

        periods = []
        num_periods_base = len(payments_by_month)
        num_periods = max(num_periods_base, PREDICTION_LENGTH_MONTHS) if churn is not None and ch.trade else num_periods_base
        latest_period_month = None

        for period_num in range(num_periods):

            payment_sum: Optional[float] = None
            predicted = _is_predicted_period(period_num, payments_by_month, churn)
            if not predicted:
                payment_period_month = list(payments_by_month.keys())[period_num]
                payments = payments_by_month[payment_period_month]
                payment_sum = sum([p.amount for p in payments])
            else:
                payment_period_month = latest_period_month + relativedelta(months = 1)
                payment_sum = _compute_prediction_for_period(periods, churn)
            
            latest_period_month = payment_period_month
            cumulative_payment += payment_sum

            if ch.trade:
                payment_percentage = payment_sum / ch.spend.spend
                threshold = thresholds_by_period_num.get(period_num, None)
                threshold_failed = threshold is not None and payment_percentage < threshold.minimum_payment_percent
                threshold_payment_share = threshold.minimum_payment_percent if threshold is not None else None
                threshold_payment_percentage = threshold_payment_share*100 if threshold_payment_share is not None else None
                threshold_expected_payment = threshold_payment_share * ch.spend.spend if threshold_payment_share else None
                share_applied = 1 if threshold_failed else ch.trade.sharing_percentage
                collected = min(share_applied * payment_sum, ch.trade.cash_cap - cumulative_collected)
                cumulative_collected += collected
                period_capped = collected == ch.trade.cash_cap
                capped = True if period_capped else capped

                period_type = PredictedFundedPeriod if predicted else FundedPeriod
                periods.append(
                    period_type(
                        period=period_num,
                        month=payment_period_month,
                        payment=payment_sum,
                        cumulative_payment=cumulative_payment,
                        threshold_payment_percentage=threshold_payment_percentage,
                        threshold_expected_payment=threshold_expected_payment,
                        threshold_failed=threshold_failed,
                        share_applied=share_applied,
                        collected=collected,
                        cumulative_collected=cumulative_collected,
                        capped=period_capped,
                    )
                )
                if _is_predicted_period(period_num, payments_by_month, churn) and capped:
                    break

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
            annual_irr = _calculate_funded_cohort_irr(ch.spend.spend, periods)
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
                    annual_irr=annual_irr
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

    cohorts.sort(key=lambda x: x.cohort_month)
    return cohorts

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
