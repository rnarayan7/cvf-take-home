"""
Test script for CVF API endpoints
"""

import pytest
import requests
import structlog

logger = structlog.get_logger(__file__)

BASE_URL = "http://localhost:8000"


@pytest.fixture(scope="module")
@pytest.mark.api
def company_id():
    """Fixture to provide a company ID for testing"""
    # First ensure we have a company to test with
    response = requests.get(f"{BASE_URL}/companies/")
    companies = response.json()

    if companies:
        company_id = companies[0]["id"]
        logger.info("Using existing company for tests", company_id=company_id, name=companies[0]["name"])
        return company_id
    else:
        # Create a test company if none exist
        logger.info("No companies found, creating test company")
        response = requests.post(f"{BASE_URL}/companies", json={"name": "Test Company"})
        if response.status_code == 200:
            company = response.json()
            logger.info("Created test company", company_id=company["id"])
            return company["id"]
        else:
            pytest.fail(f"Failed to create test company: {response.status_code}")


@pytest.mark.api
def test_health():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    logger.info("Health check", status_code=response.status_code, response=response.json())
    return response.status_code == 200


@pytest.mark.api
def test_companies():
    """Test company endpoints"""
    logger.info("Testing Companies endpoints")

    # List companies
    response = requests.get(f"{BASE_URL}/companies/")
    companies = response.json()
    logger.info("List companies", status_code=response.status_code, company_count=len(companies))

    assert response.status_code == 200
    assert isinstance(companies, list)


@pytest.mark.api
def test_cohorts(company_id):
    """Test cohort endpoints"""
    logger.info("Testing Cohorts endpoints", company_id=company_id)

    # List cohorts
    response = requests.get(f"{BASE_URL}/companies/{company_id}/cohorts/")
    cohorts = response.json()
    logger.info("List cohorts", company_id=company_id, status_code=response.status_code, cohort_count=len(cohorts))

    for cohort in cohorts:
        logger.info("Found cohort", cohort_month=cohort["cohort_month"], planned_sm=cohort["planned_sm"])


@pytest.mark.api
def test_payments(company_id):
    """Test payment endpoints"""
    logger.info("Testing Payments endpoints", company_id=company_id)

    # List payments
    response = requests.get(f"{BASE_URL}/companies/{company_id}/payments/")
    payments = response.json()
    logger.info("List payments", company_id=company_id, status_code=response.status_code, payment_count=len(payments))

    # Test CSV upload
    csv_data = """customer_id,payment_date,amount
test_001,2024-01-15,1000
test_001,2024-02-15,900
test_002,2024-01-20,1500"""

    files = {"file": ("test_payments.csv", csv_data, "text/csv")}
    response = requests.post(f"{BASE_URL}/companies/{company_id}/payments/upload", files=files)
    logger.info(
        "Upload payments test",
        company_id=company_id,
        status_code=response.status_code,
        response=response.json() if response.status_code == 200 else response.text,
    )


@pytest.mark.api
def test_thresholds(company_id):
    """Test threshold endpoints"""
    logger.info("Testing Thresholds endpoints", company_id=company_id)

    response = requests.get(f"{BASE_URL}/companies/{company_id}/thresholds/")
    thresholds = response.json()
    logger.info(
        "List thresholds", company_id=company_id, status_code=response.status_code, threshold_count=len(thresholds)
    )

    for threshold in thresholds:
        logger.info(
            "Found threshold",
            payment_period_month=threshold["payment_period_month"],
            minimum_payment_percent=threshold["minimum_payment_percent"],
        )


@pytest.mark.api
def test_analytics(company_id):
    """Test analytics endpoints"""
    logger.info("Testing Analytics endpoints", company_id=company_id)

    # Get metrics
    response = requests.get(f"{BASE_URL}/companies/{company_id}/metrics")
    if response.status_code == 200:
        metrics = response.json()
        logger.info("Get metrics", company_id=company_id, status_code=response.status_code, metrics=metrics)
    else:
        logger.error("Metrics request failed", company_id=company_id, status_code=response.status_code)

    # Get cohorts table
    response = requests.get(f"{BASE_URL}/companies/{company_id}/cohorts_table")
    if response.status_code == 200:
        table = response.json()
        logger.info(
            "Get cohorts table",
            company_id=company_id,
            status_code=response.status_code,
            cohort_count=len(table["rows"]),
            period_count=len(table["columns"]),
        )

    # Get cashflows
    response = requests.get(f"{BASE_URL}/companies/{company_id}/cashflows")
    if response.status_code == 200:
        cashflows = response.json()
        logger.info(
            "Get cashflows",
            company_id=company_id,
            status_code=response.status_code,
            trade_count=len(cashflows["trades"]),
        )


@pytest.mark.api
def test_recalc(company_id):
    """Test recalculation"""
    logger.info("Testing Recalculation endpoint", company_id=company_id)

    response = requests.post(f"{BASE_URL}/companies/{company_id}/recalc")
    logger.info(
        "Trigger recalc",
        company_id=company_id,
        status_code=response.status_code,
        result=response.json() if response.status_code == 200 else response.text,
    )
