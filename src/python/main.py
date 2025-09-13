from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import date, datetime
import structlog

from src.python.utils.calc import payment_df_to_cohort_df, get_cvf_cashflows_df
from src.python.models.models import (
    CompanyCreate,
    CompanyResponse,
    CohortCreate,
    CohortResponse,
    PaymentResponse,
    ThresholdCreate,
    ThresholdResponse,
    MetricsResponse,
)
from src.python.utils.csv_processor import get_payments_csv_processor
from src.python.db.db_operations import get_db_operations, DatabaseOperations

logger = structlog.get_logger(__file__)

app = FastAPI(
    title="CVF Portfolio Management API",
    description="""
    ## CVF Portfolio Management API
    
    This API manages cohort-based payments and cashflows for customer value funds.
    
    ### Features:
    * **Companies**: Manage portfolio companies
    * **Cohorts**: Track sales & marketing spend plans by month
    * **Payments**: Upload and manage customer payment data
    * **Analytics**: Calculate metrics like MOIC, LTV, CAC
    * **Cashflows**: View projected cashflows with trading terms
    * **Thresholds**: Set minimum payment thresholds
    
    ### Getting Started:
    1. Create a company using `POST /companies/`
    2. Add cohorts (spend plans) using `POST /companies/{id}/cohorts/`
    3. Upload payment data using `POST /companies/{id}/payments/upload`
    4. View analytics at `GET /companies/{id}/metrics`
    """,
    version="1.0.0",
    contact={
        "name": "CVF API Support",
        "email": "support@cvf.com",
    },
    license_info={
        "name": "MIT",
    },
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Session-aware database operations dependency
# get_db_operations is now defined in db_operations.py with proper dependency injection


@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "CVF Portfolio Management API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    logger.info("Health check requested")
    return {"status": "healthy", "timestamp": datetime.now()}


# Company endpoints
@app.post("/companies/", response_model=CompanyResponse, tags=["Companies"])
async def create_company(company: CompanyCreate, db_ops: DatabaseOperations = Depends(get_db_operations)):
    """Create a new company"""
    logger.info("Creating company", name=company.name)

    # Check if company already exists
    existing = db_ops.companies.get_company_by_name(company.name)
    if existing:
        logger.warning("Company already exists", name=company.name, existing_id=existing.id)
        raise HTTPException(status_code=400, detail="Company with this name already exists")

    try:
        db_company = db_ops.companies.create_company(company.name)
        return CompanyResponse.from_db(db_company)
    except Exception as e:
        logger.error("Failed to create company", name=company.name, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create company")


@app.get("/companies/", response_model=List[CompanyResponse], tags=["Companies"])
async def list_companies(db_ops: DatabaseOperations = Depends(get_db_operations)):
    """List all companies"""
    logger.info("Listing companies")
    db_companies = db_ops.companies.list_companies()
    return [CompanyResponse.from_db(company) for company in db_companies]


@app.get("/companies/{company_id}", response_model=CompanyResponse, tags=["Companies"])
async def get_company(company_id: int, db_ops: DatabaseOperations = Depends(get_db_operations)):
    """Get company by ID"""
    logger.info("Getting company", company_id=company_id)
    company = db_ops.companies.get_company_by_id(company_id)
    if not company:
        logger.warning("Company not found", company_id=company_id)
        raise HTTPException(status_code=404, detail="Company not found")
    return CompanyResponse.from_db(company)


# Spend/Cohort endpoints
@app.post("/companies/{company_id}/cohorts/", response_model=CohortResponse, tags=["Cohorts"])
async def create_cohort(company_id: int, cohort: CohortCreate, db_ops: DatabaseOperations = Depends(get_db_operations)):
    """Create a new cohort (S&M spend plan) for a company"""
    logger.info(
        "Creating cohort", company_id=company_id, cohort_month=cohort.cohort_month, planned_sm=cohort.planned_sm
    )

    # Validate company exists
    if not db_ops.companies.company_exists(company_id):
        logger.warning("Company not found for cohort creation", company_id=company_id)
        raise HTTPException(status_code=404, detail="Company not found")

    # Check if cohort already exists for this month
    existing = db_ops.cohorts.get_cohort(company_id, cohort.cohort_month)
    if existing:
        logger.warning("Cohort already exists", company_id=company_id, cohort_month=cohort.cohort_month)
        raise HTTPException(status_code=400, detail="Cohort for this month already exists")

    try:
        db_cohort = db_ops.cohorts.create_cohort(
            company_id, cohort.cohort_month, cohort.planned_sm, cohort.sharing_percentage, cohort.cash_cap
        )
        return CohortResponse.from_db(db_cohort)
    except Exception as e:
        logger.error("Failed to create cohort", company_id=company_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create cohort")


@app.get("/companies/{company_id}/cohorts/", response_model=List[CohortResponse], tags=["Cohorts"])
async def list_cohorts(company_id: int, db_ops: DatabaseOperations = Depends(get_db_operations)):
    """List all cohorts for a company"""
    logger.info("Listing cohorts", company_id=company_id)

    # Validate company exists
    if not db_ops.companies.company_exists(company_id):
        logger.warning("Company not found for cohort listing", company_id=company_id)
        raise HTTPException(status_code=404, detail="Company not found")

    db_cohorts = db_ops.cohorts.list_cohorts_by_company(company_id)
    return [CohortResponse.from_db(cohort) for cohort in db_cohorts]


# Payment endpoints
@app.post("/companies/{company_id}/payments/upload", tags=["Payments"])
async def upload_payments(
    company_id: int, file: UploadFile = File(...), db_ops: DatabaseOperations = Depends(get_db_operations)
):
    logger.info("Payment upload requested", company_id=company_id, filename=file.filename)

    # Use the CSV processor to handle the upload
    csv_processor = get_payments_csv_processor()
    result = await csv_processor.process_file(company_id, file, db_ops.db)

    logger.info("Payment upload completed", company_id=company_id, filename=file.filename, result=result)

    return result


@app.get("/companies/{company_id}/payments/", response_model=List[PaymentResponse], tags=["Payments"])
async def list_payments(company_id: int, db_ops: DatabaseOperations = Depends(get_db_operations)):
    """List all payments for a company"""
    logger.info("Listing payments", company_id=company_id)

    # Validate company exists
    if not db_ops.companies.company_exists(company_id):
        logger.warning("Company not found for payment listing", company_id=company_id)
        raise HTTPException(status_code=404, detail="Company not found")

    db_payments = db_ops.payments.list_payments_by_company(company_id)
    return [PaymentResponse.from_db(payment) for payment in db_payments]


# Threshold endpoints
@app.post("/companies/{company_id}/thresholds/", response_model=ThresholdResponse)
async def create_threshold(
    company_id: int, threshold: ThresholdCreate, db_ops: DatabaseOperations = Depends(get_db_operations)
):
    db_threshold = db_ops.thresholds.create_threshold(
        company_id, threshold.payment_period_month, threshold.minimum_payment_percent
    )
    return ThresholdResponse.from_db(db_threshold)


@app.get("/companies/{company_id}/thresholds/", response_model=List[ThresholdResponse])
async def list_thresholds(company_id: int, db_ops: DatabaseOperations = Depends(get_db_operations)):
    db_thresholds = db_ops.thresholds.list_thresholds_by_company(company_id)
    return [ThresholdResponse.from_db(threshold) for threshold in db_thresholds]


# Analytics endpoints
@app.get("/companies/{company_id}/metrics", tags=["Analytics"])
async def get_metrics(
    company_id: int, as_of: Optional[str] = None, db_ops: DatabaseOperations = Depends(get_db_operations)
) -> MetricsResponse:
    """Get company metrics for a specific month"""
    logger.info("Getting metrics", company_id=company_id, as_of=as_of)

    if as_of:
        as_of_date = datetime.strptime(as_of, "%Y-%m").date()
    else:
        as_of_date = date.today().replace(day=1)

    # Get all company data for analytics
    try:
        data = db_ops.analytics.get_company_data_for_analytics(company_id)

        if data["payments_df"].empty:
            logger.warning("No payments data found", company_id=company_id)
            return MetricsResponse(
                owed_this_month=0.0,
                breaches_count=0,
                moic_to_date=0.0,
                ltv_estimate=0.0,
                cac_estimate=0.0,
            )

        # Convert to cohort matrix
        cohort_df = payment_df_to_cohort_df(data["payments_df"])

        if data["spend_df"].empty:
            logger.warning("No spend data found", company_id=company_id)
            return MetricsResponse(
                owed_this_month=0.0,
                breaches_count=0,
                moic_to_date=0.0,
                ltv_estimate=0.0,
                cac_estimate=0.0,
            )

        spend_df = data["spend_df"].set_index("cohort")

        # Calculate cashflows
        cashflows_df = get_cvf_cashflows_df(cohort_df, spend_df, data["thresholds"], data["cohort_trades"])

        # Calculate metrics
        total_owed = 0.0  # Could calculate current month owed here
        total_spend = spend_df["spend"].sum()
        total_payments = cohort_df.sum().sum()

        # Simple calculations - can be enhanced
        moic = total_payments / total_spend if total_spend > 0 else 0.0
        ltv_estimate = total_payments / len(cohort_df) if len(cohort_df) > 0 else 0.0
        cac_estimate = total_spend / len(cohort_df) if len(cohort_df) > 0 else 0.0

        logger.info(
            "Metrics calculated", company_id=company_id, moic=moic, ltv_estimate=ltv_estimate, cac_estimate=cac_estimate
        )

        return MetricsResponse(
            owed_this_month=total_owed,
            breaches_count=0,  # Calculate based on thresholds
            moic_to_date=moic,
            ltv_estimate=ltv_estimate,
            cac_estimate=cac_estimate,
        )

    except Exception as e:
        logger.error("Error calculating metrics", company_id=company_id, error=str(e))
        return MetricsResponse(
            owed_this_month=0.0,
            breaches_count=0,
            moic_to_date=0.0,
            ltv_estimate=0.0,
            cac_estimate=0.0,
        )


@app.get("/companies/{company_id}/cohorts_table")
async def get_cohorts_table(
    company_id: int, include_predicted: bool = True, db_ops: DatabaseOperations = Depends(get_db_operations)
):
    """Get cohort payment matrix with actual and predicted values"""
    logger.info("Getting cohorts table", company_id=company_id, include_predicted=include_predicted)

    try:
        # Get payments data
        payments_df = db_ops.payments.get_payments_dataframe(company_id)
        if payments_df.empty:
            logger.warning("No payments found for cohorts table", company_id=company_id)
            return {"columns": [], "rows": []}

        # Convert to cohort matrix
        cohort_df = payment_df_to_cohort_df(payments_df)

        # Format for frontend
        columns = [f"payment_period_{i}" for i in range(len(cohort_df.columns))]
        rows = []

        for cohort_month, row in cohort_df.iterrows():
            actual_values = [float(val) if pd.notna(val) else 0.0 for val in row.values]
            predicted_values = actual_values.copy()  # Simplified - add prediction logic

            rows.append(
                {"cohort_month": cohort_month.strftime("%Y-%m"), "actual": actual_values, "predicted": predicted_values}
            )

        logger.info("Cohorts table generated", company_id=company_id, cohort_count=len(rows), period_count=len(columns))

        return {"columns": columns, "rows": rows}

    except Exception as e:
        logger.error("Error generating cohorts table", company_id=company_id, error=str(e))
        return {"columns": [], "rows": []}


@app.get("/companies/{company_id}/cashflows")
async def get_cashflows(
    company_id: int, as_of: Optional[str] = None, db_ops: DatabaseOperations = Depends(get_db_operations)
) -> Dict[str, Any]:
    """Get cashflow data with cohort trading details"""
    logger.info("Getting cashflows", company_id=company_id, as_of=as_of)

    try:
        cohorts = db_ops.cohorts.list_cohorts_by_company(company_id)

        cashflow_cohorts = []
        for cohort in cohorts:
            # Simplified cashflow calculation - could be enhanced with real calculations
            periods = []
            cumulative = 0.0

            for i in range(12):  # Show 12 periods
                period_data = {
                    "period": i,
                    "payment": 0.0,
                    "share_applied": cohort.sharing_percentage,
                    "collected": 0.0,
                    "cumulative": cumulative,
                    "status": "Active",
                    "threshold_failed": False,
                    "capped": cumulative >= cohort.cash_cap,
                }
                periods.append(period_data)

            cohort_data = {
                "cohort_id": cohort.id,
                "cohort_month": cohort.cohort_month.strftime("%Y-%m"),
                "sharing_percentage": cohort.sharing_percentage,
                "cash_cap": cohort.cash_cap,
                "cumulative_collected": cumulative,
                "periods": periods,
            }
            cashflow_cohorts.append(cohort_data)

        logger.info("Cashflows generated", company_id=company_id, cohort_count=len(cashflow_cohorts))

        return {"cohorts": cashflow_cohorts}

    except Exception as e:
        logger.error("Error generating cashflows", company_id=company_id, error=str(e))
        return {"cohorts": []}


@app.post("/companies/{company_id}/recalc", tags=["Analytics"])
async def recalculate_cashflows(company_id: int, db_ops: DatabaseOperations = Depends(get_db_operations)):
    """Synchronously recalculate cashflows and return updated metrics for a company"""
    logger.info("Cashflow recalculation requested", company_id=company_id)

    # Validate company exists
    if not db_ops.companies.company_exists(company_id):
        logger.warning("Company not found for recalculation", company_id=company_id)
        raise HTTPException(status_code=404, detail="Company not found")

    try:
        # Get all company data for analytics
        data = db_ops.analytics.get_company_data_for_analytics(company_id)

        if data["payments_df"].empty:
            logger.warning("No payments data found for recalculation", company_id=company_id)
            return {
                "message": "No payments data available for recalculation",
                "company_id": company_id,
                "metrics": {
                    "owed_this_month": 0.0,
                    "breaches_count": 0,
                    "moic_to_date": 0.0,
                    "ltv_estimate": 0.0,
                    "cac_estimate": 0.0
                }
            }

        # Convert to cohort matrix
        cohort_df = payment_df_to_cohort_df(data["payments_df"])

        if data["spend_df"].empty:
            logger.warning("No spend data found for recalculation", company_id=company_id)
            return {
                "message": "No spend data available for recalculation",
                "company_id": company_id,
                "metrics": {
                    "owed_this_month": 0.0,
                    "breaches_count": 0,
                    "moic_to_date": 0.0,
                    "ltv_estimate": 0.0,
                    "cac_estimate": 0.0
                }
            }

        spend_df = data["spend_df"].set_index("cohort")

        # Calculate cashflows
        cashflows_df = get_cvf_cashflows_df(cohort_df, spend_df, data["thresholds"], data["cohort_trades"])

        # Calculate updated metrics
        total_spend = spend_df["spend"].sum()
        total_payments = cohort_df.sum().sum()
        total_cashflows = cashflows_df.sum().sum()

        moic = total_payments / total_spend if total_spend > 0 else 0.0
        ltv_estimate = total_payments / len(cohort_df) if len(cohort_df) > 0 else 0.0
        cac_estimate = total_spend / len(cohort_df) if len(cohort_df) > 0 else 0.0

        logger.info(
            "Cashflow recalculation completed",
            company_id=company_id,
            total_cashflows=total_cashflows,
            moic=moic,
            cohorts_processed=len(cohort_df)
        )

        return {
            "message": "Cashflows recalculated successfully",
            "company_id": company_id,
            "metrics": {
                "owed_this_month": 0.0,  # Could calculate current month owed
                "breaches_count": 0,     # Could calculate threshold breaches
                "moic_to_date": moic,
                "ltv_estimate": ltv_estimate,
                "cac_estimate": cac_estimate
            },
            "summary": {
                "total_payments": total_payments,
                "total_spend": total_spend,
                "total_cashflows": total_cashflows,
                "cohorts_processed": len(cohort_df),
                "payment_periods": len(cohort_df.columns) if len(cohort_df) > 0 else 0
            }
        }

    except Exception as e:
        logger.error("Cashflow recalculation failed", company_id=company_id, error=str(e))
        raise HTTPException(status_code=500, detail=f"Recalculation failed: {str(e)}")




# Additional utility endpoints
@app.get("/companies/{company_id}/stats")
async def get_company_stats(company_id: int, db_ops: DatabaseOperations = Depends(get_db_operations)):
    """Get basic statistics about a company's data"""
    logger.info("Getting company stats", company_id=company_id)

    # Validate company exists
    if not db_ops.companies.company_exists(company_id):
        logger.warning("Company not found for stats", company_id=company_id)
        raise HTTPException(status_code=404, detail="Company not found")

    try:
        payments = db_ops.payments.list_payments_by_company(company_id)
        cohorts = db_ops.cohorts.list_cohorts_by_company(company_id)
        thresholds = db_ops.thresholds.list_thresholds_by_company(company_id)

        stats = {
            "payments_count": len(payments),
            "cohorts_count": len(cohorts),
            "thresholds_count": len(thresholds),
            "date_range": {
                "first_payment": min(p.payment_date for p in payments) if payments else None,
                "last_payment": max(p.payment_date for p in payments) if payments else None,
            },
        }

        logger.info("Company stats generated", company_id=company_id, stats=stats)
        return stats

    except Exception as e:
        logger.error("Failed to generate stats", company_id=company_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to generate statistics")
