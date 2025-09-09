from __future__ import annotations
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Integer, Float, Date, ForeignKey, UniqueConstraint, Boolean

class Base(DeclarativeBase):
    pass

class Company(Base):
    __tablename__ = "companies"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)
    cap_multiple: Mapped[float] = mapped_column(Float, default=1.5)  # total share cap = cap_multiple * sm_spend
    base_share: Mapped[float] = mapped_column(Float, default=0.5)    # 0.5 = 50%
    flip_100_on_threshold: Mapped[bool] = mapped_column(Boolean, default=False)  # example toggle

class Cohort(Base):
    __tablename__ = "cohorts"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    cohort_month: Mapped[Date] = mapped_column(index=True)
    planned_sm: Mapped[float] = mapped_column(Float)  # planned S&M for that month

    __table_args__ = (UniqueConstraint("company_id","cohort_month", name="uq_company_cohort"),)

class Adjustment(Base):
    __tablename__ = "adjustments"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    month: Mapped[Date] = mapped_column(index=True)
    actual_sm: Mapped[float] = mapped_column(Float)   # actual S&M for the month

    __table_args__ = (UniqueConstraint("company_id","month", name="uq_company_adjust_month"),)

class Payment(Base):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    cohort_month: Mapped[Date] = mapped_column(index=True)  # acquisition cohort month
    paid_month: Mapped[Date] = mapped_column(index=True)
    amount: Mapped[float] = mapped_column(Float)

class CashflowSnapshot(Base):
    __tablename__ = "cashflow_snapshots"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    company_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    as_of_month: Mapped[Date] = mapped_column(index=True)
    cohort_month: Mapped[Date] = mapped_column(index=True)
    planned_sm: Mapped[float] = mapped_column(Float)
    actual_sm: Mapped[float] = mapped_column(Float)
    cumulative_payments: Mapped[float] = mapped_column(Float)
    share_rate: Mapped[float] = mapped_column(Float)       # effective rate this month
    owed_this_month: Mapped[float] = mapped_column(Float)  # share applied to payments for paid_month == as_of_month
    cumulative_shared: Mapped[float] = mapped_column(Float)
    at_cap: Mapped[bool] = mapped_column(Boolean, default=False)
    flip_100_active: Mapped[bool] = mapped_column(Boolean, default=False)
