from pydantic import BaseModel
from typing import List, Optional
from datetime import date, datetime


# Company schemas
class CompanyBase(BaseModel):
    name: str


class CompanyCreate(CompanyBase):
    pass


class CompanyResponse(CompanyBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


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
    created_at: datetime

    class Config:
        from_attributes = True


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
    created_at: datetime

    class Config:
        from_attributes = True


# Trade schemas removed - trading terms moved to Cohort


# Threshold schemas
class ThresholdBase(BaseModel):
    payment_period_month: int
    minimum_payment_percent: float


class ThresholdCreate(ThresholdBase):
    pass


class ThresholdResponse(ThresholdBase):
    id: int
    company_id: int
    created_at: datetime

    class Config:
        from_attributes = True


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


# Job schemas
class JobResponse(BaseModel):
    id: int
    company_id: int
    trigger: str
    status: str
    started_at: datetime
    finished_at: Optional[datetime]
    log: Optional[str]
    error_message: Optional[str]

    class Config:
        from_attributes = True
