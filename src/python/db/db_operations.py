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

from src.python.db.schemas import Company, Cohort, Payment, Threshold
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


class CohortOperations:
    """Database operations for Cohort model"""

    def __init__(self, db: Session):
        self.db = db

    def create_cohort(
        self,
        company_id: int,
        cohort_month: date,
        planned_sm: float,
        sharing_percentage: float = 0.5,
        cash_cap: float = 0.0,
    ) -> Cohort:
        """Create a new cohort with trading terms"""
        logger.info(
            "Creating cohort",
            company_id=company_id,
            cohort_month=cohort_month,
            planned_sm=planned_sm,
            sharing_percentage=sharing_percentage,
            cash_cap=cash_cap,
        )

        cohort = Cohort(
            company_id=company_id,
            cohort_month=cohort_month,
            planned_sm=planned_sm,
            sharing_percentage=sharing_percentage,
            cash_cap=cash_cap,
        )
        self.db.add(cohort)
        self.db.commit()
        self.db.refresh(cohort)

        logger.info("Cohort created", cohort_id=cohort.id)
        return cohort

    def list_cohorts_by_company(self, company_id: int) -> List[Cohort]:
        """List all cohorts for a company"""
        logger.debug("Listing cohorts", company_id=company_id)
        return self.db.query(Cohort).filter(Cohort.company_id == company_id).all()

    def get_cohort(self, company_id: int, cohort_month: date) -> Optional[Cohort]:
        """Get specific cohort by company and month"""
        return (
            self.db.query(Cohort)
            .filter(and_(Cohort.company_id == company_id, Cohort.cohort_month == cohort_month))
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

    def list_thresholds_by_company(self, company_id: int) -> List[Threshold]:
        """List all thresholds for a company"""
        logger.debug("Listing thresholds", company_id=company_id)
        return self.db.query(Threshold).filter(Threshold.company_id == company_id).all()


class AnalyticsOperations:
    """Database operations for analytics and calculations"""

    def __init__(self, db: Session):
        self.db = db
        self.payments = PaymentOperations(db)
        self.cohorts = CohortOperations(db)
        self.thresholds = ThresholdOperations(db)

    def get_company_data_for_analytics(self, company_id: int) -> Dict[str, Any]:
        """Get all company data needed for analytics calculations"""
        logger.debug("Fetching analytics data", company_id=company_id)

        # Get payments as DataFrame
        payments_df = self.payments.get_payments_dataframe(company_id)

        # Get cohorts (spend data and trading terms)
        cohorts = self.cohorts.list_cohorts_by_company(company_id)
        spend_data = []
        cohort_trades = []
        for cohort in cohorts:
            spend_data.append({"cohort": cohort.cohort_month, "spend": cohort.planned_sm})
            cohort_trades.append(
                {
                    "cohort_month": cohort.cohort_month.strftime("%Y-%m-%d"),
                    "sharing_percentage": cohort.sharing_percentage,
                    "cash_cap": cohort.cash_cap,
                }
            )
        spend_df = pd.DataFrame(spend_data)

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
            "cohort_trades": cohort_trades,
        }

        logger.debug(
            "Analytics data prepared",
            company_id=company_id,
            payments_count=len(payments_df),
            cohorts_count=len(spend_df),
            thresholds_count=len(threshold_list),
            cohort_trades_count=len(cohort_trades),
        )

        return data




# Session-aware database operations class
class DatabaseOperations:
    """Session-aware database operations interface"""

    def __init__(self, db: Session):
        self.db = db
        self.companies = CompanyOperations(db)
        self.cohorts = CohortOperations(db)
        self.payments = PaymentOperations(db)
        self.thresholds = ThresholdOperations(db)
        self.analytics = AnalyticsOperations(db)


# Factory function for dependency injection
def get_db_operations(db: Session = Depends(get_db)) -> DatabaseOperations:
    """Factory function to get session-aware DatabaseOperations instance"""
    return DatabaseOperations(db)
