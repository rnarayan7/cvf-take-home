"""
Database seeding script
Seeds the database with sample data for development and testing
Data is organized by cohort month with comprehensive coverage
"""

from sqlalchemy.orm import sessionmaker
import structlog
from datetime import datetime, date
import random

from src.python.db.database import engine
from src.python.db.schemas import Company, Trade, Payment, Threshold, Spend, Customer

logger = structlog.get_logger(__file__)

# Create a session factory
Session = sessionmaker(bind=engine)

# Set random seed for reproducible data
random.seed(42)

# Seed data organized by cohort month
# Schema: {'company_name': {'threshold': threshold_data, 'monthly_data': {month: {'spend': spend_data, 'trade': trade_data, 'payments': payment_data}}}}
SEED_DATA_BY_COHORT_MONTH = {
    "Acme Corp": {
        "threshold": [
            {"payment_period_month": 0, "minimum_payment_percent": 0.15},
            {"payment_period_month": 1, "minimum_payment_percent": 0.10},
            {"payment_period_month": 3, "minimum_payment_percent": 0.25},
            {"payment_period_month": 6, "minimum_payment_percent": 0.1},
        ],
        "monthly_data": {
            date(2023, 10, 1): {
                "spend": {"amount": 185000},
                "trade": {"sharing_percentage": 0.30, "cash_cap": 220000.0},
                "payments": [
                    {"customer_id": "acme_001", "payment_date": date(2023, 10, 15), "amount": 5000},
                    {"customer_id": "acme_001", "payment_date": date(2023, 11, 15), "amount": 4800},
                    {"customer_id": "acme_001", "payment_date": date(2023, 12, 15), "amount": 4900},
                    {"customer_id": "acme_001", "payment_date": date(2024, 1, 15), "amount": 5100},
                    {"customer_id": "acme_001", "payment_date": date(2024, 2, 15), "amount": 4700},
                    {"customer_id": "acme_001", "payment_date": date(2024, 3, 15), "amount": 4850},
                    {"customer_id": "acme_002", "payment_date": date(2023, 10, 20), "amount": 7500},
                    {"customer_id": "acme_002", "payment_date": date(2023, 11, 20), "amount": 7200},
                    {"customer_id": "acme_002", "payment_date": date(2023, 12, 20), "amount": 7800},
                    {"customer_id": "acme_002", "payment_date": date(2024, 1, 20), "amount": 7600},
                    {"customer_id": "acme_002", "payment_date": date(2024, 2, 20), "amount": 7400},
                ],
            },
            date(2023, 11, 1): {
                "spend": {"amount": 178000},
                "trade": {"sharing_percentage": 0.32, "cash_cap": 210000.0},
                "payments": [
                    {"customer_id": "acme_003", "payment_date": date(2023, 11, 10), "amount": 6000},
                    {"customer_id": "acme_003", "payment_date": date(2023, 12, 10), "amount": 5800},
                    {"customer_id": "acme_003", "payment_date": date(2024, 1, 10), "amount": 6200},
                    {"customer_id": "acme_003", "payment_date": date(2024, 2, 10), "amount": 5900},
                    {"customer_id": "acme_003", "payment_date": date(2024, 3, 10), "amount": 6100},
                    {"customer_id": "acme_004", "payment_date": date(2023, 11, 25), "amount": 4200},
                    {"customer_id": "acme_004", "payment_date": date(2023, 12, 25), "amount": 4000},
                    {"customer_id": "acme_004", "payment_date": date(2024, 1, 25), "amount": 4300},
                    {"customer_id": "acme_004", "payment_date": date(2024, 2, 25), "amount": 4100},
                ],
            },
            date(2023, 12, 1): {
                "spend": {"amount": 190000},
                "trade": {"sharing_percentage": 0.35, "cash_cap": 230000.0},
                "payments": [
                    {"customer_id": "acme_005", "payment_date": date(2023, 12, 5), "amount": 8500},
                    {"customer_id": "acme_005", "payment_date": date(2024, 1, 5), "amount": 8200},
                    {"customer_id": "acme_005", "payment_date": date(2024, 2, 5), "amount": 8800},
                    {"customer_id": "acme_005", "payment_date": date(2024, 3, 5), "amount": 8400},
                    {"customer_id": "acme_005", "payment_date": date(2024, 4, 5), "amount": 8600},
                ],
            },
            date(2024, 1, 1): {
                "spend": {"amount": 172000},
                "trade": {"sharing_percentage": 0.35, "cash_cap": 205000.0},
                "payments": [
                    {"customer_id": "acme_006", "payment_date": date(2024, 1, 15), "amount": 5000},
                    {"customer_id": "acme_006", "payment_date": date(2024, 2, 15), "amount": 4800},
                    {"customer_id": "acme_006", "payment_date": date(2024, 3, 15), "amount": 5200},
                    {"customer_id": "acme_006", "payment_date": date(2024, 4, 15), "amount": 4900},
                    {"customer_id": "acme_007", "payment_date": date(2024, 1, 20), "amount": 7000},
                    {"customer_id": "acme_007", "payment_date": date(2024, 2, 20), "amount": 6800},
                    {"customer_id": "acme_007", "payment_date": date(2024, 3, 20), "amount": 7200},
                ],
            },
            date(2024, 2, 1): {
                "spend": {"amount": 195000},
                "trade": {"sharing_percentage": 0.40, "cash_cap": 240000.0},
                "payments": [
                    {"customer_id": "acme_008", "payment_date": date(2024, 2, 10), "amount": 9500},
                    {"customer_id": "acme_008", "payment_date": date(2024, 3, 10), "amount": 9200},
                    {"customer_id": "acme_008", "payment_date": date(2024, 4, 10), "amount": 9800},
                    {"customer_id": "acme_009", "payment_date": date(2024, 2, 25), "amount": 6500},
                    {"customer_id": "acme_009", "payment_date": date(2024, 3, 25), "amount": 6300},
                    {"customer_id": "acme_009", "payment_date": date(2024, 4, 25), "amount": 6700},
                ],
            },
            date(2024, 3, 1): {
                "spend": {"amount": 175000},
                "trade": {"sharing_percentage": 0.32, "cash_cap": 215000.0},
                "payments": [
                    {"customer_id": "acme_010", "payment_date": date(2024, 3, 8), "amount": 4800},
                    {"customer_id": "acme_010", "payment_date": date(2024, 4, 8), "amount": 4600},
                    {"customer_id": "acme_010", "payment_date": date(2024, 5, 8), "amount": 4900},
                ],
            },
            date(2024, 4, 1): {
                "spend": {"amount": 188000},
                "trade": {"sharing_percentage": 0.38, "cash_cap": 235000.0},
                "payments": [
                    {"customer_id": "acme_011", "payment_date": date(2024, 4, 12), "amount": 6200},
                    {"customer_id": "acme_011", "payment_date": date(2024, 5, 12), "amount": 5900},
                    {"customer_id": "acme_012", "payment_date": date(2024, 4, 18), "amount": 8700},
                    {"customer_id": "acme_012", "payment_date": date(2024, 5, 18), "amount": 8400},
                ],
            },
            date(2024, 5, 1): {
                "spend": {"amount": 192000},
                "trade": {"sharing_percentage": 0.36, "cash_cap": 240000.0},
                "payments": [
                    {"customer_id": "acme_013", "payment_date": date(2024, 5, 8), "amount": 5500},
                    {"customer_id": "acme_014", "payment_date": date(2024, 5, 25), "amount": 7800},
                ],
            },
        },
    },
    "TechStart Inc": {
        "threshold": [
            {"payment_period_month": 0, "minimum_payment_percent": 0.20},
            {"payment_period_month": 2, "minimum_payment_percent": 0.30},
            {"payment_period_month": 4, "minimum_payment_percent": 0.05},
        ],
        "monthly_data": {
            date(2023, 11, 1): {
                "spend": {"amount": 82000},
                "trade": {"sharing_percentage": 0.40, "cash_cap": 115000.0},
                "payments": [
                    {"customer_id": "tech_001", "payment_date": date(2023, 11, 10), "amount": 3500},
                    {"customer_id": "tech_001", "payment_date": date(2023, 12, 10), "amount": 3300},
                    {"customer_id": "tech_001", "payment_date": date(2024, 1, 10), "amount": 3600},
                    {"customer_id": "tech_001", "payment_date": date(2024, 2, 10), "amount": 3400},
                    {"customer_id": "tech_001", "payment_date": date(2024, 3, 10), "amount": 3550},
                    {"customer_id": "tech_002", "payment_date": date(2023, 11, 15), "amount": 2800},
                    {"customer_id": "tech_002", "payment_date": date(2023, 12, 15), "amount": 2600},
                    {"customer_id": "tech_002", "payment_date": date(2024, 1, 15), "amount": 2900},
                    {"customer_id": "tech_002", "payment_date": date(2024, 2, 15), "amount": 2750},
                ],
            },
            date(2023, 12, 1): {
                "spend": {"amount": 95000},
                "trade": {"sharing_percentage": 0.42, "cash_cap": 125000.0},
                "payments": [
                    {"customer_id": "tech_003", "payment_date": date(2023, 12, 5), "amount": 4200},
                    {"customer_id": "tech_003", "payment_date": date(2024, 1, 5), "amount": 4000},
                    {"customer_id": "tech_003", "payment_date": date(2024, 2, 5), "amount": 4400},
                    {"customer_id": "tech_003", "payment_date": date(2024, 3, 5), "amount": 4100},
                ],
            },
            date(2024, 1, 1): {
                "spend": {"amount": 78000},
                "trade": {"sharing_percentage": 0.45, "cash_cap": 110000.0},
                "payments": [
                    {"customer_id": "tech_004", "payment_date": date(2024, 1, 12), "amount": 3000},
                    {"customer_id": "tech_004", "payment_date": date(2024, 2, 12), "amount": 2850},
                    {"customer_id": "tech_004", "payment_date": date(2024, 3, 12), "amount": 3100},
                    {"customer_id": "tech_004", "payment_date": date(2024, 4, 12), "amount": 2950},
                    {"customer_id": "tech_005", "payment_date": date(2024, 1, 18), "amount": 5200},
                    {"customer_id": "tech_005", "payment_date": date(2024, 2, 18), "amount": 5000},
                    {"customer_id": "tech_005", "payment_date": date(2024, 3, 18), "amount": 5400},
                ],
            },
            date(2024, 2, 1): {
                "spend": {"amount": 91000},
                "trade": {"sharing_percentage": 0.42, "cash_cap": 130000.0},
                "payments": [
                    {"customer_id": "tech_006", "payment_date": date(2024, 2, 8), "amount": 3800},
                    {"customer_id": "tech_006", "payment_date": date(2024, 3, 8), "amount": 3600},
                    {"customer_id": "tech_006", "payment_date": date(2024, 4, 8), "amount": 3900},
                ],
            },
            date(2024, 3, 1): {
                "spend": {"amount": 86000},
                "trade": {"sharing_percentage": 0.44, "cash_cap": 120000.0},
                "payments": [
                    {"customer_id": "tech_007", "payment_date": date(2024, 3, 15), "amount": 4500},
                    {"customer_id": "tech_007", "payment_date": date(2024, 4, 15), "amount": 4300},
                    {"customer_id": "tech_007", "payment_date": date(2024, 5, 15), "amount": 4700},
                    {"customer_id": "tech_008", "payment_date": date(2024, 3, 22), "amount": 2900},
                    {"customer_id": "tech_008", "payment_date": date(2024, 4, 22), "amount": 2750},
                ],
            },
            date(2024, 4, 1): {
                "spend": {"amount": 88000},
                "trade": {"sharing_percentage": 0.43, "cash_cap": 115000.0},
                "payments": [
                    {"customer_id": "tech_009", "payment_date": date(2024, 4, 10), "amount": 3200},
                    {"customer_id": "tech_009", "payment_date": date(2024, 5, 10), "amount": 3100},
                    {"customer_id": "tech_010", "payment_date": date(2024, 4, 20), "amount": 4100},
                ],
            },
            date(2024, 5, 1): {"spend": {"amount": 85000}, "trade": None, "payments": [
                    {"customer_id": "tech_011", "payment_date": date(2024, 5, 10), "amount": 3200},
                    {"customer_id": "tech_012", "payment_date": date(2024, 6, 10), "amount": 3100},
                    {"customer_id": "tech_012", "payment_date": date(2024, 7, 20), "amount": 4100},
                ]},
        },
    },
    "GrowthCo": {
        "threshold": [
            {"payment_period_month": 1, "minimum_payment_percent": 0.12},
            {"payment_period_month": 3, "minimum_payment_percent": 0.17},
            {"payment_period_month": 6, "minimum_payment_percent": 0.2},
            {"payment_period_month": 12, "minimum_payment_percent": 0.3},
        ],
        "monthly_data": {
            date(2023, 10, 1): {"spend": {"amount": 335000}, "trade": None, "payments": [
                    {"customer_id": "growth_101", "payment_date": date(2024, 1, 8), "amount": 12000},
                    {"customer_id": "growth_101", "payment_date": date(2024, 2, 8), "amount": 11800},
                    {"customer_id": "growth_101", "payment_date": date(2024, 3, 8), "amount": 12300},
                    {"customer_id": "growth_102", "payment_date": date(2024, 1, 15), "amount": 18500},
                    {"customer_id": "growth_102", "payment_date": date(2024, 2, 15), "amount": 18200},
                    {"customer_id": "growth_102", "payment_date": date(2024, 3, 15), "amount": 18800},
                ]},
            date(2023, 11, 1): {"spend": {"amount": 315000}, "trade": None, "payments": [
                    {"customer_id": "growth_103", "payment_date": date(2024, 2, 5), "amount": 16500},
                    {"customer_id": "growth_103", "payment_date": date(2024, 3, 5), "amount": 16200},
                    {"customer_id": "growth_103", "payment_date": date(2024, 4, 5), "amount": 16800},
                    {"customer_id": "growth_104", "payment_date": date(2024, 2, 20), "amount": 24000},
                    {"customer_id": "growth_104", "payment_date": date(2024, 3, 20), "amount": 23500},
                ]},
            date(2023, 12, 1): {
                "spend": {"amount": 298000},
                "trade": {"sharing_percentage": 0.8, "cash_cap": 370000.0},
                "payments": [
                    {"customer_id": "growth_001", "payment_date": date(2023, 12, 12), "amount": 15000},
                    {"customer_id": "growth_001", "payment_date": date(2024, 1, 12), "amount": 14500},
                    {"customer_id": "growth_001", "payment_date": date(2024, 2, 12), "amount": 55500},
                    {"customer_id": "growth_001", "payment_date": date(2024, 3, 12), "amount": 54800},
                    {"customer_id": "growth_001", "payment_date": date(2024, 4, 12), "amount": 15200},
                    {"customer_id": "growth_002", "payment_date": date(2023, 12, 18), "amount": 72000},
                    {"customer_id": "growth_002", "payment_date": date(2024, 1, 18), "amount": 51500},
                    {"customer_id": "growth_002", "payment_date": date(2024, 2, 18), "amount": 32800},
                    {"customer_id": "growth_002", "payment_date": date(2024, 3, 18), "amount": 92200},
                ],
            },
            date(2024, 1, 1): {
                "spend": {"amount": 342000},
                "trade": {"sharing_percentage": 0.30, "cash_cap": 425000.0},
                "payments": [
                    {"customer_id": "growth_003", "payment_date": date(2024, 1, 8), "amount": 18000},
                    {"customer_id": "growth_003", "payment_date": date(2024, 2, 8), "amount": 17500},
                    {"customer_id": "growth_003", "payment_date": date(2024, 3, 8), "amount": 18500},
                    {"customer_id": "growth_003", "payment_date": date(2024, 4, 8), "amount": 18200},
                    {"customer_id": "growth_004", "payment_date": date(2024, 1, 25), "amount": 28000},
                    {"customer_id": "growth_004", "payment_date": date(2024, 2, 25), "amount": 27200},
                    {"customer_id": "growth_004", "payment_date": date(2024, 3, 25), "amount": 88800},
                ],
            },
            date(2024, 2, 1): {
                "spend": {"amount": 325000},
                "trade": {"sharing_percentage": 0.70, "cash_cap": 400000.0},
                "payments": [
                    {"customer_id": "growth_005", "payment_date": date(2024, 2, 12), "amount": 25000},
                    {"customer_id": "growth_005", "payment_date": date(2024, 3, 12), "amount": 24500},
                    {"customer_id": "growth_005", "payment_date": date(2024, 4, 12), "amount": 25800},
                    {"customer_id": "growth_006", "payment_date": date(2024, 2, 20), "amount": 79500},
                    {"customer_id": "growth_006", "payment_date": date(2024, 3, 20), "amount": 19000},
                    {"customer_id": "growth_006", "payment_date": date(2024, 4, 20), "amount": 470000},
                    {"customer_id": "growth_005", "payment_date": date(2024, 5, 12), "amount": 325800},
                    {"customer_id": "growth_006", "payment_date": date(2024, 6, 20), "amount": 279500},
                    {"customer_id": "growth_006", "payment_date": date(2024, 7, 20), "amount": 119000},
                    {"customer_id": "growth_006", "payment_date": date(2024, 8, 20), "amount": 170000},
                ],
            },
            date(2024, 3, 1): {
                "spend": {"amount": 358000},
                "trade": {"sharing_percentage": 0.8, "cash_cap": 450000.0},
                "payments": [
                    {"customer_id": "growth_007", "payment_date": date(2024, 3, 10), "amount": 32000},
                    {"customer_id": "growth_007", "payment_date": date(2024, 4, 10), "amount": 31500},
                    {"customer_id": "growth_007", "payment_date": date(2024, 5, 10), "amount": 33000},
                    {"customer_id": "growth_008", "payment_date": date(2024, 3, 28), "amount": 16500},
                    {"customer_id": "growth_008", "payment_date": date(2024, 4, 28), "amount": 16200},
                    {"customer_id": "growth_007", "payment_date": date(2024, 6, 10), "amount": 133000},
                    {"customer_id": "growth_008", "payment_date": date(2024, 7, 28), "amount": 16500},
                    {"customer_id": "growth_008", "payment_date": date(2024, 8, 28), "amount": 216200},
                    {"customer_id": "growth_007", "payment_date": date(2024, 8, 10), "amount": 333000},
                    {"customer_id": "growth_008", "payment_date": date(2024, 10, 28), "amount": 16500},
                    {"customer_id": "growth_008", "payment_date": date(2024, 10, 28), "amount": 316200},
                ],
            },
            date(2024, 4, 1): {
                "spend": {"amount": 310000},
                "trade": {"sharing_percentage": 0.86, "cash_cap": 385000.0},
                "payments": [
                    {"customer_id": "growth_009", "payment_date": date(2024, 4, 8), "amount": 24000},
                    {"customer_id": "growth_009", "payment_date": date(2024, 5, 8), "amount": 23500},
                    {"customer_id": "growth_010", "payment_date": date(2024, 4, 15), "amount": 18500},
                    {"customer_id": "growth_010", "payment_date": date(2024, 5, 15), "amount": 18200},
                    {"customer_id": "growth_011", "payment_date": date(2024, 4, 22), "amount": 30000},
                ],
            },
            date(2024, 5, 1): {"spend": {"amount": 320000}, "trade": None, "payments": [
                    {"customer_id": "growth_012", "payment_date": date(2024, 5, 10), "amount": 28000},
                    {"customer_id": "growth_012", "payment_date": date(2024, 6, 10), "amount": 27500},
                    {"customer_id": "growth_013", "payment_date": date(2024, 5, 25), "amount": 91000},
                    {"customer_id": "growth_013", "payment_date": date(2024, 6, 25), "amount": 40800},
                    {"customer_id": "growth_014", "payment_date": date(2024, 5, 18), "amount": 95000},
                    {"customer_id": "growth_014", "payment_date": date(2024, 5, 19), "amount": 95000},
                    {"customer_id": "growth_014", "payment_date": date(2024, 5, 12), "amount": 95000},
                    {"customer_id": "growth_014", "payment_date": date(2024, 5, 13), "amount": 95000},
                ]},
        },
    },
    "DataDriven Solutions": {
        "threshold": [
            {"payment_period_month": 0, "minimum_payment_percent": 0.18},
            {"payment_period_month": 2, "minimum_payment_percent": 0.35},
            {"payment_period_month": 6, "minimum_payment_percent": 0.10},
        ],
        "monthly_data": {
            date(2023, 10, 1): {"spend": {"amount": 168000}, "trade": None, 
                "payments": [
                    {"customer_id": "data_011", "payment_date": date(2024, 1, 12), "amount": 4500},
                    {"customer_id": "data_011", "payment_date": date(2024, 2, 12), "amount": 4300},
                    {"customer_id": "data_012", "payment_date": date(2024, 1, 20), "amount": 6200},
                    {"customer_id": "data_012", "payment_date": date(2024, 2, 20), "amount": 6000},
                    {"customer_id": "data_012", "payment_date": date(2024, 3, 20), "amount": 6400},
                ]
            },
            date(2023, 11, 1): {"spend": {"amount": 125000}, "trade": None, 
                                "payments": [
                    {"customer_id": "data_021", "payment_date": date(2024, 1, 12), "amount": 500},
                    {"customer_id": "data_021", "payment_date": date(2024, 2, 12), "amount": 300},
                    {"customer_id": "data_022", "payment_date": date(2024, 1, 20), "amount": 200},
                    {"customer_id": "data_022", "payment_date": date(2024, 2, 20), "amount": 100},
                    {"customer_id": "data_022", "payment_date": date(2024, 3, 20), "amount": 2400},
                ]},
            date(2023, 12, 1): {"spend": {"amount": 144000}, "trade": None, "payments": [
                    {"customer_id": "data_031", "payment_date": date(2024, 3, 8), "amount": 3200},
                    {"customer_id": "data_031", "payment_date": date(2024, 4, 8), "amount": 3100},
                    {"customer_id": "data_031", "payment_date": date(2024, 5, 8), "amount": 3300},
                    {"customer_id": "data_032", "payment_date": date(2024, 3, 15), "amount": 5800},
                    {"customer_id": "data_032", "payment_date": date(2024, 4, 15), "amount": 5600},
                ]},
            date(2024, 1, 1): {
                "spend": {"amount": 162000},
                "trade": {"sharing_percentage": 0.38, "cash_cap": 195000.0},
                "payments": [
                    {"customer_id": "data_001", "payment_date": date(2024, 1, 12), "amount": 4500},
                    {"customer_id": "data_001", "payment_date": date(2024, 2, 12), "amount": 4300},
                    {"customer_id": "data_002", "payment_date": date(2024, 1, 20), "amount": 6200},
                    {"customer_id": "data_002", "payment_date": date(2024, 2, 20), "amount": 6000},
                    {"customer_id": "data_002", "payment_date": date(2024, 3, 20), "amount": 6400},
                ],
            },
            date(2024, 2, 1): {
                "spend": {"amount": 138000},
                "trade": {"sharing_percentage": 0.40, "cash_cap": 175000.0},
                "payments": [
                    {"customer_id": "data_003", "payment_date": date(2024, 2, 8), "amount": 5800},
                    {"customer_id": "data_003", "payment_date": date(2024, 3, 8), "amount": 5600},
                    {"customer_id": "data_003", "payment_date": date(2024, 4, 8), "amount": 5950},
                ],
            },
            date(2024, 3, 1): {
                "spend": {"amount": 155000},
                "trade": {"sharing_percentage": 0.35, "cash_cap": 190000.0},
                "payments": [
                    {"customer_id": "data_005", "payment_date": date(2024, 3, 10), "amount": 5200},
                    {"customer_id": "data_005", "payment_date": date(2024, 4, 10), "amount": 5000},
                    {"customer_id": "data_005", "payment_date": date(2024, 5, 10), "amount": 5400},
                ],
            },
            date(2024, 4, 1): {
                "spend": {"amount": 118000},
                "trade": {"sharing_percentage": 0.42, "cash_cap": 155000.0},
                "payments": [
                    {"customer_id": "data_006", "payment_date": date(2024, 4, 5), "amount": 7500},
                    {"customer_id": "data_006", "payment_date": date(2024, 5, 5), "amount": 7300},
                    {"customer_id": "data_007", "payment_date": date(2024, 4, 18), "amount": 4800},
                    {"customer_id": "data_007", "payment_date": date(2024, 5, 18), "amount": 4600},
                    {"customer_id": "data_008", "payment_date": date(2024, 4, 25), "amount": 6200},
                ],
            },
            date(2024, 5, 1): {"spend": {"amount": 132000}, "trade": None, "payments": [
                    {"customer_id": "data_009", "payment_date": date(2024, 5, 12), "amount": 4800},
                    {"customer_id": "data_009", "payment_date": date(2024, 6, 12), "amount": 4600},
                    {"customer_id": "data_010", "payment_date": date(2024, 5, 20), "amount": 6200},
                    {"customer_id": "data_010", "payment_date": date(2024, 6, 20), "amount": 6000},
                    {"customer_id": "data_010", "payment_date": date(2024, 7, 20), "amount": 6400},
                ]},
        },
    },
    "CloudFirst Technologies": {
        "threshold": [
            {"payment_period_month": 1, "minimum_payment_percent": 0.14},
            {"payment_period_month": 3, "minimum_payment_percent": 0.32},
            {"payment_period_month": 9, "minimum_payment_percent": 0.20},
        ],
        "monthly_data": {
            date(2023, 10, 1): {"spend": {"amount": 245000}, "trade": None, "payments": [
                    {"customer_id": "cloud_011", "payment_date": date(2024, 1, 12), "amount": 8800},
                    {"customer_id": "cloud_011", "payment_date": date(2024, 2, 12), "amount": 8500},
                    {"customer_id": "cloud_011", "payment_date": date(2024, 3, 12), "amount": 8900},
                    {"customer_id": "cloud_012", "payment_date": date(2024, 1, 20), "amount": 12200},
                    {"customer_id": "cloud_012", "payment_date": date(2024, 2, 20), "amount": 11900},
                ]},
            date(2023, 11, 1): {"spend": {"amount": 218000}, "trade": None, "payments": [
                    {"customer_id": "cloud_013", "payment_date": date(2024, 2, 8), "amount": 9500},
                    {"customer_id": "cloud_013", "payment_date": date(2024, 3, 8), "amount": 9200},
                    {"customer_id": "cloud_013", "payment_date": date(2024, 4, 8), "amount": 9800},
                    {"customer_id": "cloud_014", "payment_date": date(2024, 2, 15), "amount": 11800},
                    {"customer_id": "cloud_014", "payment_date": date(2024, 3, 15), "amount": 11500},
                    {"customer_id": "cloud_014", "payment_date": date(2024, 4, 15), "amount": 12000},
                ]},
            date(2023, 12, 1): {
                "spend": {"amount": 195000},
                "trade": {"sharing_percentage": 0.33, "cash_cap": 245000.0},
                "payments": [
                    {"customer_id": "cloud_001", "payment_date": date(2023, 12, 10), "amount": 8500},
                    {"customer_id": "cloud_001", "payment_date": date(2024, 1, 10), "amount": 8200},
                    {"customer_id": "cloud_001", "payment_date": date(2024, 2, 10), "amount": 8800},
                    {"customer_id": "cloud_002", "payment_date": date(2023, 12, 25), "amount": 12000},
                    {"customer_id": "cloud_002", "payment_date": date(2024, 1, 25), "amount": 11700},
                ],
            },
            date(2024, 1, 1): {
                "spend": {"amount": 268000},
                "trade": {"sharing_percentage": 0.36, "cash_cap": 325000.0},
                "payments": [
                    {"customer_id": "cloud_003", "payment_date": date(2024, 1, 15), "amount": 9800},
                    {"customer_id": "cloud_003", "payment_date": date(2024, 2, 15), "amount": 9500},
                    {"customer_id": "cloud_003", "payment_date": date(2024, 3, 15), "amount": 10100},
                ],
            },
            date(2024, 2, 1): {
                "spend": {"amount": 212000},
                "trade": {"sharing_percentage": 0.34, "cash_cap": 270000.0},
                "payments": [
                    {"customer_id": "cloud_005", "payment_date": date(2024, 2, 8), "amount": 7800},
                    {"customer_id": "cloud_005", "payment_date": date(2024, 3, 8), "amount": 7600},
                    {"customer_id": "cloud_005", "payment_date": date(2024, 4, 8), "amount": 8000},
                ],
            },
            date(2024, 3, 1): {
                "spend": {"amount": 238000},
                "trade": {"sharing_percentage": 0.38, "cash_cap": 295000.0},
                "payments": [
                    {"customer_id": "cloud_007", "payment_date": date(2024, 3, 12), "amount": 13500},
                    {"customer_id": "cloud_007", "payment_date": date(2024, 4, 12), "amount": 13200},
                    {"customer_id": "cloud_007", "payment_date": date(2024, 5, 12), "amount": 13800},
                    {"customer_id": "cloud_008", "payment_date": date(2024, 3, 18), "amount": 10500},
                    {"customer_id": "cloud_008", "payment_date": date(2024, 4, 18), "amount": 10200},
                    {"customer_id": "cloud_008", "payment_date": date(2024, 5, 18), "amount": 10800},
                    {"customer_id": "cloud_009", "payment_date": date(2024, 3, 25), "amount": 14500},
                    {"customer_id": "cloud_009", "payment_date": date(2024, 4, 25), "amount": 14200},
                ],
            },
            date(2024, 4, 1): {"spend": {"amount": 225000}, "trade": None, "payments": [
                    {"customer_id": "cloud_015", "payment_date": date(2024, 4, 10), "amount": 10500},
                    {"customer_id": "cloud_015", "payment_date": date(2024, 5, 10), "amount": 10200},
                    {"customer_id": "cloud_015", "payment_date": date(2024, 6, 10), "amount": 10800},
                    {"customer_id": "cloud_016", "payment_date": date(2024, 4, 25), "amount": 14000},
                    {"customer_id": "cloud_016", "payment_date": date(2024, 5, 25), "amount": 13700},
                ]},
            date(2024, 5, 1): {"spend": {"amount": 242000}, "trade": None, "payments": [
                    {"customer_id": "cloud_017", "payment_date": date(2024, 5, 8), "amount": 11500},
                    {"customer_id": "cloud_017", "payment_date": date(2024, 6, 8), "amount": 11200},
                    {"customer_id": "cloud_017", "payment_date": date(2024, 7, 8), "amount": 11800},
                    {"customer_id": "cloud_018", "payment_date": date(2024, 5, 18), "amount": 15200},
                    {"customer_id": "cloud_018", "payment_date": date(2024, 6, 18), "amount": 14900},
                    {"customer_id": "cloud_019", "payment_date": date(2024, 5, 28), "amount": 8900},
                ]},
        },
    },
    "AI Innovations Ltd": {
        "threshold": [
            {"payment_period_month": 0, "minimum_payment_percent": 0.22},
            {"payment_period_month": 3, "minimum_payment_percent": 0.40},
            {"payment_period_month": 6, "minimum_payment_percent": 0.25},
        ],
        "monthly_data": {
            date(2023, 10, 1): {"spend": {"amount": 185000}, "trade": None, "payments": [
                    {"customer_id": "ai_011", "payment_date": date(2024, 1, 10), "amount": 7200},
                    {"customer_id": "ai_011", "payment_date": date(2024, 2, 10), "amount": 7000},
                    {"customer_id": "ai_011", "payment_date": date(2024, 3, 10), "amount": 7400},
                    {"customer_id": "ai_012", "payment_date": date(2024, 1, 18), "amount": 10500},
                    {"customer_id": "ai_012", "payment_date": date(2024, 2, 18), "amount": 10200},
                ]},
            date(2023, 11, 1): {"spend": {"amount": 225000}, "trade": None, "payments": [
                    {"customer_id": "ai_013", "payment_date": date(2024, 2, 5), "amount": 9800},
                    {"customer_id": "ai_013", "payment_date": date(2024, 3, 5), "amount": 9500},
                    {"customer_id": "ai_013", "payment_date": date(2024, 4, 5), "amount": 10100},
                    {"customer_id": "ai_014", "payment_date": date(2024, 2, 12), "amount": 13500},
                    {"customer_id": "ai_014", "payment_date": date(2024, 3, 12), "amount": 13200},
                    {"customer_id": "ai_014", "payment_date": date(2024, 4, 12), "amount": 13800},
                ]},
            date(2023, 12, 1): {"spend": {"amount": 168000}, "trade": None, "payments": [
                    {"customer_id": "ai_015", "payment_date": date(2024, 3, 8), "amount": 6800},
                    {"customer_id": "ai_015", "payment_date": date(2024, 4, 8), "amount": 6500},
                    {"customer_id": "ai_015", "payment_date": date(2024, 5, 8), "amount": 6900},
                    {"customer_id": "ai_016", "payment_date": date(2024, 3, 20), "amount": 8200},
                    {"customer_id": "ai_016", "payment_date": date(2024, 4, 20), "amount": 8000},
                ]},
            date(2024, 1, 1): {
                "spend": {"amount": 235000},
                "trade": {"sharing_percentage": 0.41, "cash_cap": 290000.0},
                "payments": [
                    {"customer_id": "ai_001", "payment_date": date(2024, 1, 15), "amount": 8500},
                    {"customer_id": "ai_001", "payment_date": date(2024, 2, 15), "amount": 8200},
                    {"customer_id": "ai_001", "payment_date": date(2024, 3, 15), "amount": 8800},
                    {"customer_id": "ai_002", "payment_date": date(2024, 1, 22), "amount": 12500},
                    {"customer_id": "ai_002", "payment_date": date(2024, 2, 22), "amount": 12200},
                ],
            },
            date(2024, 2, 1): {
                "spend": {"amount": 178000},
                "trade": {"sharing_percentage": 0.39, "cash_cap": 220000.0},
                "payments": [
                    {"customer_id": "ai_003", "payment_date": date(2024, 2, 10), "amount": 6800},
                    {"customer_id": "ai_003", "payment_date": date(2024, 3, 10), "amount": 6500},
                    {"customer_id": "ai_003", "payment_date": date(2024, 4, 10), "amount": 6900},
                    {"customer_id": "ai_004", "payment_date": date(2024, 2, 25), "amount": 9200},
                    {"customer_id": "ai_004", "payment_date": date(2024, 3, 25), "amount": 8900},
                ],
            },
            date(2024, 3, 1): {
                "spend": {"amount": 198000},
                "trade": {"sharing_percentage": 0.43, "cash_cap": 245000.0},
                "payments": [
                    {"customer_id": "ai_005", "payment_date": date(2024, 3, 8), "amount": 7500},
                    {"customer_id": "ai_005", "payment_date": date(2024, 4, 8), "amount": 7200},
                    {"customer_id": "ai_005", "payment_date": date(2024, 5, 8), "amount": 7800},
                    {"customer_id": "ai_006", "payment_date": date(2024, 3, 18), "amount": 11200},
                    {"customer_id": "ai_006", "payment_date": date(2024, 4, 18), "amount": 10900},
                ],
            },
            date(2024, 4, 1): {"spend": {"amount": 205000}, "trade": None, "payments": [
                    {"customer_id": "ai_007", "payment_date": date(2024, 4, 12), "amount": 8500},
                    {"customer_id": "ai_007", "payment_date": date(2024, 5, 12), "amount": 8200},
                    {"customer_id": "ai_007", "payment_date": date(2024, 6, 12), "amount": 8800},
                    {"customer_id": "ai_008", "payment_date": date(2024, 4, 22), "amount": 11800},
                    {"customer_id": "ai_008", "payment_date": date(2024, 5, 22), "amount": 11500},
                ]},
            date(2024, 5, 1): {"spend": {"amount": 192000}, "trade": None, "payments": [
                    {"customer_id": "ai_009", "payment_date": date(2024, 5, 8), "amount": 7800},
                    {"customer_id": "ai_009", "payment_date": date(2024, 6, 8), "amount": 7500},
                    {"customer_id": "ai_009", "payment_date": date(2024, 7, 8), "amount": 7900},
                    {"customer_id": "ai_010", "payment_date": date(2024, 5, 25), "amount": 10200},
                    {"customer_id": "ai_010", "payment_date": date(2024, 6, 25), "amount": 9900},
                ]},
        },
    },
    "ScaleUp Ventures": {
        "threshold": [
            {"payment_period_month": 1, "minimum_payment_percent": 0.16},
            {"payment_period_month": 4, "minimum_payment_percent": 0.42},
            {"payment_period_month": 8, "minimum_payment_percent": 0.12},
        ],
        "monthly_data": {
            date(2023, 10, 1): {"spend": {"amount": 125000}, "trade": None, "payments": []},
            date(2023, 11, 1): {
                "spend": {"amount": 95000},
                "trade": {"sharing_percentage": 0.35, "cash_cap": 125000.0},
                "payments": [
                    {"customer_id": "scale_001", "payment_date": date(2023, 11, 12), "amount": 3800},
                    {"customer_id": "scale_001", "payment_date": date(2023, 12, 12), "amount": 3600},
                    {"customer_id": "scale_001", "payment_date": date(2024, 1, 12), "amount": 3900},
                    {"customer_id": "scale_002", "payment_date": date(2023, 11, 25), "amount": 2900},
                    {"customer_id": "scale_002", "payment_date": date(2023, 12, 25), "amount": 2800},
                ],
            },
            date(2023, 12, 1): {"spend": {"amount": 148000}, "trade": None, "payments": [
                    {"customer_id": "scale_013", "payment_date": date(2024, 3, 5), "amount": 4500},
                    {"customer_id": "scale_013", "payment_date": date(2024, 4, 5), "amount": 4300},
                    {"customer_id": "scale_013", "payment_date": date(2024, 5, 5), "amount": 4700},
                    {"customer_id": "scale_014", "payment_date": date(2024, 3, 18), "amount": 3600},
                    {"customer_id": "scale_014", "payment_date": date(2024, 4, 18), "amount": 3500},
                ]},
            date(2024, 1, 1): {
                "spend": {"amount": 108000},
                "trade": {"sharing_percentage": 0.37, "cash_cap": 140000.0},
                "payments": [
                    {"customer_id": "scale_003", "payment_date": date(2024, 1, 15), "amount": 4200},
                    {"customer_id": "scale_003", "payment_date": date(2024, 2, 15), "amount": 4000},
                    {"customer_id": "scale_004", "payment_date": date(2024, 1, 28), "amount": 3100},
                ],
            },
            date(2024, 2, 1): {
                "spend": {"amount": 88000},
                "trade": {"sharing_percentage": 0.40, "cash_cap": 115000.0},
                "payments": [
                    {"customer_id": "scale_005", "payment_date": date(2024, 2, 8), "amount": 3500},
                    {"customer_id": "scale_005", "payment_date": date(2024, 3, 8), "amount": 3300},
                    {"customer_id": "scale_005", "payment_date": date(2024, 4, 8), "amount": 3700},
                ],
            },
            date(2024, 3, 1): {
                "spend": {"amount": 132000},
                "trade": {"sharing_percentage": 0.41, "cash_cap": 165000.0},
                "payments": [
                    {"customer_id": "scale_006", "payment_date": date(2024, 3, 10), "amount": 5200},
                    {"customer_id": "scale_006", "payment_date": date(2024, 4, 10), "amount": 5000},
                    {"customer_id": "scale_006", "payment_date": date(2024, 5, 10), "amount": 5400},
                    {"customer_id": "scale_007", "payment_date": date(2024, 3, 22), "amount": 4800},
                    {"customer_id": "scale_007", "payment_date": date(2024, 4, 22), "amount": 4600},
                ],
            },
            date(2024, 4, 1): {"spend": {"amount": 98000}, "trade": None, "payments": []},
            date(2024, 5, 1): {"spend": {"amount": 115000}, "trade": None, "payments": []},
        },
    },
    "FinTech Masters": {
        "threshold": [
            {"payment_period_month": 0, "minimum_payment_percent": 0.10},
            {"payment_period_month": 2, "minimum_payment_percent": 0.25},
            {"payment_period_month": 6, "minimum_payment_percent": 0.25},
            {"payment_period_month": 12, "minimum_payment_percent": 0.25},
        ],
        "monthly_data": {
            date(2023, 10, 1): {"spend": {"amount": 315000}, "trade": None, "payments": []},
            date(2023, 11, 1): {"spend": {"amount": 268000}, "trade": None, "payments": []},
            date(2023, 12, 1): {"spend": {"amount": 295000}, "trade": None, "payments": []},
            date(2024, 1, 1): {
                "spend": {"amount": 342000},
                "trade": {"sharing_percentage": 0.28, "cash_cap": 425000.0},
                "payments": [
                    {"customer_id": "fintech_001", "payment_date": date(2024, 1, 10), "amount": 25000},
                    {"customer_id": "fintech_001", "payment_date": date(2024, 2, 10), "amount": 24500},
                    {"customer_id": "fintech_001", "payment_date": date(2024, 3, 10), "amount": 25500},
                    {"customer_id": "fintech_002", "payment_date": date(2024, 1, 20), "amount": 35000},
                    {"customer_id": "fintech_002", "payment_date": date(2024, 2, 20), "amount": 34200},
                ],
            },
            date(2024, 2, 1): {
                "spend": {"amount": 288000},
                "trade": {"sharing_percentage": 0.30, "cash_cap": 360000.0},
                "payments": [
                    {"customer_id": "fintech_003", "payment_date": date(2024, 2, 8), "amount": 18500},
                    {"customer_id": "fintech_003", "payment_date": date(2024, 3, 8), "amount": 18200},
                    {"customer_id": "fintech_003", "payment_date": date(2024, 4, 8), "amount": 18800},
                    {"customer_id": "fintech_004", "payment_date": date(2024, 2, 25), "amount": 28000},
                    {"customer_id": "fintech_004", "payment_date": date(2024, 3, 25), "amount": 27500},
                ],
            },
            date(2024, 3, 1): {
                "spend": {"amount": 325000},
                "trade": {"sharing_percentage": 0.32, "cash_cap": 405000.0},
                "payments": [
                    {"customer_id": "fintech_005", "payment_date": date(2024, 3, 12), "amount": 32000},
                    {"customer_id": "fintech_005", "payment_date": date(2024, 4, 12), "amount": 31500},
                    {"customer_id": "fintech_005", "payment_date": date(2024, 5, 12), "amount": 32800},
                    {"customer_id": "fintech_006", "payment_date": date(2024, 3, 28), "amount": 22500},
                    {"customer_id": "fintech_006", "payment_date": date(2024, 4, 28), "amount": 22000},
                ],
            },
            date(2024, 4, 1): {"spend": {"amount": 278000}, "trade": None, "payments": []},
            date(2024, 5, 1): {"spend": {"amount": 308000}, "trade": None, "payments": []},
        },
    },
    "EcoTech Green": {
        "threshold": [
            {"payment_period_month": 1, "minimum_payment_percent": 0.20},
            {"payment_period_month": 3, "minimum_payment_percent": 0.38},
            {"payment_period_month": 6, "minimum_payment_percent": 0.58},
        ],
        "monthly_data": {
            date(2023, 10, 1): {"spend": {"amount": 88000}, "trade": None, "payments": []},
            date(2023, 11, 1): {"spend": {"amount": 125000}, "trade": None, "payments": []},
            date(2023, 12, 1): {"spend": {"amount": 95000}, "trade": None, "payments": []},
            date(2024, 1, 1): {"spend": {"amount": 118000}, "trade": None, "payments": []},
            date(2024, 2, 1): {
                "spend": {"amount": 132000},
                "trade": {"sharing_percentage": 0.45, "cash_cap": 165000.0},
                "payments": [
                    {"customer_id": "eco_001", "payment_date": date(2024, 2, 12), "amount": 4200},
                    {"customer_id": "eco_001", "payment_date": date(2024, 3, 12), "amount": 4000},
                    {"customer_id": "eco_001", "payment_date": date(2024, 4, 12), "amount": 4400},
                    {"customer_id": "eco_002", "payment_date": date(2024, 2, 25), "amount": 3800},
                ],
            },
            date(2024, 3, 1): {
                "spend": {"amount": 108000},
                "trade": {"sharing_percentage": 0.46, "cash_cap": 135000.0},
                "payments": [
                    {"customer_id": "eco_003", "payment_date": date(2024, 3, 8), "amount": 3500},
                    {"customer_id": "eco_003", "payment_date": date(2024, 4, 8), "amount": 3300},
                    {"customer_id": "eco_003", "payment_date": date(2024, 5, 8), "amount": 3700},
                    {"customer_id": "eco_004", "payment_date": date(2024, 3, 20), "amount": 5200},
                    {"customer_id": "eco_004", "payment_date": date(2024, 4, 20), "amount": 5000},
                ],
            },
            date(2024, 4, 1): {
                "spend": {"amount": 142000},
                "trade": {"sharing_percentage": 0.48, "cash_cap": 180000.0},
                "payments": [
                    {"customer_id": "eco_005", "payment_date": date(2024, 4, 10), "amount": 6800},
                    {"customer_id": "eco_005", "payment_date": date(2024, 5, 10), "amount": 6500},
                    {"customer_id": "eco_006", "payment_date": date(2024, 4, 22), "amount": 4500},
                    {"customer_id": "eco_006", "payment_date": date(2024, 5, 22), "amount": 4300},
                ],
            },
            date(2024, 5, 1): {"spend": {"amount": 98000}, "trade": None, "payments": []},
        },
    },
    "HealthTech Plus": {
        "threshold": [
            {"payment_period_month": 0, "minimum_payment_percent": 0.12},
            {"payment_period_month": 3, "minimum_payment_percent": 0.30},
            {"payment_period_month": 9, "minimum_payment_percent": 0.65},
            {"payment_period_month": 18, "minimum_payment_percent": 0.85},
        ],
        "monthly_data": {
            date(2023, 10, 1): {"spend": {"amount": 185000}, "trade": None, "payments": []},
            date(2023, 11, 1): {"spend": {"amount": 225000}, "trade": None, "payments": []},
            date(2023, 12, 1): {"spend": {"amount": 195000}, "trade": None, "payments": []},
            date(2024, 1, 1): {
                "spend": {"amount": 268000},
                "trade": {"sharing_percentage": 0.34, "cash_cap": 335000.0},
                "payments": [
                    {"customer_id": "health_001", "payment_date": date(2024, 1, 15), "amount": 12500},
                    {"customer_id": "health_001", "payment_date": date(2024, 2, 15), "amount": 12200},
                    {"customer_id": "health_001", "payment_date": date(2024, 3, 15), "amount": 12800},
                    {"customer_id": "health_002", "payment_date": date(2024, 1, 25), "amount": 18500},
                ],
            },
            date(2024, 2, 1): {
                "spend": {"amount": 178000},
                "trade": {"sharing_percentage": 0.36, "cash_cap": 225000.0},
                "payments": [
                    {"customer_id": "health_003", "payment_date": date(2024, 2, 10), "amount": 8200},
                    {"customer_id": "health_003", "payment_date": date(2024, 3, 10), "amount": 8000},
                    {"customer_id": "health_003", "payment_date": date(2024, 4, 10), "amount": 8400},
                    {"customer_id": "health_004", "payment_date": date(2024, 2, 28), "amount": 11500},
                    {"customer_id": "health_004", "payment_date": date(2024, 3, 28), "amount": 11200},
                ],
            },
            date(2024, 3, 1): {
                "spend": {"amount": 232000},
                "trade": {"sharing_percentage": 0.33, "cash_cap": 290000.0},
                "payments": [
                    {"customer_id": "health_005", "payment_date": date(2024, 3, 12), "amount": 15200},
                    {"customer_id": "health_005", "payment_date": date(2024, 4, 12), "amount": 14800},
                    {"customer_id": "health_005", "payment_date": date(2024, 5, 12), "amount": 15600},
                    {"customer_id": "health_006", "payment_date": date(2024, 3, 22), "amount": 9800},
                    {"customer_id": "health_006", "payment_date": date(2024, 4, 22), "amount": 9500},
                ],
            },
            date(2024, 4, 1): {"spend": {"amount": 205000}, "trade": None, "payments": []},
            date(2024, 5, 1): {"spend": {"amount": 215000}, "trade": None, "payments": []},
        },
    },
    "EdTech Revolution": {
        "threshold": [
            {"payment_period_month": 0, "minimum_payment_percent": 0.15},
            {"payment_period_month": 2, "minimum_payment_percent": 0.28},
            {"payment_period_month": 6, "minimum_payment_percent": 0.52},
        ],
        "monthly_data": {
            date(2023, 10, 1): {"spend": {"amount": 118000}, "trade": None, "payments": []},
            date(2023, 11, 1): {"spend": {"amount": 82000}, "trade": None, "payments": []},
            date(2023, 12, 1): {"spend": {"amount": 105000}, "trade": None, "payments": []},
            date(2024, 1, 1): {"spend": {"amount": 88000}, "trade": None, "payments": []},
            date(2024, 2, 1): {"spend": {"amount": 125000}, "trade": None, "payments": []},
            date(2024, 3, 1): {"spend": {"amount": 95000}, "trade": None, "payments": []},
            date(2024, 4, 1): {"spend": {"amount": 108000}, "trade": None, "payments": []},
            date(2024, 5, 1): {"spend": {"amount": 92000}, "trade": None, "payments": []},
        },
    },
    "RetailTech Pro": {
        "threshold": [
            {"payment_period_month": 1, "minimum_payment_percent": 0.18},
            {"payment_period_month": 3, "minimum_payment_percent": 0.35},
            {"payment_period_month": 8, "minimum_payment_percent": 0.62},
        ],
        "monthly_data": {
            date(2023, 10, 1): {"spend": {"amount": 155000}, "trade": None, "payments": []},
            date(2023, 11, 1): {"spend": {"amount": 185000}, "trade": None, "payments": []},
            date(2023, 12, 1): {"spend": {"amount": 142000}, "trade": None, "payments": []},
            date(2024, 1, 1): {"spend": {"amount": 198000}, "trade": None, "payments": []},
            date(2024, 2, 1): {"spend": {"amount": 175000}, "trade": None, "payments": []},
            date(2024, 3, 1): {"spend": {"amount": 132000}, "trade": None, "payments": []},
            date(2024, 4, 1): {"spend": {"amount": 168000}, "trade": None, "payments": []},
            date(2024, 5, 1): {"spend": {"amount": 145000}, "trade": None, "payments": []},
        },
    },
    "SecurityFirst Systems": {
        "threshold": [
            {"payment_period_month": 0, "minimum_payment_percent": 0.20},
            {"payment_period_month": 4, "minimum_payment_percent": 0.45},
            {"payment_period_month": 12, "minimum_payment_percent": 0.75},
        ],
        "monthly_data": {
            date(2023, 10, 1): {"spend": {"amount": 195000}, "trade": None, "payments": []},
            date(2023, 11, 1): {"spend": {"amount": 158000}, "trade": None, "payments": []},
            date(2023, 12, 1): {"spend": {"amount": 212000}, "trade": None, "payments": []},
            date(2024, 1, 1): {"spend": {"amount": 178000}, "trade": None, "payments": []},
            date(2024, 2, 1): {"spend": {"amount": 168000}, "trade": None, "payments": []},
            date(2024, 3, 1): {"spend": {"amount": 185000}, "trade": None, "payments": []},
            date(2024, 4, 1): {"spend": {"amount": 225000}, "trade": None, "payments": []},
            date(2024, 5, 1): {"spend": {"amount": 142000}, "trade": None, "payments": []},
        },
    },
    "MediaStream Networks": {
        "threshold": [
            {"payment_period_month": 1, "minimum_payment_percent": 0.16},
            {"payment_period_month": 3, "minimum_payment_percent": 0.32},
            {"payment_period_month": 6, "minimum_payment_percent": 0.55},
        ],
        "monthly_data": {
            date(2023, 10, 1): {"spend": {"amount": 138000}, "trade": None, "payments": []},
            date(2023, 11, 1): {"spend": {"amount": 175000}, "trade": None, "payments": []},
            date(2023, 12, 1): {"spend": {"amount": 162000}, "trade": None, "payments": []},
            date(2024, 1, 1): {"spend": {"amount": 118000}, "trade": None, "payments": []},
            date(2024, 2, 1): {"spend": {"amount": 145000}, "trade": None, "payments": []},
            date(2024, 3, 1): {"spend": {"amount": 188000}, "trade": None, "payments": []},
            date(2024, 4, 1): {"spend": {"amount": 132000}, "trade": None, "payments": []},
            date(2024, 5, 1): {"spend": {"amount": 168000}, "trade": None, "payments": []},
        },
    },
    "LogisticsPro Solutions": {
        "threshold": [
            {"payment_period_month": 2, "minimum_payment_percent": 0.22},
            {"payment_period_month": 6, "minimum_payment_percent": 0.48},
            {"payment_period_month": 12, "minimum_payment_percent": 0.12},
        ],
        "monthly_data": {
            date(2023, 10, 1): {"spend": {"amount": 125000}, "trade": None, "payments": []},
            date(2023, 11, 1): {"spend": {"amount": 158000}, "trade": None, "payments": []},
            date(2023, 12, 1): {"spend": {"amount": 148000}, "trade": None, "payments": []},
            date(2024, 1, 1): {"spend": {"amount": 165000}, "trade": None, "payments": []},
            date(2024, 2, 1): {"spend": {"amount": 118000}, "trade": None, "payments": []},
            date(2024, 3, 1): {"spend": {"amount": 142000}, "trade": None, "payments": []},
            date(2024, 4, 1): {"spend": {"amount": 132000}, "trade": None, "payments": []},
            date(2024, 5, 1): {"spend": {"amount": 155000}, "trade": None, "payments": []},
        },
    },
}


def seed_companies(session):
    """Seed companies table with sample data"""
    logger.info("Seeding companies")
    
    created_companies = {}
    for company_name in SEED_DATA_BY_COHORT_MONTH.keys():
        # Check if company already exists
        existing = session.query(Company).filter_by(name=company_name).first()
        if existing:
            logger.info("Company already exists", name=company_name, id=existing.id)
            created_companies[company_name] = existing
            continue

        company = Company(name=company_name, created_at=datetime.utcnow())
        session.add(company)
        session.flush()  # Flush to get the ID
        created_companies[company_name] = company
        logger.info("Created company", name=company.name, id=company.id)

    return created_companies


def seed_trades(session, companies):
    """Seed trades table using cohort month organized data"""
    logger.info("Seeding trades from cohort month organized data")

    created_trades = {}
    trades_created = 0
    
    for company_name, company_data in SEED_DATA_BY_COHORT_MONTH.items():
        company = companies[company_name]
        
        for cohort_month, monthly_data in company_data["monthly_data"].items():
            trade_data = monthly_data.get("trade")
            
            if trade_data is None:
                continue  # No trade for this cohort month
                
            # Check if trade already exists
            existing = session.query(Trade).filter_by(
                company_id=company.id, 
                cohort_month=cohort_month
            ).first()

            if existing:
                logger.info("Trade already exists", company=company_name, cohort_month=cohort_month)
                trade_key = f"{company_name}_{cohort_month}"
                created_trades[trade_key] = existing
                continue

            trade = Trade(
                company_id=company.id,
                cohort_month=cohort_month,
                sharing_percentage=trade_data["sharing_percentage"],
                cash_cap=trade_data["cash_cap"],
                created_at=datetime.utcnow(),
            )
            session.add(trade)
            session.flush()
            
            trades_created += 1
            trade_key = f"{company_name}_{cohort_month}"
            created_trades[trade_key] = trade
            logger.info(
                "Created trade",
                company=company_name,
                cohort_month=cohort_month,
                sharing_percentage=trade_data["sharing_percentage"],
                cash_cap=trade_data["cash_cap"],
            )
    
    logger.info("Created trades", total_created=trades_created)
    return created_trades


def seed_payments(session, companies):
    """Seed payments table using cohort month organized data"""
    logger.info("Seeding payments from cohort month organized data")

    payments_created = 0
    
    for company_name, company_data in SEED_DATA_BY_COHORT_MONTH.items():
        company = companies[company_name]
        
        for cohort_month, monthly_data in company_data["monthly_data"].items():
            payments_data = monthly_data.get("payments", [])
            
            if not payments_data:
                continue  # No payments for this cohort month

            for payment_data in payments_data:
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
                    cohort_month=cohort_month,
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
    """Seed thresholds table using cohort month organized data"""
    logger.info("Seeding thresholds from cohort month organized data")

    thresholds_created = 0
    
    for company_name, company_data in SEED_DATA_BY_COHORT_MONTH.items():
        company = companies[company_name]
        thresholds_data = company_data.get("threshold", [])

        for threshold_data in thresholds_data:
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
    """Seed spends table using cohort month organized data"""
    logger.info("Seeding spends from cohort month organized data")

    spends_created = 0

    for company_name, company_data in SEED_DATA_BY_COHORT_MONTH.items():
        company = companies[company_name]
        
        for cohort_month, monthly_data in company_data["monthly_data"].items():
            spend_data = monthly_data.get("spend")
            
            if spend_data is None:
                continue  # No spend for this cohort month
                
            # Check if spend already exists
            existing = session.query(Spend).filter_by(company_id=company.id, cohort_month=cohort_month).first()

            if existing:
                logger.debug("Spend already exists", company=company_name, cohort_month=cohort_month)
                continue

            spend = Spend(
                company_id=company.id,
                cohort_month=cohort_month,
                spend=spend_data["amount"],
                created_at=datetime.utcnow(),
            )
            session.add(spend)
            spends_created += 1

            logger.debug(
                "Created spend entry", 
                company=company_name, 
                cohort_month=cohort_month, 
                spend_amount=spend_data["amount"]
            )

    logger.info("Created spends", total_created=spends_created)


def seed_customers(session, companies):
    """Seed customers table with comprehensive realistic customer data linked to spends"""
    logger.info("Seeding customers - generating comprehensive customer data for all spends")

    # Realistic customer name pools
    first_names = [
        "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
        "David", "Elizabeth", "William", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
        "Thomas", "Sarah", "Christopher", "Karen", "Charles", "Nancy", "Daniel", "Lisa",
        "Matthew", "Betty", "Anthony", "Helen", "Mark", "Sandra", "Donald", "Donna",
        "Steven", "Carol", "Paul", "Ruth", "Andrew", "Sharon", "Joshua", "Michelle",
    ]

    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
        "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
        "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
        "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
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
            # Generate unique customer name for this spend
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