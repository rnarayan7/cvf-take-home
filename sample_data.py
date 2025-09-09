from datetime import date
from dateutil.relativedelta import relativedelta
from sqlalchemy import select
from .storage import init_db, SessionLocal
from .models import Company, Cohort, Adjustment, Payment
from .calc import recompute_cashflows

def seed():
    init_db()
    db = SessionLocal()
    # create company
    co = db.execute(select(Company).where(Company.name=="Acme Co")).scalar_one_or_none()
    if not co:
        co = Company(name="Acme Co", cap_multiple=1.5, base_share=0.5, flip_100_on_threshold=True)
        db.add(co); db.commit()
    # cohorts for Jan, Feb, Mar 2024
    months = [date(2024,1,1), date(2024,2,1), date(2024,3,1)]
    planned = [100000, 120000, 90000]
    for m, p in zip(months, planned):
        if not db.execute(select(Cohort).where(Cohort.company_id==co.id, Cohort.cohort_month==m)).scalar_one_or_none():
            db.add(Cohort(company_id=co.id, cohort_month=m, planned_sm=p))
    # adjustments (actuals) for those months
    actuals = [95000, 130000, 88000]
    for m, a in zip(months, actuals):
        if not db.execute(select(Adjustment).where(Adjustment.company_id==co.id, Adjustment.month==m)).scalar_one_or_none():
            db.add(Adjustment(company_id=co.id, month=m, actual_sm=a))
    # payments: each cohort pays over time
    def add_payment(cohort_m, months_after, amt):
        paid_m = cohort_m + relativedelta(months=months_after)
        db.add(Payment(company_id=co.id, cohort_month=cohort_m, paid_month=paid_m, amount=amt))

    for i, m in enumerate(months):
        add_payment(m, 1, 20000 + i*2000)
        add_payment(m, 2, 25000 + i*2000)
        add_payment(m, 3, 30000 + i*2000)
        add_payment(m, 6, 15000)
        add_payment(m, 12, 10000)

    db.commit()
    recompute_cashflows(db, co.id, date.today())
    db.close()
    print("Seeded demo data.")

if __name__ == "__main__":
    seed()
