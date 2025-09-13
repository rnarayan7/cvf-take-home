from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    cohorts = relationship("Cohort", back_populates="company")
    payments = relationship("Payment", back_populates="company")
    thresholds = relationship("Threshold", back_populates="company")


class Cohort(Base):
    __tablename__ = "cohorts"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    cohort_month = Column(Date, nullable=False, index=True)
    planned_sm = Column(Float, nullable=False)  # Planned Sales & Marketing spend

    # Trading terms (moved from Trade model)
    sharing_percentage = Column(Float, nullable=False, default=0.5)  # e.g., 0.32 for 32%
    cash_cap = Column(Float, nullable=False, default=0.0)  # Cash cap for this cohort

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="cohorts")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    customer_id = Column(String, nullable=False, index=True)
    payment_date = Column(Date, nullable=False, index=True)
    cohort_month = Column(Date, nullable=False, index=True)  # Derived from first payment
    amount = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="payments")


class Threshold(Base):
    __tablename__ = "thresholds"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    payment_period_month = Column(Integer, nullable=False)  # 0, 1, 2, etc.
    minimum_payment_percent = Column(Float, nullable=False)  # e.g., 0.15 for 15%
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="thresholds")


class CashflowSnapshot(Base):
    __tablename__ = "cashflow_snapshots"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    cohort_month = Column(Date, nullable=False, index=True)
    as_of_month = Column(Date, nullable=False, index=True)

    # Calculated fields
    planned_sm = Column(Float, nullable=False)
    actual_sm = Column(Float)
    cumulative_payments = Column(Float, nullable=False, default=0.0)
    share_rate = Column(Float, nullable=False)  # Effective sharing rate
    owed_this_month = Column(Float, nullable=False, default=0.0)
    cumulative_shared = Column(Float, nullable=False, default=0.0)
    at_cap = Column(Boolean, default=False)
    flip_100_active = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)


