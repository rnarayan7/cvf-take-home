from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from dateutil.relativedelta import relativedelta
from typing import List, Dict, Tuple
from sqlalchemy import select, delete
from sqlalchemy.orm import Session
from .models import Company, Cohort, Adjustment, Payment, CashflowSnapshot

@dataclass
class CompanyTerms:
    cap_multiple: float
    base_share: float
    flip_100_on_threshold: bool

def month_floor(d: date) -> date:
    return date(d.year, d.month, 1)

def month_range(start: date, end: date):
    cur = month_floor(start)
    end = month_floor(end)
    while cur <= end:
        yield cur
        cur = cur + relativedelta(months=1)

def effective_share_rate(terms: CompanyTerms, cohort_month: date, paid_month: date,
                         planned_sm: float, cumulative_shared_to_date: float,
                         cumulative_payments_to_date: float) -> Tuple[float, bool]:
    """Decide the share rate for a cohort in a given paid_month.

    - Base sharing is terms.base_share (e.g., 50% of cohort payments).
    - Stop sharing once cumulative_shared >= cap_multiple * planned_sm.
    - Optional 'flip to 100%' logic (example): if cumulative_payments_to_date is below a simple threshold
      versus expected recovery (e.g., < 20% by month 6), flip to 100% until caught up.
      This is a placeholder policy to demonstrate the mechanism.
    """
    cap = terms.cap_multiple * (planned_sm or 0.0)
    at_cap = cumulative_shared_to_date >= cap - 1e-6
    flip_active = False

    if at_cap:
        return 0.0, False  # no sharing beyond cap

    rate = terms.base_share

    if terms.flip_100_on_threshold:
        # Example threshold: by 6 months post-cohort, expect >= 20% gross payback
        months_elapsed = (paid_month.year - cohort_month.year) * 12 + (paid_month.month - cohort_month.month)
        expected = 0.20 * (planned_sm or 0.0)
        if months_elapsed >= 6 and cumulative_payments_to_date < expected:
            rate = 1.0
            flip_active = True

    return rate, flip_active

def recompute_cashflows(db: Session, company_id: int, thru_month: date):
    """Idempotent recomputation of CashflowSnapshot for a company up to thru_month."""
    # purge existing snapshots for this company up to thru_month
    db.execute(delete(CashflowSnapshot).where(
        CashflowSnapshot.company_id==company_id,
        CashflowSnapshot.as_of_month<=thru_month
    ))

    company = db.get(Company, company_id)
    terms = CompanyTerms(company.cap_multiple, company.base_share, company.flip_100_on_threshold)

    cohorts = db.execute(select(Cohort).where(Cohort.company_id==company_id)).scalars().all()
    adjustments = {a.month: a.actual_sm for a in db.execute(select(Adjustment).where(Adjustment.company_id==company_id)).scalars().all()}

    # group payments by (cohort_month, paid_month)
    pays = db.execute(select(Payment).where(Payment.company_id==company_id)).scalars().all()
    payments_map: Dict[Tuple[date,date], float] = {}
    for p in pays:
        key = (p.cohort_month, p.paid_month)
        payments_map[key] = payments_map.get(key, 0.0) + float(p.amount)

    # iterate months
    all_months = sorted({m for _, m in payments_map.keys()} | set(adjustments.keys()) |
                        {c.cohort_month for c in cohorts})
    if not all_months:
        return
    start = min(all_months)
    end = max(list(all_months) + [thru_month])

    for as_of in month_range(start, end):
        for c in cohorts:
            planned = float(c.planned_sm or 0.0)
            actual = float(adjustments.get(c.cohort_month, 0.0) if c.cohort_month == as_of else adjustments.get(as_of, 0.0))

            # cumulative payments up to as_of for this cohort
            cum_pays = 0.0
            cum_shared = 0.0
            for m in month_range(c.cohort_month, as_of):
                pays_m = float(payments_map.get((c.cohort_month, m), 0.0))
                cum_pays += pays_m
                # effective rate for that m based on state *before* sharing this month's payments
                rate, _ = effective_share_rate(terms, c.cohort_month, m, planned, cum_shared, cum_pays - pays_m)
                shared_m = min(rate * pays_m, max(0.0, terms.cap_multiple * planned - cum_shared))
                cum_shared += shared_m

            # owed in this as_of month is sharing applied to payments in this month
            pays_asof = float(payments_map.get((c.cohort_month, as_of), 0.0))
            rate_asof, flip = effective_share_rate(terms, c.cohort_month, as_of, planned, cum_shared - (0.0), cum_pays - pays_asof)
            owed_asof = 0.0
            # recompute owed for this month carefully without double-sharing beyond cap
            remaining_cap = max(0.0, terms.cap_multiple * planned - (cum_shared - (rate_asof * pays_asof)))
            owed_asof = min(rate_asof * pays_asof, remaining_cap)

            at_cap = (cum_shared >= terms.cap_multiple * planned - 1e-6)

            snap = CashflowSnapshot(
                company_id=company_id,
                as_of_month=as_of,
                cohort_month=c.cohort_month,
                planned_sm=planned,
                actual_sm=float(adjustments.get(c.cohort_month, 0.0) or 0.0),
                cumulative_payments=cum_pays,
                share_rate=rate_asof,
                owed_this_month=owed_asof,
                cumulative_shared=cum_shared,
                at_cap=at_cap,
                flip_100_active=flip
            )
            db.add(snap)
    db.commit()

def owed_summary(db: Session, company_id: int, as_of: date) -> Dict[str, float]:
    """Return total owed this month and a cohort breakdown for a company."""
    rows = db.execute(
        select(CashflowSnapshot).where(
            CashflowSnapshot.company_id==company_id,
            CashflowSnapshot.as_of_month==as_of
        )
    ).scalars().all()
    total = sum(r.owed_this_month for r in rows)
    by_cohort = {str(r.cohort_month): r.owed_this_month for r in rows if r.owed_this_month}
    return {"total_owed": total, "by_cohort": by_cohort}
