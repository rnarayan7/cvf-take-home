from __future__ import annotations
from pydantic import BaseModel
from typing import List, Optional, TYPE_CHECKING
from datetime import date, datetime
import src.python.db.schemas as db_schemas


# Company schemas
class CompanyBase(BaseModel):
    name: str


class CompanyCreate(CompanyBase):
    pass


class CompanyResponse(CompanyBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
    
    @classmethod
    def from_db(cls, company: db_schemas.Company) -> CompanyResponse:
        """Convert Company DB model to CompanyResponse API schema"""
        return cls(
            id=company.id,
            name=company.name,
            created_at=company.created_at,
        )


# Cohort schemas
class CohortBase(BaseModel):
    cohort_month: date
    planned_sm: float
    sharing_percentage: float = 0.5  # Default 50%
    cash_cap: float = 0.0  # Default no cap


class CohortCreate(CohortBase):
    pass


class CohortResponse(CohortBase):
    id: int
    company_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
    
    @classmethod
    def from_db(cls, cohort: db_schemas.Cohort) -> CohortResponse:
        """Convert Cohort DB model to CohortResponse API schema"""
        return cls(
            id=cohort.id,
            company_id=cohort.company_id,
            cohort_month=cohort.cohort_month,
            planned_sm=cohort.planned_sm,
            sharing_percentage=cohort.sharing_percentage,
            cash_cap=cohort.cash_cap,
            created_at=cohort.created_at,
        )


# Payment schemas
class PaymentBase(BaseModel):
    customer_id: str
    payment_date: date
    amount: float


class PaymentCreate(PaymentBase):
    pass


class PaymentResponse(PaymentBase):
    id: int
    company_id: int
    cohort_month: date
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
    
    @classmethod
    def from_db(cls, payment: db_schemas.Payment) -> PaymentResponse:
        """Convert Payment DB model to PaymentResponse API schema"""
        return cls(
            id=payment.id,
            company_id=payment.company_id,
            customer_id=payment.customer_id,
            payment_date=payment.payment_date,
            cohort_month=payment.cohort_month,
            amount=payment.amount,
            created_at=payment.created_at,
        )


# Threshold schemas
class ThresholdBase(BaseModel):
    payment_period_month: int
    minimum_payment_percent: float


class ThresholdCreate(ThresholdBase):
    pass


class ThresholdResponse(ThresholdBase):
    id: int
    company_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
    
    @classmethod
    def from_db(cls, threshold: db_schemas.Threshold) -> ThresholdResponse:
        """Convert Threshold DB model to ThresholdResponse API schema"""
        return cls(
            id=threshold.id,
            company_id=threshold.company_id,
            payment_period_month=threshold.payment_period_month,
            minimum_payment_percent=threshold.minimum_payment_percent,
            created_at=threshold.created_at,
        )


# Analytics response schemas
class MetricsResponse(BaseModel):
    owed_this_month: float
    breaches_count: int
    moic_to_date: float
    ltv_estimate: float
    cac_estimate: float


class CohortTableRow(BaseModel):
    cohort_month: str
    actual: List[float]
    predicted: List[float]


class CohortTableResponse(BaseModel):
    columns: List[str]
    rows: List[CohortTableRow]


class PeriodData(BaseModel):
    period: int
    payment: float
    share_applied: float
    collected: float
    cumulative: float
    status: str
    threshold_failed: bool
    capped: bool


class CohortCashflowData(BaseModel):
    cohort_id: int
    cohort_month: str
    sharing_percentage: float
    cash_cap: float
    cumulative_collected: float
    periods: List[PeriodData]


class CashflowResponse(BaseModel):
    cohorts: List[CohortCashflowData]


