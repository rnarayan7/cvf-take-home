"""
Database initialization script
"""

from sqlalchemy import text
from database import engine, create_tables
import os
import structlog

logger = structlog.get_logger("init_db")

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
            conn.execute(text("""
                INSERT OR IGNORE INTO companies (name) VALUES 
                    ('Acme Corp'),
                    ('TechStart Inc'),
                    ('GrowthCo')
            """))
            
            # Get company IDs
            acme = conn.execute(text("SELECT id FROM companies WHERE name = 'Acme Corp'")).scalar()
            techstart = conn.execute(text("SELECT id FROM companies WHERE name = 'TechStart Inc'")).scalar()
            growthco = conn.execute(text("SELECT id FROM companies WHERE name = 'GrowthCo'")).scalar()
            
            # Insert cohorts
            conn.execute(text("""
                INSERT OR IGNORE INTO cohorts (company_id, cohort_month, planned_sm) VALUES
                    (?, '2024-01-01', 100000),
                    (?, '2024-02-01', 120000),
                    (?, '2024-03-01', 90000),
                    (?, '2024-01-01', 50000),
                    (?, '2024-02-01', 60000),
                    (?, '2024-02-01', 200000)
            """), (acme, acme, acme, techstart, techstart, growthco))
            
            # Insert sample payments
            conn.execute(text("""
                INSERT OR IGNORE INTO payments (company_id, customer_id, payment_date, cohort_month, amount) VALUES
                    (?, 'cust_001', '2024-01-15', '2024-01-01', 5000),
                    (?, 'cust_001', '2024-02-15', '2024-01-01', 4500),
                    (?, 'cust_002', '2024-01-20', '2024-01-01', 8000),
                    (?, 'cust_003', '2024-02-10', '2024-02-01', 12000),
                    (?, 'tech_001', '2024-01-10', '2024-01-01', 3000),
                    (?, 'growth_001', '2024-02-12', '2024-02-01', 25000)
            """), (acme, acme, acme, acme, techstart, growthco))
            
            # Insert trades
            conn.execute(text("""
                INSERT OR IGNORE INTO trades (company_id, cohort_start_at, sharing_percentage, cash_cap) VALUES
                    (?, '2024-01-01', 0.35, 150000),
                    (?, '2024-02-01', 0.40, 180000),
                    (?, '2024-01-01', 0.45, 75000),
                    (?, '2024-02-01', 0.30, 300000)
            """), (acme, acme, techstart, growthco))
            
            # Insert thresholds
            conn.execute(text("""
                INSERT OR IGNORE INTO thresholds (company_id, payment_period_month, minimum_payment_percent) VALUES
                    (?, 0, 0.15),
                    (?, 1, 0.10),
                    (?, 0, 0.20),
                    (?, 1, 0.12)
            """), (acme, acme, techstart, growthco))
            
            conn.commit()
            logger.info("Sample data inserted successfully")
    
    logger.info("Database initialization completed")

if __name__ == "__main__":
    init_database()