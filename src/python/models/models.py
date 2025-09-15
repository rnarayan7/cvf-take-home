from __future__ import annotations
from pydantic import BaseModel
from typing import List, Optional
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


# Trade schemas
class TradeBase(BaseModel):
    cohort_month: date
    sharing_percentage: float = 0.5  # Default 50%
    cash_cap: float = 0.0  # Default no cap


class TradeCreate(TradeBase):
    pass


class TradeResponse(TradeBase):
    id: int
    company_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_db(cls, trade: db_schemas.Trade) -> TradeResponse:
        """Convert Trade DB model to TradeResponse API schema"""
        return cls(
            id=trade.id,
            company_id=trade.company_id,
            cohort_month=trade.cohort_month,
            sharing_percentage=trade.sharing_percentage,
            cash_cap=trade.cash_cap,
            created_at=trade.created_at,
        )


# Payment schemas
class PaymentBase(BaseModel):
    customer_id: str
    payment_date: date
    amount: float


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    customer_id: Optional[str] = None
    payment_date: Optional[date] = None
    amount: Optional[float] = None
    cohort_month: Optional[date] = None


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


class ThresholdUpdate(BaseModel):
    payment_period_month: Optional[int] = None
    minimum_payment_percent: Optional[float] = None


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


# Spend schemas
class SpendBase(BaseModel):
    company_id: int
    cohort_month: date
    spend: float


class SpendCreate(SpendBase):
    cohort_month: date
    spend: float


class SpendUpdate(BaseModel):
    company_id: Optional[int] = None
    cohort_month: Optional[date] = None
    spend: Optional[float] = None


class SpendResponse(SpendBase):
    id: int
    created_at: Optional[datetime] = None
    company: Optional[CompanyResponse] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_db(cls, spend: db_schemas.Spend, include_company: bool = False) -> SpendResponse:
        """Convert Spend DB model to SpendResponse API schema"""
        response = cls(
            id=spend.id,
            company_id=spend.company_id,
            cohort_month=spend.cohort_month,
            spend=spend.spend,
            created_at=spend.created_at,
        )

        if include_company and spend.company:
            response.company = CompanyResponse.from_db(spend.company)

        return response


# Analytics response schemas
class MetricsResponse(BaseModel):
    owed_this_month: float
    breaches_count: int
    moic_to_date: float
    ltv_estimate: float
    cac_estimate: float


# Cashflow schemas
class Cohort(BaseModel):
    cohort_month: date
    company_id: int
    spend: float
    periods: List[Period]
    customers: List[str]
    cumulative_payment: float
    funded: bool = False


class FundedCohort(Cohort):
    trade_id: int
    sharing_percentage: float
    cash_cap: float
    cumulative_collected: float
    periods: List[FundedPeriod]
    capped: bool
    funded: bool = True


class Period(BaseModel):
    period: int
    month: date
    payment: float
    cumulative_payment: float


class FundedPeriod(Period):
    threshold_payment_percentage: Optional[float] = None
    threshold_expected_payment: Optional[float] = None
    threshold_failed: bool
    share_applied: float
    collected: float
    cumulative_collected: float
    capped: bool


class PredictedFundedPeriod(FundedPeriod):
    predicted: bool = True


class CashflowResponse(BaseModel):
    cohorts: List[FundedCohort | Cohort]

# Customer schemas
class CustomerBase(BaseModel):
    customer_name: str
    cohort_month: date
    spend_id: int


class CustomerResponse(CustomerBase):
    id: int
    created_at: Optional[datetime] = None
    spend: Optional[SpendResponse] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_db(cls, customer: db_schemas.Customer, include_spend: bool = False) -> CustomerResponse:
        """Convert Customer DB model to CustomerResponse API schema"""
        response = cls(
            id=customer.id,
            customer_name=customer.customer_name,
            cohort_month=customer.cohort_month,
            spend_id=customer.spend_id,
            created_at=customer.created_at,
        )

        if include_spend and customer.spend:
            response.spend = SpendResponse.from_db(customer.spend)

        return response
