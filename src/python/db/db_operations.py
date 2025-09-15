"""
Database operations layer for CVF API
Abstracts all database interactions from the main API endpoints
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date
import pandas as pd
import structlog
from fastapi import Depends

from src.python.db.schemas import Company, Trade, Payment, Threshold, Spend, Customer
from src.python.db.database import get_db

logger = structlog.get_logger(__file__)


class CompanyOperations:
    """Database operations for Company model"""

    def __init__(self, db: Session):
        self.db = db

    def create_company(self, name: str) -> Company:
        """Create a new company"""
        logger.info("Creating company", name=name)

        company = Company(name=name)
        self.db.add(company)
        self.db.commit()
        self.db.refresh(company)

        logger.info("Company created", company_id=company.id, name=name)
        return company

    def get_company_by_id(self, company_id: int) -> Optional[Company]:
        """Get company by ID"""
        logger.debug("Fetching company", company_id=company_id)
        return self.db.query(Company).filter(Company.id == company_id).first()

    def get_company_by_name(self, name: str) -> Optional[Company]:
        """Get company by name"""
        logger.debug("Fetching company by name", name=name)
        return self.db.query(Company).filter(Company.name == name).first()

    def list_companies(self) -> List[Company]:
        """List all companies"""
        logger.debug("Listing companies")
        return self.db.query(Company).all()

    def company_exists(self, company_id: int) -> bool:
        """Check if company exists"""
        return self.db.query(Company).filter(Company.id == company_id).first() is not None


class TradeOperations:
    """Database operations for Trade model"""

    def __init__(self, db: Session):
        self.db = db

    def create_trade(
        self,
        company_id: int,
        cohort_month: date,
        sharing_percentage: float = 0.5,
        cash_cap: float = 0.0,
    ) -> Trade:
        """Create a new trade with trading terms"""
        logger.info(
            "Creating trade",
            company_id=company_id,
            cohort_month=cohort_month,
            sharing_percentage=sharing_percentage,
            cash_cap=cash_cap,
        )

        trade = Trade(
            company_id=company_id,
            cohort_month=cohort_month,
            sharing_percentage=sharing_percentage,
            cash_cap=cash_cap,
        )
        self.db.add(trade)
        self.db.commit()
        self.db.refresh(trade)

        logger.info("Trade created", trade_id=trade.id)
        return trade

    def list_trades_by_company(self, company_id: int) -> List[Trade]:
        """List all trades for a company"""
        logger.debug("Listing trades", company_id=company_id)
        return self.db.query(Trade).filter(Trade.company_id == company_id).all()

    def get_trade(self, company_id: int, cohort_month: date) -> Optional[Trade]:
        """Get specific trade by company and month"""
        return (
            self.db.query(Trade)
            .filter(and_(Trade.company_id == company_id, Trade.cohort_month == cohort_month))
            .first()
        )


class PaymentOperations:
    """Database operations for Payment model"""

    def __init__(self, db: Session):
        self.db = db

    def create_payment(
        self,
        company_id: int,
        customer_id: str,
        payment_date: date,
        cohort_month: date,
        amount: float,
        commit: bool = False,
    ) -> Payment:
        """Create a new payment record"""
        logger.debug("Creating payment", company_id=company_id, customer_id=customer_id, amount=amount)

        payment = Payment(
            company_id=company_id,
            customer_id=customer_id,
            payment_date=payment_date,
            cohort_month=cohort_month,
            amount=amount,
        )
        self.db.add(payment)

        if commit:
            self.db.commit()
            self.db.refresh(payment)

        return payment

    def bulk_create_payments(self, payments: List[Payment]) -> int:
        """Bulk create payment records"""
        logger.info("Bulk creating payments", payment_count=len(payments))

        self.db.add_all(payments)
        self.db.commit()

        logger.info("Payments created successfully", count=len(payments))
        return len(payments)

    def list_payments_by_company(self, company_id: int) -> List[Payment]:
        """List all payments for a company"""
        logger.debug("Listing payments", company_id=company_id)
        return self.db.query(Payment).filter(Payment.company_id == company_id).all()

    def get_customer_payments(self, company_id: int, customer_id: str) -> List[Payment]:
        """Get all payments for a specific customer"""
        return (
            self.db.query(Payment)
            .filter(and_(Payment.company_id == company_id, Payment.customer_id == customer_id))
            .all()
        )

    def get_payment_by_id(self, payment_id: int) -> Optional[Payment]:
        """Get payment by ID"""
        logger.debug("Fetching payment", payment_id=payment_id)
        return self.db.query(Payment).filter(Payment.id == payment_id).first()

    def update_payment(
        self,
        payment_id: int,
        amount: Optional[float] = None,
        payment_date: Optional[date] = None,
        customer_id: Optional[str] = None,
        cohort_month: Optional[date] = None,
    ) -> Optional[Payment]:
        """Update an existing payment record"""
        logger.info("Updating payment", payment_id=payment_id)

        payment = self.get_payment_by_id(payment_id)
        if not payment:
            logger.warning("Payment not found for update", payment_id=payment_id)
            return None

        if amount is not None:
            payment.amount = amount
        if payment_date is not None:
            payment.payment_date = payment_date
        if customer_id is not None:
            payment.customer_id = customer_id
        if cohort_month is not None:
            payment.cohort_month = cohort_month

        self.db.commit()
        self.db.refresh(payment)

        logger.info("Payment updated", payment_id=payment_id)
        return payment

    def delete_payment(self, payment_id: int) -> bool:
        """Delete a payment record"""
        logger.info("Deleting payment", payment_id=payment_id)

        payment = self.get_payment_by_id(payment_id)
        if not payment:
            logger.warning("Payment not found for deletion", payment_id=payment_id)
            return False

        self.db.delete(payment)
        self.db.commit()

        logger.info("Payment deleted", payment_id=payment_id)
        return True

    def get_payments_dataframe(self, company_id: int) -> pd.DataFrame:
        """Get payments as pandas DataFrame for calculations"""
        logger.debug("Converting payments to DataFrame", company_id=company_id)

        payments = self.list_payments_by_company(company_id)

        if not payments:
            logger.warning("No payments found", company_id=company_id)
            return pd.DataFrame()

        data = []
        for payment in payments:
            data.append(
                {
                    "customer_id": payment.customer_id,
                    "payment_date": payment.payment_date,
                    "amount": payment.amount,
                    "cohort_month": payment.cohort_month,
                }
            )

        df = pd.DataFrame(data)
        logger.debug("DataFrame created", rows=len(df), columns=list(df.columns))
        return df


# TradeOperations removed - trading terms moved to CohortOperations


class ThresholdOperations:
    """Database operations for Threshold model"""

    def __init__(self, db: Session):
        self.db = db

    def create_threshold(self, company_id: int, payment_period_month: int, minimum_payment_percent: float) -> Threshold:
        """Create a new threshold"""
        logger.info(
            "Creating threshold",
            company_id=company_id,
            payment_period_month=payment_period_month,
            minimum_payment_percent=minimum_payment_percent,
        )

        threshold = Threshold(
            company_id=company_id,
            payment_period_month=payment_period_month,
            minimum_payment_percent=minimum_payment_percent,
        )
        self.db.add(threshold)
        self.db.commit()
        self.db.refresh(threshold)

        logger.info("Threshold created", threshold_id=threshold.id)
        return threshold

    def get_threshold_by_id(self, threshold_id: int) -> Optional[Threshold]:
        """Get threshold by ID"""
        logger.debug("Fetching threshold", threshold_id=threshold_id)
        return self.db.query(Threshold).filter(Threshold.id == threshold_id).first()

    def update_threshold(
        self,
        threshold_id: int,
        payment_period_month: Optional[int] = None,
        minimum_payment_percent: Optional[float] = None,
    ) -> Optional[Threshold]:
        """Update an existing threshold record"""
        logger.info("Updating threshold", threshold_id=threshold_id)

        threshold = self.get_threshold_by_id(threshold_id)
        if not threshold:
            logger.warning("Threshold not found for update", threshold_id=threshold_id)
            return None

        if payment_period_month is not None:
            threshold.payment_period_month = payment_period_month
        if minimum_payment_percent is not None:
            threshold.minimum_payment_percent = minimum_payment_percent

        self.db.commit()
        self.db.refresh(threshold)

        logger.info("Threshold updated", threshold_id=threshold_id)
        return threshold

    def list_thresholds_by_company(self, company_id: int) -> List[Threshold]:
        """List all thresholds for a company"""
        logger.debug("Listing thresholds", company_id=company_id)
        return self.db.query(Threshold).filter(Threshold.company_id == company_id).all()


class SpendOperations:
    """Database operations for Spend model"""

    def __init__(self, db: Session):
        self.db = db

    def create_spend(self, company_id: int, cohort_month: date, spend: float) -> Spend:
        """Create a new spend record"""
        logger.info(
            "Creating spend",
            company_id=company_id,
            cohort_month=cohort_month,
            spend=spend,
        )

        spend_record = Spend(
            company_id=company_id,
            cohort_month=cohort_month,
            spend=spend,
        )
        self.db.add(spend_record)
        self.db.commit()
        self.db.refresh(spend_record)

        logger.info("Spend created", spend_id=spend_record.id)
        return spend_record

    def get_spend_by_id(self, spend_id: int) -> Optional[Spend]:
        """Get spend by ID"""
        logger.debug("Fetching spend", spend_id=spend_id)
        return self.db.query(Spend).filter(Spend.id == spend_id).first()

    def update_spend(
        self,
        spend_id: int,
        company_id: Optional[int] = None,
        cohort_month: Optional[date] = None,
        spend: Optional[float] = None,
    ) -> Optional[Spend]:
        """Update an existing spend record"""
        logger.info("Updating spend", spend_id=spend_id)

        spend_record = self.get_spend_by_id(spend_id)
        if not spend_record:
            logger.warning("Spend not found for update", spend_id=spend_id)
            return None

        if company_id is not None:
            spend_record.company_id = company_id
        if cohort_month is not None:
            spend_record.cohort_month = cohort_month
        if spend is not None:
            spend_record.spend = spend

        self.db.commit()
        self.db.refresh(spend_record)

        logger.info("Spend updated", spend_id=spend_id)
        return spend_record

    def delete_spend(self, spend_id: int) -> bool:
        """Delete a spend record"""
        logger.info("Deleting spend", spend_id=spend_id)

        spend_record = self.get_spend_by_id(spend_id)
        if not spend_record:
            logger.warning("Spend not found for deletion", spend_id=spend_id)
            return False

        self.db.delete(spend_record)
        self.db.commit()

        logger.info("Spend deleted", spend_id=spend_id)
        return True

    def list_spends(self,company_id: Optional[int] = None) -> List[Spend]:
        """List spends with optional filtering and pagination"""
        logger.debug("Listing spends", company_id=company_id)

        query = self.db.query(Spend)

        if company_id is not None:
            query = query.filter(Spend.company_id == company_id)

        query = query.order_by(Spend.cohort_month.desc(), Spend.id.desc())
        return query.all()

    def list_spends_by_company(self,company_id: int) -> List[Spend]:
        """List all spends for a company with optional filtering"""
        logger.debug("Listing spends by company", company_id=company_id)
        return self.list_spends(company_id=company_id)

    def get_spend_by_company_and_cohort(self, company_id: int, cohort_month: date) -> Optional[Spend]:
        """Get specific spend by company and cohort month"""
        return (
            self.db.query(Spend)
            .filter(and_(Spend.company_id == company_id, Spend.cohort_month == cohort_month))
            .first()
        )

    def get_spends_dataframe(self, company_id: int) -> pd.DataFrame:
        """Get spends as pandas DataFrame for calculations"""
        logger.debug("Converting spends to DataFrame", company_id=company_id)

        spends = self.list_spends_by_company(company_id)

        if not spends:
            logger.warning("No spends found", company_id=company_id)
            return pd.DataFrame()

        data = []
        for spend in spends:
            data.append(
                {
                    "cohort": spend.cohort_month,
                    "spend": spend.spend,
                }
            )

        df = pd.DataFrame(data)
        logger.debug("DataFrame created", rows=len(df), columns=list(df.columns))
        return df


class CustomerOperations:
    """Database operations for Customer model"""

    def __init__(self, db: Session):
        self.db = db

    def get_customer_by_id(self, customer_id: int) -> Optional[Customer]:
        """Get customer by ID"""
        logger.debug("Fetching customer", customer_id=customer_id)
        return self.db.query(Customer).filter(Customer.id == customer_id).first()

    def list_customers(
        self,
        cohort_month: Optional[date] = None,
        spend_id: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Customer]:
        """List customers with optional filtering and pagination"""
        logger.debug("Listing customers", cohort_month=cohort_month, spend_id=spend_id, limit=limit, offset=offset)

        query = self.db.query(Customer)

        if cohort_month is not None:
            query = query.filter(Customer.cohort_month == cohort_month)
        if spend_id is not None:
            query = query.filter(Customer.spend_id == spend_id)

        query = query.order_by(Customer.cohort_month.desc(), Customer.id.desc())

        if offset is not None:
            query = query.offset(offset)
        if limit is not None:
            query = query.limit(limit)

        return query.all()


class AnalyticsOperations:
    """Database operations for analytics and calculations"""

    def __init__(self, db: Session):
        self.db = db
        self.payments = PaymentOperations(db)
        self.trades = TradeOperations(db)
        self.thresholds = ThresholdOperations(db)
        self.spends = SpendOperations(db)

    def get_company_data_for_analytics(self, company_id: int) -> Dict[str, Any]:
        """Get all company data needed for analytics calculations"""
        logger.debug("Fetching analytics data", company_id=company_id)

        # Get payments as DataFrame
        payments_df = self.payments.get_payments_dataframe(company_id)

        # Get spends as DataFrame
        spend_df = self.spends.get_spends_dataframe(company_id)

        # Get trades (trading terms)
        trades = self.trades.list_trades_by_company(company_id)
        trade_list = []
        for trade in trades:
            trade_list.append(
                {
                    "cohort_month": trade.cohort_month.strftime("%Y-%m-%d"),
                    "sharing_percentage": trade.sharing_percentage,
                    "cash_cap": trade.cash_cap,
                }
            )

        # Get thresholds
        thresholds = self.thresholds.list_thresholds_by_company(company_id)
        threshold_list = []
        for threshold in thresholds:
            threshold_list.append(
                {
                    "payment_period_month": threshold.payment_period_month,
                    "minimum_payment_percent": threshold.minimum_payment_percent,
                }
            )

        data = {
            "payments_df": payments_df,
            "spend_df": spend_df,
            "thresholds": threshold_list,
            "cohort_trades": trade_list,
        }

        logger.debug(
            "Analytics data prepared",
            company_id=company_id,
            payments_count=len(payments_df),
            spends_count=len(spend_df),
            thresholds_count=len(threshold_list),
            trades_count=len(trade_list),
        )

        return data


# Session-aware database operations class
class DatabaseOperations:
    """Session-aware database operations interface"""

    def __init__(self, db: Session):
        self.db = db
        self.companies = CompanyOperations(db)
        self.trades = TradeOperations(db)
        self.payments = PaymentOperations(db)
        self.thresholds = ThresholdOperations(db)
        self.spends = SpendOperations(db)
        self.customers = CustomerOperations(db)
        self.analytics = AnalyticsOperations(db)


# Factory function for dependency injection
def get_db_operations(db: Session = Depends(get_db)) -> DatabaseOperations:
    """Factory function to get session-aware DatabaseOperations instance"""
    return DatabaseOperations(db)
