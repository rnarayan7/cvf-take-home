"""
CVF Portfolio Management API - Comprehensive Integration Test
Single test that validates the entire system end-to-end via REST API
"""

import pytest
import requests
import json
import io
import pandas as pd
import structlog
from typing import Dict, List, Any

# Configuration
BASE_URL = "http://localhost:8000"

logger = structlog.get_logger(__file__)


@pytest.mark.integration
class TestCVFIntegration:
    """Comprehensive integration test for CVF API via REST endpoints"""

    def test_complete_cvf_workflow(self):
        """
        Single comprehensive test that validates the entire CVF workflow:
        1. Create companies
        2. Create cohorts with trading terms
        3. Upload payment data
        4. Create thresholds
        5. Calculate metrics and validate results
        6. Test cashflow calculations
        7. Validate all data consistency
        """
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        
        # Test data storage
        companies = {}
        cohorts = {}
        
        # === STEP 1: Create Companies ===
        logger.info("Starting CVF workflow integration test - Step 1: Creating Companies")
        company_configs = [
            {"name": "Acme Corp"},
            {"name": "TechStart Inc"},
            {"name": "GrowthCo"}
        ]
        
        for config in company_configs:
            companies[config["name"]] = self._create_company(session, config)
        
        # Validate companies were created
        all_companies = self._list_companies(session)
        assert len(all_companies) >= 3, "Should have at least 3 companies"
        for company_name in companies.keys():
            assert any(c["name"] == company_name for c in all_companies), f"Company {company_name} not found in list"
        
        # === STEP 2: Create Cohorts with Trading Terms ===
        logger.info("Step 2: Creating Cohorts with Trading Terms")
        cohort_configs = [
            {
                "company": "Acme Corp",
                "cohorts": [
                    {"cohort_month": "2024-01-01", "planned_sm": 100000.0, "sharing_percentage": 0.35, "cash_cap": 150000.0},
                    {"cohort_month": "2024-02-01", "planned_sm": 120000.0, "sharing_percentage": 0.40, "cash_cap": 180000.0},
                    {"cohort_month": "2024-03-01", "planned_sm": 90000.0, "sharing_percentage": 0.32, "cash_cap": 120000.0}
                ]
            },
            {
                "company": "TechStart Inc",
                "cohorts": [
                    {"cohort_month": "2024-01-01", "planned_sm": 50000.0, "sharing_percentage": 0.45, "cash_cap": 75000.0},
                    {"cohort_month": "2024-02-01", "planned_sm": 60000.0, "sharing_percentage": 0.42, "cash_cap": 90000.0}
                ]
            },
            {
                "company": "GrowthCo",
                "cohorts": [
                    {"cohort_month": "2024-02-01", "planned_sm": 200000.0, "sharing_percentage": 0.30, "cash_cap": 300000.0}
                ]
            }
        ]
        
        for config in cohort_configs:
            company_id = companies[config["company"]]["id"]
            for cohort_data in config["cohorts"]:
                cohort_key = f"{config['company']}_{cohort_data['cohort_month']}"
                cohorts[cohort_key] = self._create_cohort(session, company_id, cohort_data)
        
        # Validate cohorts were created correctly
        for company_name, company in companies.items():
            company_cohorts = self._list_cohorts(session, company["id"])
            expected_cohorts = [k for k in cohorts.keys() if k.startswith(company_name)]
            if expected_cohorts:
                assert len(company_cohorts) > 0, f"Company {company_name} should have cohorts"
                
                # Validate cohort data integrity
                for cohort in company_cohorts:
                    assert cohort["company_id"] == company["id"]
                    assert "planned_sm" in cohort
                    assert "sharing_percentage" in cohort
                    assert "cash_cap" in cohort
                    assert 0 <= cohort["sharing_percentage"] <= 1, "Sharing percentage should be between 0 and 1"
                    assert cohort["cash_cap"] >= cohort["planned_sm"], "Cash cap should be >= planned spend"
        
        # === STEP 3: Upload Payment Data ===
        logger.info("Step 3: Uploading Payment Data")
        
        # Create payment data that aligns with cohorts
        acme_payments = [
            {"customer_id": "cust_001", "payment_date": "2024-01-15", "amount": 5000.0},
            {"customer_id": "cust_001", "payment_date": "2024-02-15", "amount": 4500.0},
            {"customer_id": "cust_002", "payment_date": "2024-01-20", "amount": 8000.0},
            {"customer_id": "cust_003", "payment_date": "2024-02-10", "amount": 12000.0},
        ]
        
        techstart_payments = [
            {"customer_id": "tech_001", "payment_date": "2024-01-10", "amount": 3000.0},
            {"customer_id": "tech_002", "payment_date": "2024-02-05", "amount": 2500.0},
        ]
        
        growthco_payments = [
            {"customer_id": "growth_001", "payment_date": "2024-02-12", "amount": 25000.0},
        ]
        
        # Upload payments for each company
        self._upload_payments(session, companies["Acme Corp"]["id"], acme_payments)
        self._upload_payments(session, companies["TechStart Inc"]["id"], techstart_payments)
        self._upload_payments(session, companies["GrowthCo"]["id"], growthco_payments)
        
        # Validate payments were uploaded correctly
        for company_name, company in companies.items():
            payments = self._list_payments(session, company["id"])
            assert len(payments) > 0, f"Company {company_name} should have payments"
            
            # Validate payment structure and cohort assignment
            for payment in payments:
                assert "customer_id" in payment
                assert "payment_date" in payment
                assert "amount" in payment
                assert "cohort_month" in payment
                assert payment["amount"] > 0, "Payment amount should be positive"
                assert payment["company_id"] == company["id"]
        
        # === STEP 4: Create Thresholds ===
        logger.info("Step 4: Creating Thresholds")
        
        threshold_configs = [
            {
                "company": "Acme Corp",
                "thresholds": [
                    {"payment_period_month": 0, "minimum_payment_percent": 0.15},
                    {"payment_period_month": 1, "minimum_payment_percent": 0.10}
                ]
            },
            {
                "company": "TechStart Inc", 
                "thresholds": [
                    {"payment_period_month": 0, "minimum_payment_percent": 0.20}
                ]
            },
            {
                "company": "GrowthCo",
                "thresholds": [
                    {"payment_period_month": 1, "minimum_payment_percent": 0.12}
                ]
            }
        ]
        
        for config in threshold_configs:
            company_id = companies[config["company"]]["id"]
            for threshold_data in config["thresholds"]:
                self._create_threshold(session, company_id, threshold_data)
        
        # Validate thresholds
        for company_name, company in companies.items():
            thresholds = self._list_thresholds(session, company["id"])
            # At least some companies should have thresholds
            if any(cfg["company"] == company_name for cfg in threshold_configs):
                assert len(thresholds) > 0, f"Company {company_name} should have thresholds"
                for threshold in thresholds:
                    assert 0 <= threshold["minimum_payment_percent"] <= 1, "Threshold should be between 0 and 1"
                    assert threshold["payment_period_month"] >= 0, "Payment period should be non-negative"
        
        # === STEP 5: Calculate Metrics and Validate ===
        logger.info("Step 5: Calculating and Validating Metrics")
        
        for company_name, company in companies.items():
            company_id = company["id"]
            
            # Calculate metrics
            metrics = self._calculate_metrics(session, company_id)
            
            # Validate metrics structure
            assert "cohort_metrics" in metrics, "Should have cohort_metrics"
            
            if metrics["cohort_metrics"]:
                for cohort_metric in metrics["cohort_metrics"]:
                    # Validate required fields
                    required_fields = ["cohort_month", "customers", "months_tracked", "ltv_metrics", "payment_metrics"]
                    for field in required_fields:
                        assert field in cohort_metric, f"Missing field {field} in cohort metrics"
                    
                    # Validate data types and ranges
                    assert isinstance(cohort_metric["customers"], int), "Customers should be integer"
                    assert cohort_metric["customers"] >= 0, "Customers should be non-negative"
                    assert isinstance(cohort_metric["months_tracked"], int), "Months tracked should be integer"
                    assert cohort_metric["months_tracked"] >= 0, "Months tracked should be non-negative"
                    
                    # Validate LTV metrics
                    ltv_metrics = cohort_metric["ltv_metrics"]
                    assert isinstance(ltv_metrics, dict), "LTV metrics should be dict"
                    if "ltv_mean" in ltv_metrics:
                        assert isinstance(ltv_metrics["ltv_mean"], (int, float)), "LTV mean should be numeric"
                    
                    # Validate payment metrics
                    payment_metrics = cohort_metric["payment_metrics"]
                    assert isinstance(payment_metrics, dict), "Payment metrics should be dict"
            
            logger.info("Metrics validated for company", 
                       company=company_name, 
                       cohort_count=len(metrics['cohort_metrics']))
        
        # === STEP 6: Test Cashflow Calculations ===
        logger.info("Step 6: Testing Cashflow Calculations")
        
        for company_name, company in companies.items():
            company_id = company["id"]
            
            # Get initial cashflows
            initial_cashflows = self._get_cashflows(session, company_id)
            
            # Recalculate cashflows
            recalc_result = self._recalculate_cashflows(session, company_id)
            assert "message" in recalc_result, "Recalculation should return a message"
            
            # Get updated cashflows
            updated_cashflows = self._get_cashflows(session, company_id)
            
            # Validate cashflow structure
            if updated_cashflows:
                for cashflow in updated_cashflows:
                    assert "month" in cashflow, "Cashflow should have month"
                    assert "cashflow" in cashflow, "Cashflow should have cashflow value"
                    assert isinstance(cashflow["cashflow"], (int, float)), "Cashflow should be numeric"
            
            logger.info("Cashflows validated for company", 
                       company=company_name, 
                       cashflow_periods=len(updated_cashflows))
        
        # === STEP 7: Cross-Validation and Business Logic ===
        logger.info("Step 7: Cross-Validation and Business Logic")
        
        # Validate total system consistency
        total_companies = len(self._list_companies(session))
        total_payments = sum(len(self._list_payments(session, c["id"])) for c in companies.values())
        total_cohorts = sum(len(self._list_cohorts(session, c["id"])) for c in companies.values())
        
        assert total_companies >= 3, "Should have at least 3 companies in system"
        assert total_payments >= 7, "Should have at least 7 payments across all companies"
        assert total_cohorts >= 6, "Should have at least 6 cohorts across all companies"
        
        # Validate business logic: companies with more spend should generally have more sophisticated setups
        acme_cohorts = self._list_cohorts(session, companies["Acme Corp"]["id"])
        acme_total_spend = sum(c["planned_sm"] for c in acme_cohorts)
        
        growthco_cohorts = self._list_cohorts(session, companies["GrowthCo"]["id"])
        growthco_total_spend = sum(c["planned_sm"] for c in growthco_cohorts)
        
        # GrowthCo has higher individual cohort spend, Acme has more cohorts
        assert acme_total_spend > 0 and growthco_total_spend > 0, "All companies should have positive spend"
        
        logger.info("All cross-validations passed")
        logger.info("System validation complete", 
                   total_companies=total_companies, 
                   total_cohorts=total_cohorts, 
                   total_payments=total_payments)
        
        logger.info("Complete CVF workflow integration test PASSED!")

    # === Helper Methods ===
    
    def _create_company(self, session: requests.Session, company_data: Dict) -> Dict:
        """Create a company and return the created company data"""
        response = session.post(f"{BASE_URL}/companies", json=company_data)
        assert response.status_code == 200, f"Failed to create company {company_data['name']}: {response.text}"
        company = response.json()
        assert company["name"] == company_data["name"]
        assert "id" in company
        logger.info("Created company", name=company['name'], company_id=company['id'])
        return company
    
    def _list_companies(self, session: requests.Session) -> List[Dict]:
        """List all companies"""
        response = session.get(f"{BASE_URL}/companies")
        assert response.status_code == 200, f"Failed to list companies: {response.text}"
        return response.json()
    
    def _create_cohort(self, session: requests.Session, company_id: int, cohort_data: Dict) -> Dict:
        """Create a cohort for a company"""
        response = session.post(f"{BASE_URL}/companies/{company_id}/cohorts", json=cohort_data)
        assert response.status_code == 200, f"Failed to create cohort: {response.text}"
        cohort = response.json()
        assert cohort["cohort_month"] == cohort_data["cohort_month"]
        assert cohort["planned_sm"] == cohort_data["planned_sm"]
        logger.info("Created cohort", 
                   cohort_month=cohort['cohort_month'], 
                   company_id=company_id,
                   planned_sm=cohort['planned_sm'])
        return cohort
    
    def _list_cohorts(self, session: requests.Session, company_id: int) -> List[Dict]:
        """List cohorts for a company"""
        response = session.get(f"{BASE_URL}/companies/{company_id}/cohorts")
        assert response.status_code == 200, f"Failed to list cohorts: {response.text}"
        return response.json()
    
    def _upload_payments(self, session: requests.Session, company_id: int, payment_data: List[Dict]):
        """Upload payment data via CSV"""
        df = pd.DataFrame(payment_data)
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_content = csv_buffer.getvalue()
        
        files = {"file": ("payments.csv", csv_content, "text/csv")}
        response = session.post(f"{BASE_URL}/companies/{company_id}/payments/upload", files=files)
        assert response.status_code == 200, f"Failed to upload payments: {response.text}"
        result = response.json()
        assert result["count"] == len(payment_data)
        logger.info("Uploaded payments", 
                   company_id=company_id, 
                   payment_count=result['count'])
    
    def _list_payments(self, session: requests.Session, company_id: int) -> List[Dict]:
        """List payments for a company"""
        response = session.get(f"{BASE_URL}/companies/{company_id}/payments")
        assert response.status_code == 200, f"Failed to list payments: {response.text}"
        return response.json()
    
    def _create_threshold(self, session: requests.Session, company_id: int, threshold_data: Dict) -> Dict:
        """Create a threshold for a company"""
        response = session.post(f"{BASE_URL}/companies/{company_id}/thresholds", json=threshold_data)
        assert response.status_code == 200, f"Failed to create threshold: {response.text}"
        threshold = response.json()
        assert threshold["payment_period_month"] == threshold_data["payment_period_month"]
        assert threshold["minimum_payment_percent"] == threshold_data["minimum_payment_percent"]
        logger.info("Created threshold", 
                   payment_period_months=threshold_data['payment_period_month'],
                   minimum_payment_percent=threshold_data['minimum_payment_percent'],
                   company_id=company_id)
        return threshold
    
    def _list_thresholds(self, session: requests.Session, company_id: int) -> List[Dict]:
        """List thresholds for a company"""
        response = session.get(f"{BASE_URL}/companies/{company_id}/thresholds")
        assert response.status_code == 200, f"Failed to list thresholds: {response.text}"
        return response.json()
    
    def _calculate_metrics(self, session: requests.Session, company_id: int) -> Dict:
        """Calculate metrics for a company"""
        response = session.post(f"{BASE_URL}/companies/{company_id}/calculate")
        assert response.status_code == 200, f"Failed to calculate metrics: {response.text}"
        return response.json()
    
    def _get_cashflows(self, session: requests.Session, company_id: int) -> List[Dict]:
        """Get cashflows for a company"""
        response = session.get(f"{BASE_URL}/companies/{company_id}/cashflows")
        assert response.status_code == 200, f"Failed to get cashflows: {response.text}"
        return response.json()
    
    def _recalculate_cashflows(self, session: requests.Session, company_id: int) -> Dict:
        """Recalculate cashflows for a company"""
        response = session.post(f"{BASE_URL}/companies/{company_id}/recalculate")
        assert response.status_code == 200, f"Failed to recalculate cashflows: {response.text}"
        return response.json()