from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Boolean, DateTime, Text, Numeric, CheckConstraint, UniqueConstraint, Index
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
    trades = relationship("Trade", back_populates="company")
    payments = relationship("Payment", back_populates="company")
    thresholds = relationship("Threshold", back_populates="company")
    spends = relationship("Spend", back_populates="company")


class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    cohort_month = Column(Date, nullable=False, index=True)

    # Trading terms
    sharing_percentage = Column(Numeric, nullable=False, default=0.5)  # e.g., 0.32 for 32%
    cash_cap = Column(Numeric, nullable=False, default=0.0)  # Cash cap for this trade

    created_at = Column(DateTime, default=datetime.utcnow)

    # Constraints
    __table_args__ = (
        UniqueConstraint('company_id', 'cohort_month', name='unique_company_cohort_month'),
        CheckConstraint('sharing_percentage >= 0 AND sharing_percentage <= 1', name='check_sharing_percentage'),
        CheckConstraint('cash_cap >= 0', name='check_cash_cap'),
    )

    # Relationships
    company = relationship("Company", back_populates="trades")


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    customer_id = Column(String, nullable=False, index=True)
    payment_date = Column(Date, nullable=False, index=True)
    cohort_month = Column(Date, nullable=False, index=True)  # Derived from first payment
    amount = Column(Numeric, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    company = relationship("Company", back_populates="payments")


class Threshold(Base):
    __tablename__ = "thresholds"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    payment_period_month = Column(Integer, nullable=False)  # 0, 1, 2, etc.
    minimum_payment_percent = Column(Numeric, nullable=False)  # e.g., 0.15 for 15%
    created_at = Column(DateTime, default=datetime.utcnow)

    # Constraints
    __table_args__ = (
        CheckConstraint('payment_period_month >= 0', name='check_payment_period_month'),
        CheckConstraint('minimum_payment_percent >= 0 AND minimum_payment_percent <= 1', name='check_minimum_payment_percent'),
    )

    # Relationships
    company = relationship("Company", back_populates="thresholds")


class Spend(Base):
    __tablename__ = "spends"

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    cohort_month = Column(Date, nullable=False, index=True)
    spend = Column(Numeric, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Constraints
    __table_args__ = (
        UniqueConstraint('company_id', 'cohort_month', name='unique_company_spend_cohort_month'),
        CheckConstraint('spend >= 0', name='check_spend_positive'),
    )

    # Relationships
    company = relationship("Company", back_populates="spends")


