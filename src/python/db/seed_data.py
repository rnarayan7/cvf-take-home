"""
Database seeding script
Seeds the database with sample data for development and testing
"""

from sqlalchemy.orm import sessionmaker
import structlog
from datetime import datetime, date

from src.python.db.database import engine
from src.python.db.schemas import Company, Cohort, Payment, Threshold, CashflowSnapshot

logger = structlog.get_logger(__file__)

# Create a session factory
Session = sessionmaker(bind=engine)


def seed_companies(session):
    """Seed companies table with sample data"""
    logger.info("Seeding companies")
    
    companies_data = [
        {"name": "Acme Corp"},
        {"name": "TechStart Inc"},
        {"name": "GrowthCo"}
    ]
    
    created_companies = {}
    for company_data in companies_data:
        # Check if company already exists
        existing = session.query(Company).filter_by(name=company_data["name"]).first()
        if existing:
            logger.info("Company already exists", name=company_data["name"], id=existing.id)
            created_companies[company_data["name"]] = existing
            continue
            
        company = Company(
            name=company_data["name"],
            created_at=datetime.utcnow()
        )
        session.add(company)
        session.flush()  # Flush to get the ID
        created_companies[company_data["name"]] = company
        logger.info("Created company", name=company.name, id=company.id)
    
    return created_companies


def seed_cohorts(session, companies):
    """Seed cohorts table with sample data"""
    logger.info("Seeding cohorts")
    
    cohorts_data = [
        {
            "company_name": "Acme Corp",
            "cohorts": [
                {
                    "cohort_month": date(2024, 1, 1),
                    "planned_sm": 100000.0,
                    "sharing_percentage": 0.35,
                    "cash_cap": 150000.0
                },
                {
                    "cohort_month": date(2024, 2, 1),
                    "planned_sm": 120000.0,
                    "sharing_percentage": 0.40,
                    "cash_cap": 180000.0
                },
                {
                    "cohort_month": date(2024, 3, 1),
                    "planned_sm": 90000.0,
                    "sharing_percentage": 0.32,
                    "cash_cap": 120000.0
                }
            ]
        },
        {
            "company_name": "TechStart Inc",
            "cohorts": [
                {
                    "cohort_month": date(2024, 1, 1),
                    "planned_sm": 50000.0,
                    "sharing_percentage": 0.45,
                    "cash_cap": 75000.0
                },
                {
                    "cohort_month": date(2024, 2, 1),
                    "planned_sm": 60000.0,
                    "sharing_percentage": 0.42,
                    "cash_cap": 90000.0
                }
            ]
        },
        {
            "company_name": "GrowthCo",
            "cohorts": [
                {
                    "cohort_month": date(2024, 2, 1),
                    "planned_sm": 200000.0,
                    "sharing_percentage": 0.30,
                    "cash_cap": 300000.0
                }
            ]
        }
    ]
    
    created_cohorts = {}
    for company_cohorts in cohorts_data:
        company_name = company_cohorts["company_name"]
        company = companies[company_name]
        
        for cohort_data in company_cohorts["cohorts"]:
            # Check if cohort already exists
            existing = session.query(Cohort).filter_by(
                company_id=company.id,
                cohort_month=cohort_data["cohort_month"]
            ).first()
            
            if existing:
                logger.info("Cohort already exists", 
                           company=company_name,
                           cohort_month=cohort_data["cohort_month"])
                cohort_key = f"{company_name}_{cohort_data['cohort_month']}"
                created_cohorts[cohort_key] = existing
                continue
                
            cohort = Cohort(
                company_id=company.id,
                cohort_month=cohort_data["cohort_month"],
                planned_sm=cohort_data["planned_sm"],
                sharing_percentage=cohort_data["sharing_percentage"],
                cash_cap=cohort_data["cash_cap"],
                created_at=datetime.utcnow()
            )
            session.add(cohort)
            session.flush()
            
            cohort_key = f"{company_name}_{cohort_data['cohort_month']}"
            created_cohorts[cohort_key] = cohort
            logger.info("Created cohort",
                       company=company_name,
                       cohort_month=cohort_data["cohort_month"],
                       planned_sm=cohort_data["planned_sm"])
    
    return created_cohorts


def seed_payments(session, companies):
    """Seed payments table with sample data"""
    logger.info("Seeding payments")
    
    payments_data = [
        {
            "company_name": "Acme Corp",
            "payments": [
                {"customer_id": "cust_001", "payment_date": date(2024, 1, 15), "cohort_month": date(2024, 1, 1), "amount": 5000.0},
                {"customer_id": "cust_001", "payment_date": date(2024, 2, 15), "cohort_month": date(2024, 1, 1), "amount": 4500.0},
                {"customer_id": "cust_002", "payment_date": date(2024, 1, 20), "cohort_month": date(2024, 1, 1), "amount": 8000.0},
                {"customer_id": "cust_003", "payment_date": date(2024, 2, 10), "cohort_month": date(2024, 2, 1), "amount": 12000.0}
            ]
        },
        {
            "company_name": "TechStart Inc",
            "payments": [
                {"customer_id": "tech_001", "payment_date": date(2024, 1, 10), "cohort_month": date(2024, 1, 1), "amount": 3000.0}
            ]
        },
        {
            "company_name": "GrowthCo",
            "payments": [
                {"customer_id": "growth_001", "payment_date": date(2024, 2, 12), "cohort_month": date(2024, 2, 1), "amount": 25000.0}
            ]
        }
    ]
    
    payments_created = 0
    for company_payments in payments_data:
        company_name = company_payments["company_name"]
        company = companies[company_name]
        
        for payment_data in company_payments["payments"]:
            # Check if payment already exists (basic duplicate prevention)
            existing = session.query(Payment).filter_by(
                company_id=company.id,
                customer_id=payment_data["customer_id"],
                payment_date=payment_data["payment_date"]
            ).first()
            
            if existing:
                logger.info("Payment already exists",
                           company=company_name,
                           customer_id=payment_data["customer_id"],
                           payment_date=payment_data["payment_date"])
                continue
                
            payment = Payment(
                company_id=company.id,
                customer_id=payment_data["customer_id"],
                payment_date=payment_data["payment_date"],
                cohort_month=payment_data["cohort_month"],
                amount=payment_data["amount"],
                created_at=datetime.utcnow()
            )
            session.add(payment)
            payments_created += 1
            logger.debug("Created payment",
                        company=company_name,
                        customer_id=payment_data["customer_id"],
                        amount=payment_data["amount"])
    
    logger.info("Created payments", total_created=payments_created)


def seed_thresholds(session, companies):
    """Seed thresholds table with sample data"""
    logger.info("Seeding thresholds")
    
    thresholds_data = [
        {
            "company_name": "Acme Corp",
            "thresholds": [
                {"payment_period_month": 0, "minimum_payment_percent": 0.15},
                {"payment_period_month": 1, "minimum_payment_percent": 0.10}
            ]
        },
        {
            "company_name": "TechStart Inc",
            "thresholds": [
                {"payment_period_month": 0, "minimum_payment_percent": 0.20}
            ]
        },
        {
            "company_name": "GrowthCo",
            "thresholds": [
                {"payment_period_month": 1, "minimum_payment_percent": 0.12}
            ]
        }
    ]
    
    thresholds_created = 0
    for company_thresholds in thresholds_data:
        company_name = company_thresholds["company_name"]
        company = companies[company_name]
        
        for threshold_data in company_thresholds["thresholds"]:
            # Check if threshold already exists
            existing = session.query(Threshold).filter_by(
                company_id=company.id,
                payment_period_month=threshold_data["payment_period_month"]
            ).first()
            
            if existing:
                logger.info("Threshold already exists",
                           company=company_name,
                           payment_period_month=threshold_data["payment_period_month"])
                continue
                
            threshold = Threshold(
                company_id=company.id,
                payment_period_month=threshold_data["payment_period_month"],
                minimum_payment_percent=threshold_data["minimum_payment_percent"],
                created_at=datetime.utcnow()
            )
            session.add(threshold)
            thresholds_created += 1
            logger.debug("Created threshold",
                        company=company_name,
                        payment_period_month=threshold_data["payment_period_month"],
                        minimum_payment_percent=threshold_data["minimum_payment_percent"])
    
    logger.info("Created thresholds", total_created=thresholds_created)


def seed_database(force_recreate=False):
    """
    Main seeding function that populates the database with sample data
    
    Args:
        force_recreate (bool): If True, will delete existing data first
    """
    logger.info("Starting database seeding", force_recreate=force_recreate)
    
    session = Session()
    
    try:
        if force_recreate:
            logger.warning("Force recreate enabled - clearing existing data")
            # Delete in reverse dependency order
            session.query(CashflowSnapshot).delete()
            session.query(Threshold).delete()
            session.query(Payment).delete()
            session.query(Cohort).delete()
            session.query(Company).delete()
            session.commit()
            logger.info("Cleared existing data")
        
        # Seed data in dependency order
        companies = seed_companies(session)
        cohorts = seed_cohorts(session, companies)
        seed_payments(session, companies)
        seed_thresholds(session, companies)
        
        # Commit all changes
        session.commit()
        logger.info("Database seeding completed successfully")
        
        # Log summary
        company_count = session.query(Company).count()
        cohort_count = session.query(Cohort).count()
        payment_count = session.query(Payment).count()
        threshold_count = session.query(Threshold).count()
        
        logger.info("Seeding summary",
                   companies=company_count,
                   cohorts=cohort_count,
                   payments=payment_count,
                   thresholds=threshold_count)
        
    except Exception as e:
        logger.error("Error during database seeding", error=str(e))
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Seed database with sample data")
    parser.add_argument("--force", action="store_true", help="Force recreate - clear existing data first")
    
    args = parser.parse_args()
    
    seed_database(force_recreate=args.force)