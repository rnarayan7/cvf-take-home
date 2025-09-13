"""
Database initialization script
"""

from sqlalchemy import text
import structlog

from src.python.db.database import engine, create_tables

logger = structlog.get_logger(__file__)


def init_database():
    """Initialize database with tables and sample data"""

    logger.info("Creating database tables")
    create_tables()
    logger.info("Tables created successfully")

    # For SQLite development, we can't use the Supabase SQL directly
    # Instead, we'll create a simplified version
    if "sqlite" in str(engine.url):
        logger.info("Setting up SQLite database with sample data")

        with engine.connect() as conn:
            # Create some sample data for SQLite
            from datetime import datetime
            now = datetime.utcnow()
            
            conn.execute(
                text("""
                INSERT OR IGNORE INTO companies (name, created_at) VALUES 
                    ('Acme Corp', :now1),
                    ('TechStart Inc', :now2),
                    ('GrowthCo', :now3)
            """),
                {"now1": now, "now2": now, "now3": now}
            )

            # Get company IDs
            acme = conn.execute(text("SELECT id FROM companies WHERE name = 'Acme Corp'")).scalar()
            techstart = conn.execute(text("SELECT id FROM companies WHERE name = 'TechStart Inc'")).scalar()
            growthco = conn.execute(text("SELECT id FROM companies WHERE name = 'GrowthCo'")).scalar()

            # Insert cohorts with trading terms
            cohort_data = [
                {"company_id": acme, "cohort_month": "2024-01-01", "planned_sm": 100000, "sharing_percentage": 0.35, "cash_cap": 150000, "created_at": now},
                {"company_id": acme, "cohort_month": "2024-02-01", "planned_sm": 120000, "sharing_percentage": 0.40, "cash_cap": 180000, "created_at": now},
                {"company_id": acme, "cohort_month": "2024-03-01", "planned_sm": 90000, "sharing_percentage": 0.32, "cash_cap": 120000, "created_at": now},
                {"company_id": techstart, "cohort_month": "2024-01-01", "planned_sm": 50000, "sharing_percentage": 0.45, "cash_cap": 75000, "created_at": now},
                {"company_id": techstart, "cohort_month": "2024-02-01", "planned_sm": 60000, "sharing_percentage": 0.42, "cash_cap": 90000, "created_at": now},
                {"company_id": growthco, "cohort_month": "2024-02-01", "planned_sm": 200000, "sharing_percentage": 0.30, "cash_cap": 300000, "created_at": now},
            ]
            
            for cohort in cohort_data:
                conn.execute(
                    text("INSERT OR IGNORE INTO cohorts (company_id, cohort_month, planned_sm, sharing_percentage, cash_cap, created_at) VALUES (:company_id, :cohort_month, :planned_sm, :sharing_percentage, :cash_cap, :created_at)"),
                    cohort
                )

            # Insert sample payments
            payment_data = [
                {"company_id": acme, "customer_id": "cust_001", "payment_date": "2024-01-15", "cohort_month": "2024-01-01", "amount": 5000, "created_at": now},
                {"company_id": acme, "customer_id": "cust_001", "payment_date": "2024-02-15", "cohort_month": "2024-01-01", "amount": 4500, "created_at": now},
                {"company_id": acme, "customer_id": "cust_002", "payment_date": "2024-01-20", "cohort_month": "2024-01-01", "amount": 8000, "created_at": now},
                {"company_id": acme, "customer_id": "cust_003", "payment_date": "2024-02-10", "cohort_month": "2024-02-01", "amount": 12000, "created_at": now},
                {"company_id": techstart, "customer_id": "tech_001", "payment_date": "2024-01-10", "cohort_month": "2024-01-01", "amount": 3000, "created_at": now},
                {"company_id": growthco, "customer_id": "growth_001", "payment_date": "2024-02-12", "cohort_month": "2024-02-01", "amount": 25000, "created_at": now},
            ]
            
            for payment in payment_data:
                conn.execute(
                    text("INSERT OR IGNORE INTO payments (company_id, customer_id, payment_date, cohort_month, amount, created_at) VALUES (:company_id, :customer_id, :payment_date, :cohort_month, :amount, :created_at)"),
                    payment
                )

            # Insert thresholds
            threshold_data = [
                {"company_id": acme, "payment_period_month": 0, "minimum_payment_percent": 0.15, "created_at": now},
                {"company_id": acme, "payment_period_month": 1, "minimum_payment_percent": 0.10, "created_at": now},
                {"company_id": techstart, "payment_period_month": 0, "minimum_payment_percent": 0.20, "created_at": now},
                {"company_id": growthco, "payment_period_month": 1, "minimum_payment_percent": 0.12, "created_at": now},
            ]
            
            for threshold in threshold_data:
                conn.execute(
                    text("INSERT OR IGNORE INTO thresholds (company_id, payment_period_month, minimum_payment_percent, created_at) VALUES (:company_id, :payment_period_month, :minimum_payment_percent, :created_at)"),
                    threshold
                )

            conn.commit()
            logger.info("Sample data inserted successfully")

    logger.info("Database initialization completed")


if __name__ == "__main__":
    init_database()
