"""
Database seeding script
Seeds the database with sample data for development and testing
"""

from sqlalchemy.orm import sessionmaker
import structlog
from datetime import datetime, date

from src.python.db.database import engine
from src.python.db.schemas import Company, Trade, Payment, Threshold, Spend, Customer

logger = structlog.get_logger(__file__)

# Create a session factory
Session = sessionmaker(bind=engine)


def seed_companies(session):
    """Seed companies table with sample data"""
    logger.info("Seeding companies")

    companies_data = [
        {"name": "Acme Corp"},
        {"name": "TechStart Inc"},
        {"name": "GrowthCo"},
        {"name": "DataDriven Solutions"},
        {"name": "CloudFirst Technologies"},
        {"name": "AI Innovations Ltd"},
        {"name": "ScaleUp Ventures"},
        {"name": "FinTech Masters"},
        {"name": "EcoTech Green"},
        {"name": "HealthTech Plus"},
        {"name": "EdTech Revolution"},
        {"name": "RetailTech Pro"},
        {"name": "SecurityFirst Systems"},
        {"name": "MediaStream Networks"},
        {"name": "LogisticsPro Solutions"},
    ]

    created_companies = {}
    for company_data in companies_data:
        # Check if company already exists
        existing = session.query(Company).filter_by(name=company_data["name"]).first()
        if existing:
            logger.info("Company already exists", name=company_data["name"], id=existing.id)
            created_companies[company_data["name"]] = existing
            continue

        company = Company(name=company_data["name"], created_at=datetime.utcnow())
        session.add(company)
        session.flush()  # Flush to get the ID
        created_companies[company_data["name"]] = company
        logger.info("Created company", name=company.name, id=company.id)

    return created_companies


def seed_trades(session, companies):
    """Seed trades table with sample data"""
    logger.info("Seeding trades")

    trades_data = [
        {
            "company_name": "Acme Corp",
            "trades": [
                {"cohort_month": date(2023, 10, 1), "sharing_percentage": 0.30, "cash_cap": 120000.0},
                {"cohort_month": date(2023, 11, 1), "sharing_percentage": 0.32, "cash_cap": 140000.0},
                {"cohort_month": date(2023, 12, 1), "sharing_percentage": 0.35, "cash_cap": 165000.0},
                {"cohort_month": date(2024, 1, 1), "sharing_percentage": 0.35, "cash_cap": 150000.0},
                {"cohort_month": date(2024, 2, 1), "sharing_percentage": 0.40, "cash_cap": 180000.0},
                {"cohort_month": date(2024, 3, 1), "sharing_percentage": 0.32, "cash_cap": 135000.0},
                {"cohort_month": date(2024, 4, 1), "sharing_percentage": 0.38, "cash_cap": 195000.0},
                {"cohort_month": date(2024, 5, 1), "sharing_percentage": 0.36, "cash_cap": 157000.0},
            ],
        },
        {
            "company_name": "TechStart Inc",
            "trades": [
                {"cohort_month": date(2023, 11, 1), "sharing_percentage": 0.40, "cash_cap": 65000.0},
                {"cohort_month": date(2023, 12, 1), "sharing_percentage": 0.42, "cash_cap": 80000.0},
                {"cohort_month": date(2024, 1, 1), "sharing_percentage": 0.45, "cash_cap": 75000.0},
                {"cohort_month": date(2024, 2, 1), "sharing_percentage": 0.42, "cash_cap": 90000.0},
                {"cohort_month": date(2024, 3, 1), "sharing_percentage": 0.44, "cash_cap": 105000.0},
                {"cohort_month": date(2024, 4, 1), "sharing_percentage": 0.43, "cash_cap": 97000.0},
            ],
        },
        {
            "company_name": "GrowthCo",
            "trades": [
                {"cohort_month": date(2023, 12, 1), "sharing_percentage": 0.28, "cash_cap": 270000.0},
                {"cohort_month": date(2024, 1, 1), "sharing_percentage": 0.30, "cash_cap": 330000.0},
                {"cohort_month": date(2024, 2, 1), "sharing_percentage": 0.30, "cash_cap": 300000.0},
                {"cohort_month": date(2024, 3, 1), "sharing_percentage": 0.32, "cash_cap": 375000.0},
                {"cohort_month": date(2024, 4, 1), "sharing_percentage": 0.29, "cash_cap": 285000.0},
            ],
        },
        {
            "company_name": "DataDriven Solutions",
            "trades": [
                {"cohort_month": date(2024, 1, 1), "sharing_percentage": 0.38, "cash_cap": 127000.0},
                {"cohort_month": date(2024, 2, 1), "sharing_percentage": 0.40, "cash_cap": 138000.0},
                {"cohort_month": date(2024, 3, 1), "sharing_percentage": 0.35, "cash_cap": 117000.0},
                {"cohort_month": date(2024, 4, 1), "sharing_percentage": 0.42, "cash_cap": 157000.0},
            ],
        },
        {
            "company_name": "CloudFirst Technologies",
            "trades": [
                {"cohort_month": date(2023, 12, 1), "sharing_percentage": 0.33, "cash_cap": 210000.0},
                {"cohort_month": date(2024, 1, 1), "sharing_percentage": 0.36, "cash_cap": 240000.0},
                {"cohort_month": date(2024, 2, 1), "sharing_percentage": 0.34, "cash_cap": 202000.0},
                {"cohort_month": date(2024, 3, 1), "sharing_percentage": 0.38, "cash_cap": 262000.0},
            ],
        },
        {
            "company_name": "AI Innovations Ltd",
            "trades": [
                {"cohort_month": date(2024, 1, 1), "sharing_percentage": 0.41, "cash_cap": 180000.0},
                {"cohort_month": date(2024, 2, 1), "sharing_percentage": 0.39, "cash_cap": 165000.0},
                {"cohort_month": date(2024, 3, 1), "sharing_percentage": 0.43, "cash_cap": 217000.0},
            ],
        },
        {
            "company_name": "ScaleUp Ventures",
            "trades": [
                {"cohort_month": date(2023, 11, 1), "sharing_percentage": 0.35, "cash_cap": 90000.0},
                {"cohort_month": date(2024, 1, 1), "sharing_percentage": 0.37, "cash_cap": 112000.0},
                {"cohort_month": date(2024, 2, 1), "sharing_percentage": 0.40, "cash_cap": 127000.0},
                {"cohort_month": date(2024, 3, 1), "sharing_percentage": 0.41, "cash_cap": 142000.0},
            ],
        },
        {
            "company_name": "FinTech Masters",
            "trades": [
                {"cohort_month": date(2024, 1, 1), "sharing_percentage": 0.28, "cash_cap": 300000.0},
                {"cohort_month": date(2024, 2, 1), "sharing_percentage": 0.30, "cash_cap": 277000.0},
                {"cohort_month": date(2024, 3, 1), "sharing_percentage": 0.32, "cash_cap": 345000.0},
            ],
        },
        {
            "company_name": "EcoTech Green",
            "trades": [
                {"cohort_month": date(2024, 2, 1), "sharing_percentage": 0.45, "cash_cap": 105000.0},
                {"cohort_month": date(2024, 3, 1), "sharing_percentage": 0.46, "cash_cap": 120000.0},
                {"cohort_month": date(2024, 4, 1), "sharing_percentage": 0.48, "cash_cap": 135000.0},
            ],
        },
        {
            "company_name": "HealthTech Plus",
            "trades": [
                {"cohort_month": date(2024, 1, 1), "sharing_percentage": 0.34, "cash_cap": 225000.0},
                {"cohort_month": date(2024, 2, 1), "sharing_percentage": 0.36, "cash_cap": 247000.0},
                {"cohort_month": date(2024, 3, 1), "sharing_percentage": 0.33, "cash_cap": 210000.0},
            ],
        },
    ]

    created_trades = {}
    for company_trades in trades_data:
        company_name = company_trades["company_name"]
        company = companies[company_name]

        for trade_data in company_trades["trades"]:
            # Check if trade already exists
            existing = (
                session.query(Trade).filter_by(company_id=company.id, cohort_month=trade_data["cohort_month"]).first()
            )

            if existing:
                logger.info("Trade already exists", company=company_name, cohort_month=trade_data["cohort_month"])
                trade_key = f"{company_name}_{trade_data['cohort_month']}"
                created_trades[trade_key] = existing
                continue

            trade = Trade(
                company_id=company.id,
                cohort_month=trade_data["cohort_month"],
                sharing_percentage=trade_data["sharing_percentage"],
                cash_cap=trade_data["cash_cap"],
                created_at=datetime.utcnow(),
            )
            session.add(trade)
            session.flush()

            trade_key = f"{company_name}_{trade_data['cohort_month']}"
            created_trades[trade_key] = trade
            logger.info(
                "Created trade",
                company=company_name,
                cohort_month=trade_data["cohort_month"],
                sharing_percentage=trade_data["sharing_percentage"],
                cash_cap=trade_data["cash_cap"],
            )

    return created_trades


def seed_payments(session, companies):
    """Seed payments table with sample data - extensive multi-month data"""
    logger.info("Seeding payments - generating extensive payment data")

    # Helper function to generate payment amounts with some variance
    import random

    random.seed(42)  # For reproducible data

    def generate_payment_amount(base_amount, variance=0.3):
        """Generate payment amount with variance"""
        return round(base_amount * (1 + random.uniform(-variance, variance)), 2)

    payments_data = [
        {
            "company_name": "Acme Corp",
            "payments": [
                # October 2023 cohort customers
                {
                    "customer_id": "acme_001",
                    "payment_date": date(2023, 10, 15),
                    "cohort_month": date(2023, 10, 1),
                    "amount": generate_payment_amount(5000),
                },
                {
                    "customer_id": "acme_001",
                    "payment_date": date(2023, 11, 15),
                    "cohort_month": date(2023, 10, 1),
                    "amount": generate_payment_amount(4800),
                },
                {
                    "customer_id": "acme_001",
                    "payment_date": date(2023, 12, 15),
                    "cohort_month": date(2023, 10, 1),
                    "amount": generate_payment_amount(4900),
                },
                {
                    "customer_id": "acme_001",
                    "payment_date": date(2024, 1, 15),
                    "cohort_month": date(2023, 10, 1),
                    "amount": generate_payment_amount(5100),
                },
                {
                    "customer_id": "acme_001",
                    "payment_date": date(2024, 2, 15),
                    "cohort_month": date(2023, 10, 1),
                    "amount": generate_payment_amount(4700),
                },
                {
                    "customer_id": "acme_001",
                    "payment_date": date(2024, 3, 15),
                    "cohort_month": date(2023, 10, 1),
                    "amount": generate_payment_amount(4850),
                },
                {
                    "customer_id": "acme_002",
                    "payment_date": date(2023, 10, 20),
                    "cohort_month": date(2023, 10, 1),
                    "amount": generate_payment_amount(7500),
                },
                {
                    "customer_id": "acme_002",
                    "payment_date": date(2023, 11, 20),
                    "cohort_month": date(2023, 10, 1),
                    "amount": generate_payment_amount(7200),
                },
                {
                    "customer_id": "acme_002",
                    "payment_date": date(2023, 12, 20),
                    "cohort_month": date(2023, 10, 1),
                    "amount": generate_payment_amount(7800),
                },
                {
                    "customer_id": "acme_002",
                    "payment_date": date(2024, 1, 20),
                    "cohort_month": date(2023, 10, 1),
                    "amount": generate_payment_amount(7600),
                },
                {
                    "customer_id": "acme_002",
                    "payment_date": date(2024, 2, 20),
                    "cohort_month": date(2023, 10, 1),
                    "amount": generate_payment_amount(7400),
                },
                # November 2023 cohort customers
                {
                    "customer_id": "acme_003",
                    "payment_date": date(2023, 11, 10),
                    "cohort_month": date(2023, 11, 1),
                    "amount": generate_payment_amount(6000),
                },
                {
                    "customer_id": "acme_003",
                    "payment_date": date(2023, 12, 10),
                    "cohort_month": date(2023, 11, 1),
                    "amount": generate_payment_amount(5800),
                },
                {
                    "customer_id": "acme_003",
                    "payment_date": date(2024, 1, 10),
                    "cohort_month": date(2023, 11, 1),
                    "amount": generate_payment_amount(6200),
                },
                {
                    "customer_id": "acme_003",
                    "payment_date": date(2024, 2, 10),
                    "cohort_month": date(2023, 11, 1),
                    "amount": generate_payment_amount(5900),
                },
                {
                    "customer_id": "acme_003",
                    "payment_date": date(2024, 3, 10),
                    "cohort_month": date(2023, 11, 1),
                    "amount": generate_payment_amount(6100),
                },
                {
                    "customer_id": "acme_004",
                    "payment_date": date(2023, 11, 25),
                    "cohort_month": date(2023, 11, 1),
                    "amount": generate_payment_amount(4200),
                },
                {
                    "customer_id": "acme_004",
                    "payment_date": date(2023, 12, 25),
                    "cohort_month": date(2023, 11, 1),
                    "amount": generate_payment_amount(4000),
                },
                {
                    "customer_id": "acme_004",
                    "payment_date": date(2024, 1, 25),
                    "cohort_month": date(2023, 11, 1),
                    "amount": generate_payment_amount(4300),
                },
                {
                    "customer_id": "acme_004",
                    "payment_date": date(2024, 2, 25),
                    "cohort_month": date(2023, 11, 1),
                    "amount": generate_payment_amount(4100),
                },
                # December 2023 cohort customers
                {
                    "customer_id": "acme_005",
                    "payment_date": date(2023, 12, 5),
                    "cohort_month": date(2023, 12, 1),
                    "amount": generate_payment_amount(8500),
                },
                {
                    "customer_id": "acme_005",
                    "payment_date": date(2024, 1, 5),
                    "cohort_month": date(2023, 12, 1),
                    "amount": generate_payment_amount(8200),
                },
                {
                    "customer_id": "acme_005",
                    "payment_date": date(2024, 2, 5),
                    "cohort_month": date(2023, 12, 1),
                    "amount": generate_payment_amount(8800),
                },
                {
                    "customer_id": "acme_005",
                    "payment_date": date(2024, 3, 5),
                    "cohort_month": date(2023, 12, 1),
                    "amount": generate_payment_amount(8400),
                },
                {
                    "customer_id": "acme_005",
                    "payment_date": date(2024, 4, 5),
                    "cohort_month": date(2023, 12, 1),
                    "amount": generate_payment_amount(8600),
                },
                # January 2024 cohort customers
                {
                    "customer_id": "acme_006",
                    "payment_date": date(2024, 1, 15),
                    "cohort_month": date(2024, 1, 1),
                    "amount": generate_payment_amount(5000),
                },
                {
                    "customer_id": "acme_006",
                    "payment_date": date(2024, 2, 15),
                    "cohort_month": date(2024, 1, 1),
                    "amount": generate_payment_amount(4800),
                },
                {
                    "customer_id": "acme_006",
                    "payment_date": date(2024, 3, 15),
                    "cohort_month": date(2024, 1, 1),
                    "amount": generate_payment_amount(5200),
                },
                {
                    "customer_id": "acme_006",
                    "payment_date": date(2024, 4, 15),
                    "cohort_month": date(2024, 1, 1),
                    "amount": generate_payment_amount(4900),
                },
                {
                    "customer_id": "acme_007",
                    "payment_date": date(2024, 1, 20),
                    "cohort_month": date(2024, 1, 1),
                    "amount": generate_payment_amount(7000),
                },
                {
                    "customer_id": "acme_007",
                    "payment_date": date(2024, 2, 20),
                    "cohort_month": date(2024, 1, 1),
                    "amount": generate_payment_amount(6800),
                },
                {
                    "customer_id": "acme_007",
                    "payment_date": date(2024, 3, 20),
                    "cohort_month": date(2024, 1, 1),
                    "amount": generate_payment_amount(7200),
                },
                # February 2024 cohort customers
                {
                    "customer_id": "acme_008",
                    "payment_date": date(2024, 2, 10),
                    "cohort_month": date(2024, 2, 1),
                    "amount": generate_payment_amount(9500),
                },
                {
                    "customer_id": "acme_008",
                    "payment_date": date(2024, 3, 10),
                    "cohort_month": date(2024, 2, 1),
                    "amount": generate_payment_amount(9200),
                },
                {
                    "customer_id": "acme_008",
                    "payment_date": date(2024, 4, 10),
                    "cohort_month": date(2024, 2, 1),
                    "amount": generate_payment_amount(9800),
                },
                {
                    "customer_id": "acme_009",
                    "payment_date": date(2024, 2, 25),
                    "cohort_month": date(2024, 2, 1),
                    "amount": generate_payment_amount(6500),
                },
                {
                    "customer_id": "acme_009",
                    "payment_date": date(2024, 3, 25),
                    "cohort_month": date(2024, 2, 1),
                    "amount": generate_payment_amount(6300),
                },
                {
                    "customer_id": "acme_009",
                    "payment_date": date(2024, 4, 25),
                    "cohort_month": date(2024, 2, 1),
                    "amount": generate_payment_amount(6700),
                },
                # March 2024 cohort customers
                {
                    "customer_id": "acme_010",
                    "payment_date": date(2024, 3, 8),
                    "cohort_month": date(2024, 3, 1),
                    "amount": generate_payment_amount(4800),
                },
                {
                    "customer_id": "acme_010",
                    "payment_date": date(2024, 4, 8),
                    "cohort_month": date(2024, 3, 1),
                    "amount": generate_payment_amount(4600),
                },
                {
                    "customer_id": "acme_010",
                    "payment_date": date(2024, 5, 8),
                    "cohort_month": date(2024, 3, 1),
                    "amount": generate_payment_amount(4900),
                },
            ],
        },
        {
            "company_name": "TechStart Inc",
            "payments": [
                # November 2023 cohort
                {
                    "customer_id": "tech_001",
                    "payment_date": date(2023, 11, 10),
                    "cohort_month": date(2023, 11, 1),
                    "amount": generate_payment_amount(3500),
                },
                {
                    "customer_id": "tech_001",
                    "payment_date": date(2023, 12, 10),
                    "cohort_month": date(2023, 11, 1),
                    "amount": generate_payment_amount(3300),
                },
                {
                    "customer_id": "tech_001",
                    "payment_date": date(2024, 1, 10),
                    "cohort_month": date(2023, 11, 1),
                    "amount": generate_payment_amount(3600),
                },
                {
                    "customer_id": "tech_001",
                    "payment_date": date(2024, 2, 10),
                    "cohort_month": date(2023, 11, 1),
                    "amount": generate_payment_amount(3400),
                },
                {
                    "customer_id": "tech_001",
                    "payment_date": date(2024, 3, 10),
                    "cohort_month": date(2023, 11, 1),
                    "amount": generate_payment_amount(3550),
                },
                {
                    "customer_id": "tech_002",
                    "payment_date": date(2023, 11, 15),
                    "cohort_month": date(2023, 11, 1),
                    "amount": generate_payment_amount(2800),
                },
                {
                    "customer_id": "tech_002",
                    "payment_date": date(2023, 12, 15),
                    "cohort_month": date(2023, 11, 1),
                    "amount": generate_payment_amount(2600),
                },
                {
                    "customer_id": "tech_002",
                    "payment_date": date(2024, 1, 15),
                    "cohort_month": date(2023, 11, 1),
                    "amount": generate_payment_amount(2900),
                },
                {
                    "customer_id": "tech_002",
                    "payment_date": date(2024, 2, 15),
                    "cohort_month": date(2023, 11, 1),
                    "amount": generate_payment_amount(2750),
                },
                # December 2023 cohort
                {
                    "customer_id": "tech_003",
                    "payment_date": date(2023, 12, 5),
                    "cohort_month": date(2023, 12, 1),
                    "amount": generate_payment_amount(4200),
                },
                {
                    "customer_id": "tech_003",
                    "payment_date": date(2024, 1, 5),
                    "cohort_month": date(2023, 12, 1),
                    "amount": generate_payment_amount(4000),
                },
                {
                    "customer_id": "tech_003",
                    "payment_date": date(2024, 2, 5),
                    "cohort_month": date(2023, 12, 1),
                    "amount": generate_payment_amount(4400),
                },
                {
                    "customer_id": "tech_003",
                    "payment_date": date(2024, 3, 5),
                    "cohort_month": date(2023, 12, 1),
                    "amount": generate_payment_amount(4100),
                },
                # January 2024 cohort
                {
                    "customer_id": "tech_004",
                    "payment_date": date(2024, 1, 12),
                    "cohort_month": date(2024, 1, 1),
                    "amount": generate_payment_amount(3000),
                },
                {
                    "customer_id": "tech_004",
                    "payment_date": date(2024, 2, 12),
                    "cohort_month": date(2024, 1, 1),
                    "amount": generate_payment_amount(2850),
                },
                {
                    "customer_id": "tech_004",
                    "payment_date": date(2024, 3, 12),
                    "cohort_month": date(2024, 1, 1),
                    "amount": generate_payment_amount(3100),
                },
                {
                    "customer_id": "tech_004",
                    "payment_date": date(2024, 4, 12),
                    "cohort_month": date(2024, 1, 1),
                    "amount": generate_payment_amount(2950),
                },
                {
                    "customer_id": "tech_005",
                    "payment_date": date(2024, 1, 18),
                    "cohort_month": date(2024, 1, 1),
                    "amount": generate_payment_amount(5200),
                },
                {
                    "customer_id": "tech_005",
                    "payment_date": date(2024, 2, 18),
                    "cohort_month": date(2024, 1, 1),
                    "amount": generate_payment_amount(5000),
                },
                {
                    "customer_id": "tech_005",
                    "payment_date": date(2024, 3, 18),
                    "cohort_month": date(2024, 1, 1),
                    "amount": generate_payment_amount(5400),
                },
                # February 2024 cohort
                {
                    "customer_id": "tech_006",
                    "payment_date": date(2024, 2, 8),
                    "cohort_month": date(2024, 2, 1),
                    "amount": generate_payment_amount(3800),
                },
                {
                    "customer_id": "tech_006",
                    "payment_date": date(2024, 3, 8),
                    "cohort_month": date(2024, 2, 1),
                    "amount": generate_payment_amount(3600),
                },
                {
                    "customer_id": "tech_006",
                    "payment_date": date(2024, 4, 8),
                    "cohort_month": date(2024, 2, 1),
                    "amount": generate_payment_amount(3900),
                },
                # March 2024 cohort
                {
                    "customer_id": "tech_007",
                    "payment_date": date(2024, 3, 15),
                    "cohort_month": date(2024, 3, 1),
                    "amount": generate_payment_amount(4500),
                },
                {
                    "customer_id": "tech_007",
                    "payment_date": date(2024, 4, 15),
                    "cohort_month": date(2024, 3, 1),
                    "amount": generate_payment_amount(4300),
                },
                {
                    "customer_id": "tech_007",
                    "payment_date": date(2024, 5, 15),
                    "cohort_month": date(2024, 3, 1),
                    "amount": generate_payment_amount(4700),
                },
                {
                    "customer_id": "tech_008",
                    "payment_date": date(2024, 3, 22),
                    "cohort_month": date(2024, 3, 1),
                    "amount": generate_payment_amount(2900),
                },
                {
                    "customer_id": "tech_008",
                    "payment_date": date(2024, 4, 22),
                    "cohort_month": date(2024, 3, 1),
                    "amount": generate_payment_amount(2750),
                },
            ],
        },
        {
            "company_name": "GrowthCo",
            "payments": [
                # December 2023 cohort
                {
                    "customer_id": "growth_001",
                    "payment_date": date(2023, 12, 12),
                    "cohort_month": date(2023, 12, 1),
                    "amount": generate_payment_amount(15000),
                },
                {
                    "customer_id": "growth_001",
                    "payment_date": date(2024, 1, 12),
                    "cohort_month": date(2023, 12, 1),
                    "amount": generate_payment_amount(14500),
                },
                {
                    "customer_id": "growth_001",
                    "payment_date": date(2024, 2, 12),
                    "cohort_month": date(2023, 12, 1),
                    "amount": generate_payment_amount(15500),
                },
                {
                    "customer_id": "growth_001",
                    "payment_date": date(2024, 3, 12),
                    "cohort_month": date(2023, 12, 1),
                    "amount": generate_payment_amount(14800),
                },
                {
                    "customer_id": "growth_001",
                    "payment_date": date(2024, 4, 12),
                    "cohort_month": date(2023, 12, 1),
                    "amount": generate_payment_amount(15200),
                },
                {
                    "customer_id": "growth_002",
                    "payment_date": date(2023, 12, 18),
                    "cohort_month": date(2023, 12, 1),
                    "amount": generate_payment_amount(22000),
                },
                {
                    "customer_id": "growth_002",
                    "payment_date": date(2024, 1, 18),
                    "cohort_month": date(2023, 12, 1),
                    "amount": generate_payment_amount(21500),
                },
                {
                    "customer_id": "growth_002",
                    "payment_date": date(2024, 2, 18),
                    "cohort_month": date(2023, 12, 1),
                    "amount": generate_payment_amount(22800),
                },
                {
                    "customer_id": "growth_002",
                    "payment_date": date(2024, 3, 18),
                    "cohort_month": date(2023, 12, 1),
                    "amount": generate_payment_amount(22200),
                },
                # January 2024 cohort
                {
                    "customer_id": "growth_003",
                    "payment_date": date(2024, 1, 8),
                    "cohort_month": date(2024, 1, 1),
                    "amount": generate_payment_amount(18000),
                },
                {
                    "customer_id": "growth_003",
                    "payment_date": date(2024, 2, 8),
                    "cohort_month": date(2024, 1, 1),
                    "amount": generate_payment_amount(17500),
                },
                {
                    "customer_id": "growth_003",
                    "payment_date": date(2024, 3, 8),
                    "cohort_month": date(2024, 1, 1),
                    "amount": generate_payment_amount(18500),
                },
                {
                    "customer_id": "growth_003",
                    "payment_date": date(2024, 4, 8),
                    "cohort_month": date(2024, 1, 1),
                    "amount": generate_payment_amount(18200),
                },
                {
                    "customer_id": "growth_004",
                    "payment_date": date(2024, 1, 25),
                    "cohort_month": date(2024, 1, 1),
                    "amount": generate_payment_amount(28000),
                },
                {
                    "customer_id": "growth_004",
                    "payment_date": date(2024, 2, 25),
                    "cohort_month": date(2024, 1, 1),
                    "amount": generate_payment_amount(27200),
                },
                {
                    "customer_id": "growth_004",
                    "payment_date": date(2024, 3, 25),
                    "cohort_month": date(2024, 1, 1),
                    "amount": generate_payment_amount(28800),
                },
                # February 2024 cohort
                {
                    "customer_id": "growth_005",
                    "payment_date": date(2024, 2, 12),
                    "cohort_month": date(2024, 2, 1),
                    "amount": generate_payment_amount(25000),
                },
                {
                    "customer_id": "growth_005",
                    "payment_date": date(2024, 3, 12),
                    "cohort_month": date(2024, 2, 1),
                    "amount": generate_payment_amount(24500),
                },
                {
                    "customer_id": "growth_005",
                    "payment_date": date(2024, 4, 12),
                    "cohort_month": date(2024, 2, 1),
                    "amount": generate_payment_amount(25800),
                },
                {
                    "customer_id": "growth_006",
                    "payment_date": date(2024, 2, 20),
                    "cohort_month": date(2024, 2, 1),
                    "amount": generate_payment_amount(19500),
                },
                {
                    "customer_id": "growth_006",
                    "payment_date": date(2024, 3, 20),
                    "cohort_month": date(2024, 2, 1),
                    "amount": generate_payment_amount(19000),
                },
                {
                    "customer_id": "growth_006",
                    "payment_date": date(2024, 4, 20),
                    "cohort_month": date(2024, 2, 1),
                    "amount": generate_payment_amount(20000),
                },
                # March 2024 cohort
                {
                    "customer_id": "growth_007",
                    "payment_date": date(2024, 3, 10),
                    "cohort_month": date(2024, 3, 1),
                    "amount": generate_payment_amount(32000),
                },
                {
                    "customer_id": "growth_007",
                    "payment_date": date(2024, 4, 10),
                    "cohort_month": date(2024, 3, 1),
                    "amount": generate_payment_amount(31500),
                },
                {
                    "customer_id": "growth_007",
                    "payment_date": date(2024, 5, 10),
                    "cohort_month": date(2024, 3, 1),
                    "amount": generate_payment_amount(33000),
                },
                {
                    "customer_id": "growth_008",
                    "payment_date": date(2024, 3, 28),
                    "cohort_month": date(2024, 3, 1),
                    "amount": generate_payment_amount(16500),
                },
                {
                    "customer_id": "growth_008",
                    "payment_date": date(2024, 4, 28),
                    "cohort_month": date(2024, 3, 1),
                    "amount": generate_payment_amount(16200),
                },
            ],
        },
        {
            "company_name": "DataDriven Solutions",
            "payments": [
                # January 2024 cohort
                {
                    "customer_id": "data_001",
                    "payment_date": date(2024, 1, 12),
                    "cohort_month": date(2024, 1, 1),
                    "amount": generate_payment_amount(4500),
                },
                {
                    "customer_id": "data_001",
                    "payment_date": date(2024, 2, 12),
                    "cohort_month": date(2024, 1, 1),
                    "amount": generate_payment_amount(4300),
                },
                {
                    "customer_id": "data_001",
                    "payment_date": date(2024, 3, 12),
                    "cohort_month": date(2024, 1, 1),
                    "amount": generate_payment_amount(4700),
                },
                {
                    "customer_id": "data_001",
                    "payment_date": date(2024, 4, 12),
                    "cohort_month": date(2024, 1, 1),
                    "amount": generate_payment_amount(4400),
                },
                {
                    "customer_id": "data_002",
                    "payment_date": date(2024, 1, 20),
                    "cohort_month": date(2024, 1, 1),
                    "amount": generate_payment_amount(6200),
                },
                {
                    "customer_id": "data_002",
                    "payment_date": date(2024, 2, 20),
                    "cohort_month": date(2024, 1, 1),
                    "amount": generate_payment_amount(6000),
                },
                {
                    "customer_id": "data_002",
                    "payment_date": date(2024, 3, 20),
                    "cohort_month": date(2024, 1, 1),
                    "amount": generate_payment_amount(6400),
                },
                # February 2024 cohort
                {
                    "customer_id": "data_003",
                    "payment_date": date(2024, 2, 8),
                    "cohort_month": date(2024, 2, 1),
                    "amount": generate_payment_amount(5800),
                },
                {
                    "customer_id": "data_003",
                    "payment_date": date(2024, 3, 8),
                    "cohort_month": date(2024, 2, 1),
                    "amount": generate_payment_amount(5600),
                },
                {
                    "customer_id": "data_003",
                    "payment_date": date(2024, 4, 8),
                    "cohort_month": date(2024, 2, 1),
                    "amount": generate_payment_amount(5950),
                },
                {
                    "customer_id": "data_004",
                    "payment_date": date(2024, 2, 15),
                    "cohort_month": date(2024, 2, 1),
                    "amount": generate_payment_amount(3900),
                },
                {
                    "customer_id": "data_004",
                    "payment_date": date(2024, 3, 15),
                    "cohort_month": date(2024, 2, 1),
                    "amount": generate_payment_amount(3750),
                },
                {
                    "customer_id": "data_004",
                    "payment_date": date(2024, 4, 15),
                    "cohort_month": date(2024, 2, 1),
                    "amount": generate_payment_amount(4000),
                },
                # March 2024 cohort
                {
                    "customer_id": "data_005",
                    "payment_date": date(2024, 3, 10),
                    "cohort_month": date(2024, 3, 1),
                    "amount": generate_payment_amount(5200),
                },
                {
                    "customer_id": "data_005",
                    "payment_date": date(2024, 4, 10),
                    "cohort_month": date(2024, 3, 1),
                    "amount": generate_payment_amount(5000),
                },
                {
                    "customer_id": "data_005",
                    "payment_date": date(2024, 5, 10),
                    "cohort_month": date(2024, 3, 1),
                    "amount": generate_payment_amount(5400),
                },
                # April 2024 cohort
                {
                    "customer_id": "data_006",
                    "payment_date": date(2024, 4, 5),
                    "cohort_month": date(2024, 4, 1),
                    "amount": generate_payment_amount(7500),
                },
                {
                    "customer_id": "data_006",
                    "payment_date": date(2024, 5, 5),
                    "cohort_month": date(2024, 4, 1),
                    "amount": generate_payment_amount(7300),
                },
                {
                    "customer_id": "data_007",
                    "payment_date": date(2024, 4, 18),
                    "cohort_month": date(2024, 4, 1),
                    "amount": generate_payment_amount(4800),
                },
                {
                    "customer_id": "data_007",
                    "payment_date": date(2024, 5, 18),
                    "cohort_month": date(2024, 4, 1),
                    "amount": generate_payment_amount(4600),
                },
            ],
        },
        {
            "company_name": "CloudFirst Technologies",
            "payments": [
                # December 2023 cohort
                {
                    "customer_id": "cloud_001",
                    "payment_date": date(2023, 12, 10),
                    "cohort_month": date(2023, 12, 1),
                    "amount": generate_payment_amount(8500),
                },
                {
                    "customer_id": "cloud_001",
                    "payment_date": date(2024, 1, 10),
                    "cohort_month": date(2023, 12, 1),
                    "amount": generate_payment_amount(8200),
                },
                {
                    "customer_id": "cloud_001",
                    "payment_date": date(2024, 2, 10),
                    "cohort_month": date(2023, 12, 1),
                    "amount": generate_payment_amount(8800),
                },
                {
                    "customer_id": "cloud_001",
                    "payment_date": date(2024, 3, 10),
                    "cohort_month": date(2023, 12, 1),
                    "amount": generate_payment_amount(8400),
                },
                {
                    "customer_id": "cloud_001",
                    "payment_date": date(2024, 4, 10),
                    "cohort_month": date(2023, 12, 1),
                    "amount": generate_payment_amount(8600),
                },
                {
                    "customer_id": "cloud_002",
                    "payment_date": date(2023, 12, 25),
                    "cohort_month": date(2023, 12, 1),
                    "amount": generate_payment_amount(12000),
                },
                {
                    "customer_id": "cloud_002",
                    "payment_date": date(2024, 1, 25),
                    "cohort_month": date(2023, 12, 1),
                    "amount": generate_payment_amount(11700),
                },
                {
                    "customer_id": "cloud_002",
                    "payment_date": date(2024, 2, 25),
                    "cohort_month": date(2023, 12, 1),
                    "amount": generate_payment_amount(12300),
                },
                {
                    "customer_id": "cloud_002",
                    "payment_date": date(2024, 3, 25),
                    "cohort_month": date(2023, 12, 1),
                    "amount": generate_payment_amount(12100),
                },
                # January 2024 cohort
                {
                    "customer_id": "cloud_003",
                    "payment_date": date(2024, 1, 15),
                    "cohort_month": date(2024, 1, 1),
                    "amount": generate_payment_amount(9800),
                },
                {
                    "customer_id": "cloud_003",
                    "payment_date": date(2024, 2, 15),
                    "cohort_month": date(2024, 1, 1),
                    "amount": generate_payment_amount(9500),
                },
                {
                    "customer_id": "cloud_003",
                    "payment_date": date(2024, 3, 15),
                    "cohort_month": date(2024, 1, 1),
                    "amount": generate_payment_amount(10100),
                },
                {
                    "customer_id": "cloud_003",
                    "payment_date": date(2024, 4, 15),
                    "cohort_month": date(2024, 1, 1),
                    "amount": generate_payment_amount(9750),
                },
                {
                    "customer_id": "cloud_004",
                    "payment_date": date(2024, 1, 22),
                    "cohort_month": date(2024, 1, 1),
                    "amount": generate_payment_amount(14500),
                },
                {
                    "customer_id": "cloud_004",
                    "payment_date": date(2024, 2, 22),
                    "cohort_month": date(2024, 1, 1),
                    "amount": generate_payment_amount(14200),
                },
                {
                    "customer_id": "cloud_004",
                    "payment_date": date(2024, 3, 22),
                    "cohort_month": date(2024, 1, 1),
                    "amount": generate_payment_amount(14800),
                },
                # February 2024 cohort
                {
                    "customer_id": "cloud_005",
                    "payment_date": date(2024, 2, 8),
                    "cohort_month": date(2024, 2, 1),
                    "amount": generate_payment_amount(7800),
                },
                {
                    "customer_id": "cloud_005",
                    "payment_date": date(2024, 3, 8),
                    "cohort_month": date(2024, 2, 1),
                    "amount": generate_payment_amount(7600),
                },
                {
                    "customer_id": "cloud_005",
                    "payment_date": date(2024, 4, 8),
                    "cohort_month": date(2024, 2, 1),
                    "amount": generate_payment_amount(8000),
                },
                {
                    "customer_id": "cloud_006",
                    "payment_date": date(2024, 2, 20),
                    "cohort_month": date(2024, 2, 1),
                    "amount": generate_payment_amount(11200),
                },
                {
                    "customer_id": "cloud_006",
                    "payment_date": date(2024, 3, 20),
                    "cohort_month": date(2024, 2, 1),
                    "amount": generate_payment_amount(10900),
                },
                {
                    "customer_id": "cloud_006",
                    "payment_date": date(2024, 4, 20),
                    "cohort_month": date(2024, 2, 1),
                    "amount": generate_payment_amount(11500),
                },
                # March 2024 cohort
                {
                    "customer_id": "cloud_007",
                    "payment_date": date(2024, 3, 12),
                    "cohort_month": date(2024, 3, 1),
                    "amount": generate_payment_amount(13500),
                },
                {
                    "customer_id": "cloud_007",
                    "payment_date": date(2024, 4, 12),
                    "cohort_month": date(2024, 3, 1),
                    "amount": generate_payment_amount(13200),
                },
                {
                    "customer_id": "cloud_007",
                    "payment_date": date(2024, 5, 12),
                    "cohort_month": date(2024, 3, 1),
                    "amount": generate_payment_amount(13800),
                },
            ],
        },
    ]

    payments_created = 0
    for company_payments in payments_data:
        company_name = company_payments["company_name"]
        company = companies[company_name]

        for payment_data in company_payments["payments"]:
            # Check if payment already exists (basic duplicate prevention)
            existing = (
                session.query(Payment)
                .filter_by(
                    company_id=company.id,
                    customer_id=payment_data["customer_id"],
                    payment_date=payment_data["payment_date"],
                )
                .first()
            )

            if existing:
                logger.info(
                    "Payment already exists",
                    company=company_name,
                    customer_id=payment_data["customer_id"],
                    payment_date=payment_data["payment_date"],
                )
                continue

            payment = Payment(
                company_id=company.id,
                customer_id=payment_data["customer_id"],
                payment_date=payment_data["payment_date"],
                cohort_month=payment_data["cohort_month"],
                amount=payment_data["amount"],
                created_at=datetime.utcnow(),
            )
            session.add(payment)
            payments_created += 1
            logger.debug(
                "Created payment",
                company=company_name,
                customer_id=payment_data["customer_id"],
                amount=payment_data["amount"],
            )

    logger.info("Created payments", total_created=payments_created)


def seed_thresholds(session, companies):
    """Seed thresholds table with sample data"""
    logger.info("Seeding thresholds")

    thresholds_data = [
        {
            "company_name": "Acme Corp",
            "thresholds": [
                {"payment_period_month": 0, "minimum_payment_percent": 0.15},
                {"payment_period_month": 1, "minimum_payment_percent": 0.10},
                {"payment_period_month": 3, "minimum_payment_percent": 0.25},
                {"payment_period_month": 6, "minimum_payment_percent": 0.45},
            ],
        },
        {
            "company_name": "TechStart Inc",
            "thresholds": [
                {"payment_period_month": 0, "minimum_payment_percent": 0.20},
                {"payment_period_month": 2, "minimum_payment_percent": 0.30},
                {"payment_period_month": 4, "minimum_payment_percent": 0.50},
            ],
        },
        {
            "company_name": "GrowthCo",
            "thresholds": [
                {"payment_period_month": 1, "minimum_payment_percent": 0.12},
                {"payment_period_month": 3, "minimum_payment_percent": 0.28},
                {"payment_period_month": 6, "minimum_payment_percent": 0.55},
                {"payment_period_month": 12, "minimum_payment_percent": 0.75},
            ],
        },
        {
            "company_name": "DataDriven Solutions",
            "thresholds": [
                {"payment_period_month": 0, "minimum_payment_percent": 0.18},
                {"payment_period_month": 2, "minimum_payment_percent": 0.35},
                {"payment_period_month": 6, "minimum_payment_percent": 0.60},
            ],
        },
        {
            "company_name": "CloudFirst Technologies",
            "thresholds": [
                {"payment_period_month": 1, "minimum_payment_percent": 0.14},
                {"payment_period_month": 3, "minimum_payment_percent": 0.32},
                {"payment_period_month": 9, "minimum_payment_percent": 0.70},
            ],
        },
        {
            "company_name": "AI Innovations Ltd",
            "thresholds": [
                {"payment_period_month": 0, "minimum_payment_percent": 0.22},
                {"payment_period_month": 3, "minimum_payment_percent": 0.40},
                {"payment_period_month": 6, "minimum_payment_percent": 0.65},
            ],
        },
        {
            "company_name": "ScaleUp Ventures",
            "thresholds": [
                {"payment_period_month": 1, "minimum_payment_percent": 0.16},
                {"payment_period_month": 4, "minimum_payment_percent": 0.42},
                {"payment_period_month": 8, "minimum_payment_percent": 0.68},
            ],
        },
        {
            "company_name": "FinTech Masters",
            "thresholds": [
                {"payment_period_month": 0, "minimum_payment_percent": 0.10},
                {"payment_period_month": 2, "minimum_payment_percent": 0.25},
                {"payment_period_month": 6, "minimum_payment_percent": 0.50},
                {"payment_period_month": 12, "minimum_payment_percent": 0.80},
            ],
        },
        {
            "company_name": "EcoTech Green",
            "thresholds": [
                {"payment_period_month": 1, "minimum_payment_percent": 0.20},
                {"payment_period_month": 3, "minimum_payment_percent": 0.38},
                {"payment_period_month": 6, "minimum_payment_percent": 0.58},
            ],
        },
        {
            "company_name": "HealthTech Plus",
            "thresholds": [
                {"payment_period_month": 0, "minimum_payment_percent": 0.12},
                {"payment_period_month": 3, "minimum_payment_percent": 0.30},
                {"payment_period_month": 9, "minimum_payment_percent": 0.65},
                {"payment_period_month": 18, "minimum_payment_percent": 0.85},
            ],
        },
    ]

    thresholds_created = 0
    for company_thresholds in thresholds_data:
        company_name = company_thresholds["company_name"]
        company = companies[company_name]

        for threshold_data in company_thresholds["thresholds"]:
            # Check if threshold already exists
            existing = (
                session.query(Threshold)
                .filter_by(company_id=company.id, payment_period_month=threshold_data["payment_period_month"])
                .first()
            )

            if existing:
                logger.info(
                    "Threshold already exists",
                    company=company_name,
                    payment_period_month=threshold_data["payment_period_month"],
                )
                continue

            threshold = Threshold(
                company_id=company.id,
                payment_period_month=threshold_data["payment_period_month"],
                minimum_payment_percent=threshold_data["minimum_payment_percent"],
                created_at=datetime.utcnow(),
            )
            session.add(threshold)
            thresholds_created += 1
            logger.debug(
                "Created threshold",
                company=company_name,
                payment_period_month=threshold_data["payment_period_month"],
                minimum_payment_percent=threshold_data["minimum_payment_percent"],
            )

    logger.info("Created thresholds", total_created=thresholds_created)


def seed_spends(session, companies):
    """Seed spends table with comprehensive monthly coverage for ALL companies"""
    logger.info("Seeding spends - generating comprehensive monthly spend data")

    # Import random for reproducible variance in spend amounts
    import random
    from datetime import date

    random.seed(42)  # For reproducible data

    def generate_spend_amount(base_amount, variance=0.2):
        """Generate spend amount with variance"""
        return round(base_amount * (1 + random.uniform(-variance, variance)), 2)

    # ALL months from Oct 2023 to May 2024 - comprehensive coverage
    all_cohort_months = [
        date(2023, 10, 1),
        date(2023, 11, 1),
        date(2023, 12, 1),
        date(2024, 1, 1),
        date(2024, 2, 1),
        date(2024, 3, 1),
        date(2024, 4, 1),
        date(2024, 5, 1),
    ]

    # Company spend profiles with realistic base amounts (monthly spend budgets)
    company_spend_profiles = {
        "Acme Corp": {"base_spend": 180000, "variance": 0.15},
        "TechStart Inc": {"base_spend": 85000, "variance": 0.25},
        "GrowthCo": {"base_spend": 320000, "variance": 0.18},
        "DataDriven Solutions": {"base_spend": 140000, "variance": 0.22},
        "CloudFirst Technologies": {"base_spend": 230000, "variance": 0.20},
        "AI Innovations Ltd": {"base_spend": 195000, "variance": 0.24},
        "ScaleUp Ventures": {"base_spend": 115000, "variance": 0.28},
        "FinTech Masters": {"base_spend": 290000, "variance": 0.16},
        "EcoTech Green": {"base_spend": 105000, "variance": 0.30},
        "HealthTech Plus": {"base_spend": 210000, "variance": 0.19},
        "EdTech Revolution": {"base_spend": 95000, "variance": 0.26},
        "RetailTech Pro": {"base_spend": 165000, "variance": 0.21},
        "SecurityFirst Systems": {"base_spend": 175000, "variance": 0.23},
        "MediaStream Networks": {"base_spend": 155000, "variance": 0.25},
        "LogisticsPro Solutions": {"base_spend": 135000, "variance": 0.24},
    }

    spends_created = 0

    # Generate spend data for ALL companies and ALL months
    for company_name, company in companies.items():
        spend_profile = company_spend_profiles.get(company_name, {"base_spend": 150000, "variance": 0.2})

        logger.info(
            "Creating spend data for company",
            company=company_name,
            base_spend=spend_profile["base_spend"],
            total_months=len(all_cohort_months),
        )

        for cohort_month in all_cohort_months:
            # Check if spend already exists
            existing = session.query(Spend).filter_by(company_id=company.id, cohort_month=cohort_month).first()

            if existing:
                logger.debug("Spend already exists", company=company_name, cohort_month=cohort_month)
                continue

            # Generate spend amount with variance
            spend_amount = generate_spend_amount(spend_profile["base_spend"], spend_profile["variance"])

            spend = Spend(
                company_id=company.id, cohort_month=cohort_month, spend=spend_amount, created_at=datetime.utcnow()
            )
            session.add(spend)
            spends_created += 1

            logger.debug(
                "Created spend entry", company=company_name, cohort_month=cohort_month, spend_amount=spend_amount
            )

    logger.info(
        "Created spends",
        total_created=spends_created,
        expected_total=len(companies) * len(all_cohort_months),
        companies=len(companies),
        months=len(all_cohort_months),
    )

    # Verification: ensure we have complete coverage
    session.flush()  # Ensure data is available for querying

    for company_name, company in companies.items():
        spend_count = session.query(Spend).filter_by(company_id=company.id).count()
        expected_count = len(all_cohort_months)

        if spend_count != expected_count:
            logger.warning(
                "Incomplete spend coverage",
                company=company_name,
                actual_count=spend_count,
                expected_count=expected_count,
            )
        else:
            logger.debug("Complete spend coverage verified", company=company_name, spend_count=spend_count)


def seed_customers(session, companies):
    """Seed customers table with comprehensive realistic customer data linked to spends"""
    logger.info("Seeding customers - generating comprehensive customer data for all spends")

    import random

    random.seed(42)  # For reproducible data

    # Realistic customer name pools
    first_names = [
        "James",
        "Mary",
        "John",
        "Patricia",
        "Robert",
        "Jennifer",
        "Michael",
        "Linda",
        "David",
        "Elizabeth",
        "William",
        "Barbara",
        "Richard",
        "Susan",
        "Joseph",
        "Jessica",
        "Thomas",
        "Sarah",
        "Christopher",
        "Karen",
        "Charles",
        "Nancy",
        "Daniel",
        "Lisa",
        "Matthew",
        "Betty",
        "Anthony",
        "Helen",
        "Mark",
        "Sandra",
        "Donald",
        "Donna",
        "Steven",
        "Carol",
        "Paul",
        "Ruth",
        "Andrew",
        "Sharon",
        "Joshua",
        "Michelle",
        "Kenneth",
        "Laura",
        "Kevin",
        "Sarah",
        "Brian",
        "Kimberly",
        "George",
        "Deborah",
        "Timothy",
        "Dorothy",
        "Ronald",
        "Amy",
        "Jason",
        "Angela",
        "Edward",
        "Ashley",
        "Jeffrey",
        "Brenda",
        "Ryan",
        "Emma",
        "Jacob",
        "Olivia",
        "Gary",
        "Cynthia",
        "Nicholas",
        "Marie",
        "Eric",
        "Janet",
        "Jonathan",
        "Catherine",
        "Stephen",
        "Frances",
        "Larry",
        "Christine",
        "Justin",
        "Samantha",
        "Scott",
        "Debra",
        "Brandon",
        "Rachel",
    ]

    last_names = [
        "Smith",
        "Johnson",
        "Williams",
        "Brown",
        "Jones",
        "Garcia",
        "Miller",
        "Davis",
        "Rodriguez",
        "Martinez",
        "Hernandez",
        "Lopez",
        "Gonzalez",
        "Wilson",
        "Anderson",
        "Thomas",
        "Taylor",
        "Moore",
        "Jackson",
        "Martin",
        "Lee",
        "Perez",
        "Thompson",
        "White",
        "Harris",
        "Sanchez",
        "Clark",
        "Ramirez",
        "Lewis",
        "Robinson",
        "Walker",
        "Young",
        "Allen",
        "King",
        "Wright",
        "Scott",
        "Torres",
        "Nguyen",
        "Hill",
        "Flores",
        "Green",
        "Adams",
        "Nelson",
        "Baker",
        "Hall",
        "Rivera",
        "Campbell",
        "Mitchell",
        "Carter",
        "Roberts",
        "Gomez",
        "Phillips",
        "Evans",
        "Turner",
        "Diaz",
        "Parker",
        "Cruz",
        "Edwards",
        "Collins",
        "Reyes",
        "Stewart",
        "Morris",
        "Morales",
        "Murphy",
        "Cook",
        "Rogers",
        "Gutierrez",
        "Ortiz",
        "Morgan",
        "Cooper",
        "Peterson",
        "Bailey",
        "Reed",
        "Kelly",
        "Howard",
        "Ramos",
        "Kim",
        "Cox",
        "Ward",
        "Richardson",
    ]

    def generate_customer_name():
        """Generate a realistic customer name"""
        first = random.choice(first_names)
        last = random.choice(last_names)
        return f"{first} {last}"

    # Get all spends from the database
    all_spends = session.query(Spend).all()
    logger.info(f"Found {len(all_spends)} spend records to create customers for")

    customers_created = 0

    for spend in all_spends:
        # Get company name for logging
        company_name = spend.company.name

        # Determine number of customers for this spend (3-8 customers per spend)
        num_customers = random.randint(3, 8)

        logger.debug(
            "Creating customers for spend",
            company=company_name,
            cohort_month=spend.cohort_month,
            spend_amount=float(spend.spend),
            num_customers=num_customers,
        )

        for i in range(num_customers):
            # Check if customer already exists for this spend (basic duplicate prevention)
            # We'll use a simple naming scheme to avoid duplicates in re-runs
            customer_name = generate_customer_name()

            # Ensure no exact duplicate names for the same spend
            existing_names = [c.customer_name for c in session.query(Customer).filter_by(spend_id=spend.id).all()]
            while customer_name in existing_names:
                customer_name = generate_customer_name()

            customer = Customer(
                customer_name=customer_name,
                cohort_month=spend.cohort_month,  # Must match the spend's cohort_month
                spend_id=spend.id,
                created_at=datetime.utcnow(),
            )

            session.add(customer)
            customers_created += 1

            logger.debug(
                "Created customer",
                customer_name=customer_name,
                company=company_name,
                cohort_month=spend.cohort_month,
                spend_id=spend.id,
            )

    # Flush to ensure customers are available for verification
    session.flush()

    logger.info(
        "Created customers",
        total_created=customers_created,
        average_per_spend=round(customers_created / len(all_spends), 1) if all_spends else 0,
    )

    # Verification: check that each spend has customers
    spends_without_customers = []
    for spend in all_spends:
        customer_count = session.query(Customer).filter_by(spend_id=spend.id).count()
        if customer_count == 0:
            spends_without_customers.append(f"{spend.company.name}_{spend.cohort_month}")
        else:
            logger.debug(
                "Verified customers for spend",
                company=spend.company.name,
                cohort_month=spend.cohort_month,
                customer_count=customer_count,
            )

    if spends_without_customers:
        logger.warning("Some spends have no customers", spends_without_customers=spends_without_customers)
    else:
        logger.info("Verification complete - all spends have customers")


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
            session.query(Customer).delete()
            session.query(Spend).delete()
            session.query(Threshold).delete()
            session.query(Payment).delete()
            session.query(Trade).delete()
            session.query(Company).delete()
            session.commit()
            logger.info("Cleared existing data")

        # Seed data in dependency order
        companies = seed_companies(session)
        trades = seed_trades(session, companies)
        seed_payments(session, companies)
        seed_thresholds(session, companies)
        seed_spends(session, companies)
        seed_customers(session, companies)

        # Commit all changes
        session.commit()
        logger.info("Database seeding completed successfully")

        # Log summary
        company_count = session.query(Company).count()
        trade_count = session.query(Trade).count()
        payment_count = session.query(Payment).count()
        threshold_count = session.query(Threshold).count()
        spend_count = session.query(Spend).count()
        customer_count = session.query(Customer).count()

        logger.info(
            "Seeding summary",
            companies=company_count,
            trades=trade_count,
            payments=payment_count,
            thresholds=threshold_count,
            spends=spend_count,
            customers=customer_count,
        )

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
