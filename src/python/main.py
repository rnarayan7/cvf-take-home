from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
import structlog
from src.python.utils.calc import compute_company_cohort_cashflows, cohorts_to_cvf_cashflows_df
import src.python.models.models as models
from src.python.utils.csv_processor import get_payments_csv_processor
from src.python.db.db_operations import get_db_operations, DatabaseOperations

FORECAST_TIMEFRAME = 36

logger = structlog.get_logger(__file__)

app = FastAPI(
    title="CVF Portfolio Management API",
    description="""
    ## CVF Portfolio Management API
    
    This API manages cohort-based payments and cashflows for customer value funds.
    
    ### Features:
    * **Companies**: Manage portfolio companies
    * **Trades**: Track trading terms by cohort month
    * **Payments**: Upload and manage customer payment data
    * **Spends**: Manage spending data by company and cohort month (company-scoped)
    * **Customers**: View customer records with spend relationship data (read-only)
    * **Analytics**: Calculate metrics like MOIC, LTV, CAC
    * **Cashflows**: View projected cashflows with trading terms
    * **Thresholds**: Set minimum payment thresholds
    
    ### Getting Started:
    1. Create a company using `POST /companies/`
    2. Add trades (trading terms) using `POST /companies/{id}/trades/`
    3. Add spend data using `POST /companies/{id}/spends/`
    4. Upload payment data using `POST /companies/{id}/payments/upload`
    5. View analytics at `GET /companies/{id}/metrics`
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


@app.get("/")
async def root():
    logger.info("Root endpoint accessed")
    return {"message": "CVF Portfolio Management API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    logger.info("Health check requested")
    return {"status": "healthy", "timestamp": datetime.now()}


# Company endpoints
@app.post("/companies/", response_model=models.CompanyResponse, tags=["Companies"])
async def create_company(company: models.CompanyCreate, db_ops: DatabaseOperations = Depends(get_db_operations)):
    """Create a new company"""
    logger.info("Creating company", name=company.name)

    # Check if company already exists
    existing = db_ops.companies.get_company_by_name(company.name)
    if existing:
        logger.warning("Company already exists", name=company.name, existing_id=existing.id)
        raise HTTPException(status_code=400, detail="Company with this name already exists")

    try:
        db_company = db_ops.companies.create_company(company.name)
        return models.CompanyResponse.from_db(db_company)
    except Exception as e:
        logger.error("Failed to create company", name=company.name, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create company")


@app.get("/companies/", response_model=List[models.CompanyResponse], tags=["Companies"])
async def list_companies(db_ops: DatabaseOperations = Depends(get_db_operations)):
    """List all companies"""
    logger.info("Listing companies")
    db_companies = db_ops.companies.list_companies()
    return [models.CompanyResponse.from_db(company) for company in db_companies]


@app.get("/companies/{company_id}", response_model=models.CompanyResponse, tags=["Companies"])
async def get_company(company_id: int, db_ops: DatabaseOperations = Depends(get_db_operations)):
    """Get company by ID"""
    logger.info("Getting company", company_id=company_id)
    company = db_ops.companies.get_company_by_id(company_id)
    if not company:
        logger.warning("Company not found", company_id=company_id)
        raise HTTPException(status_code=404, detail="Company not found")
    return models.CompanyResponse.from_db(company)


# Trade endpoints
@app.post("/companies/{company_id}/trades/", response_model=models.TradeResponse, tags=["Trades"])
async def create_trade(company_id: int, trade: models.TradeCreate, db_ops: DatabaseOperations = Depends(get_db_operations)):
    """Create a new trade (trading terms) for a company cohort"""
    logger.info("Creating trade", company_id=company_id, cohort_month=trade.cohort_month)

    # Validate company exists
    if not db_ops.companies.company_exists(company_id):
        logger.warning("Company not found for trade creation", company_id=company_id)
        raise HTTPException(status_code=404, detail="Company not found")

    # Check if trade already exists for this month
    existing = db_ops.trades.get_trade(company_id, trade.cohort_month)
    if existing:
        logger.warning("Trade already exists", company_id=company_id, cohort_month=trade.cohort_month)
        raise HTTPException(status_code=400, detail="Trade for this month already exists")

    try:
        db_trade = db_ops.trades.create_trade(company_id, trade.cohort_month, trade.sharing_percentage, trade.cash_cap)
        return models.TradeResponse.from_db(db_trade)
    except Exception as e:
        logger.error("Failed to create trade", company_id=company_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create trade")


@app.get("/companies/{company_id}/trades/", response_model=List[models.TradeResponse], tags=["Trades"])
async def list_trades(company_id: int, db_ops: DatabaseOperations = Depends(get_db_operations)):
    """List all trades for a company"""
    logger.info("Listing trades", company_id=company_id)

    # Validate company exists
    if not db_ops.companies.company_exists(company_id):
        logger.warning("Company not found for trade listing", company_id=company_id)
        raise HTTPException(status_code=404, detail="Company not found")

    db_trades = db_ops.trades.list_trades_by_company(company_id)
    return [models.TradeResponse.from_db(trade) for trade in db_trades]


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


@app.get("/companies/{company_id}/payments/", response_model=List[models.PaymentResponse], tags=["Payments"])
async def list_payments(company_id: int, db_ops: DatabaseOperations = Depends(get_db_operations)):
    """List all payments for a company"""
    logger.info("Listing payments", company_id=company_id)

    # Validate company exists
    if not db_ops.companies.company_exists(company_id):
        logger.warning("Company not found for payment listing", company_id=company_id)
        raise HTTPException(status_code=404, detail="Company not found")

    db_payments = db_ops.payments.list_payments_by_company(company_id)
    return [models.PaymentResponse.from_db(payment) for payment in db_payments]


@app.get("/companies/{company_id}/payments/{payment_id}", response_model=models.PaymentResponse, tags=["Payments"])
async def get_company_payment(
    company_id: int, payment_id: int, db_ops: DatabaseOperations = Depends(get_db_operations)
):
    """Get specific payment by ID for a specific company"""
    logger.info("Getting company payment", company_id=company_id, payment_id=payment_id)

    try:
        # Validate company exists
        if not db_ops.companies.company_exists(company_id):
            logger.warning("Company not found for payment retrieval", company_id=company_id)
            raise HTTPException(status_code=404, detail="Company not found")

        # Get payment
        payment = db_ops.payments.get_payment_by_id(payment_id)

        if not payment:
            logger.warning("Payment not found", company_id=company_id, payment_id=payment_id)
            raise HTTPException(status_code=404, detail="Payment not found")

        # Validate payment belongs to the company
        if payment.company_id != company_id:
            logger.warning(
                "Payment does not belong to company",
                company_id=company_id,
                payment_id=payment_id,
                payment_company_id=payment.company_id,
            )
            raise HTTPException(status_code=404, detail="Payment not found")

        return models.PaymentResponse.from_db(payment)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get company payment", company_id=company_id, payment_id=payment_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get payment")


@app.put("/companies/{company_id}/payments/{payment_id}", response_model=models.PaymentResponse, tags=["Payments"])
async def update_company_payment(
    company_id: int,
    payment_id: int,
    payment_update: models.PaymentUpdate,
    db_ops: DatabaseOperations = Depends(get_db_operations),
):
    """Update an existing payment record for a specific company"""
    logger.info("Updating company payment", company_id=company_id, payment_id=payment_id)

    try:
        # Validate company exists
        if not db_ops.companies.company_exists(company_id):
            logger.warning("Company not found for payment update", company_id=company_id)
            raise HTTPException(status_code=404, detail="Company not found")

        # Check if payment exists and belongs to the company
        existing_payment = db_ops.payments.get_payment_by_id(payment_id)
        if not existing_payment:
            logger.warning("Payment not found for update", company_id=company_id, payment_id=payment_id)
            raise HTTPException(status_code=404, detail="Payment not found")

        if existing_payment.company_id != company_id:
            logger.warning(
                "Payment does not belong to company",
                company_id=company_id,
                payment_id=payment_id,
                payment_company_id=existing_payment.company_id,
            )
            raise HTTPException(status_code=404, detail="Payment not found")

        # Validate payment amount is positive if being updated
        if payment_update.amount is not None and payment_update.amount <= 0:
            logger.warning("Invalid payment amount", payment_amount=payment_update.amount)
            raise HTTPException(status_code=400, detail="Payment amount must be positive")

        # Update payment
        updated_payment = db_ops.payments.update_payment(
            payment_id=payment_id,
            amount=payment_update.amount,
            payment_date=payment_update.payment_date,
            customer_id=payment_update.customer_id,
            cohort_month=payment_update.cohort_month,
        )

        if not updated_payment:
            logger.error("Failed to update company payment", company_id=company_id, payment_id=payment_id)
            raise HTTPException(status_code=500, detail="Failed to update payment")

        return models.PaymentResponse.from_db(updated_payment)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update company payment", company_id=company_id, payment_id=payment_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to update payment")


@app.delete("/companies/{company_id}/payments/{payment_id}", tags=["Payments"])
async def delete_company_payment(
    company_id: int, payment_id: int, db_ops: DatabaseOperations = Depends(get_db_operations)
):
    """Delete a payment record for a specific company"""
    logger.info("Deleting company payment", company_id=company_id, payment_id=payment_id)

    try:
        # Validate company exists
        if not db_ops.companies.company_exists(company_id):
            logger.warning("Company not found for payment deletion", company_id=company_id)
            raise HTTPException(status_code=404, detail="Company not found")

        # Check if payment exists and belongs to the company
        existing_payment = db_ops.payments.get_payment_by_id(payment_id)
        if not existing_payment:
            logger.warning("Payment not found for deletion", company_id=company_id, payment_id=payment_id)
            raise HTTPException(status_code=404, detail="Payment not found")

        if existing_payment.company_id != company_id:
            logger.warning(
                "Payment does not belong to company",
                company_id=company_id,
                payment_id=payment_id,
                payment_company_id=existing_payment.company_id,
            )
            raise HTTPException(status_code=404, detail="Payment not found")

        # Delete payment
        success = db_ops.payments.delete_payment(payment_id)

        if not success:
            logger.error("Failed to delete company payment", company_id=company_id, payment_id=payment_id)
            raise HTTPException(status_code=500, detail="Failed to delete payment")

        logger.info("Payment deleted successfully", company_id=company_id, payment_id=payment_id)
        return {"message": "Payment deleted successfully", "payment_id": payment_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete company payment", company_id=company_id, payment_id=payment_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to delete payment")


# Threshold endpoints
@app.post("/companies/{company_id}/thresholds/", response_model=models.ThresholdResponse, tags=["Thresholds"])
async def create_threshold(
    company_id: int, threshold: models.ThresholdCreate, db_ops: DatabaseOperations = Depends(get_db_operations)
):
    db_threshold = db_ops.thresholds.create_threshold(
        company_id, threshold.payment_period_month, threshold.minimum_payment_percent
    )
    return models.ThresholdResponse.from_db(db_threshold)


@app.get("/companies/{company_id}/thresholds/", response_model=List[models.ThresholdResponse], tags=["Thresholds"])
async def list_thresholds(company_id: int, db_ops: DatabaseOperations = Depends(get_db_operations)):
    db_thresholds = db_ops.thresholds.list_thresholds_by_company(company_id)
    return [models.ThresholdResponse.from_db(threshold) for threshold in db_thresholds]


@app.get("/companies/{company_id}/spends/", response_model=List[models.SpendResponse], tags=["Spends"])
async def list_company_spends(
    company_id: int,
    cohort_month: Optional[str] = None,
    limit: Optional[int] = None,
    offset: Optional[int] = None,
    include_company: bool = False,
    db_ops: DatabaseOperations = Depends(get_db_operations),
):
    """Get all spend records for a specific company"""
    logger.info(
        "Listing company spends",
        company_id=company_id,
        cohort_month=cohort_month,
        limit=limit,
        offset=offset,
        include_company=include_company,
    )

    try:
        # Validate company exists
        if not db_ops.companies.company_exists(company_id):
            logger.warning("Company not found for spend listing", company_id=company_id)
            raise HTTPException(status_code=404, detail="Company not found")

        # Parse cohort_month if provided
        cohort_date = None
        if cohort_month:
            try:
                cohort_date = datetime.strptime(cohort_month, "%Y-%m").date()
            except ValueError:
                logger.warning("Invalid cohort_month format", cohort_month=cohort_month)
                raise HTTPException(status_code=400, detail="Invalid cohort_month format. Use YYYY-MM")

        # Get spends for the company
        db_spends = db_ops.spends.list_spends_by_company(
            company_id=company_id, cohort_month=cohort_date, limit=limit, offset=offset
        )

        # Convert to response models
        response_spends = []
        for spend in db_spends:
            if include_company:
                # Load company relationship if requested
                from sqlalchemy.orm import joinedload
                from src.python.db.schemas import Spend

                spend_with_company = (
                    db_ops.db.query(Spend).options(joinedload("company")).filter(Spend.id == spend.id)
                ).first()
                response_spends.append(models.SpendResponse.from_db(spend_with_company, include_company=True))
            else:
                response_spends.append(models.SpendResponse.from_db(spend, include_company=False))

        logger.info("Company spends listed", company_id=company_id, count=len(response_spends))
        return response_spends

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to list company spends", company_id=company_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list company spends")


@app.post("/companies/{company_id}/spends/", response_model=models.SpendResponse, tags=["Spends"])
async def create_company_spend(
    company_id: int, spend: models.SpendCreate, db_ops: DatabaseOperations = Depends(get_db_operations)
):
    """Create a new spend record for a specific company"""
    logger.info(
        "Creating company spend", company_id=company_id, cohort_month=spend.cohort_month, spend_amount=spend.spend
    )

    try:
        # Validate company exists
        if not db_ops.companies.company_exists(company_id):
            logger.warning("Company not found for spend creation", company_id=company_id)
            raise HTTPException(status_code=404, detail="Company not found")

        # Check if spend already exists for this company and cohort month
        existing = db_ops.spends.get_spend_by_company_and_cohort(company_id, spend.cohort_month)
        if existing:
            logger.warning("Spend already exists", company_id=company_id, cohort_month=spend.cohort_month)
            raise HTTPException(status_code=400, detail="Spend for this company and cohort month already exists")

        # Validate spend amount is positive
        if spend.spend <= 0:
            logger.warning("Invalid spend amount", spend_amount=spend.spend)
            raise HTTPException(status_code=400, detail="Spend amount must be positive")

        # Create spend
        db_spend = db_ops.spends.create_spend(company_id=company_id, cohort_month=spend.cohort_month, spend=spend.spend)

        return models.SpendResponse.from_db(db_spend)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to create company spend", company_id=company_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to create spend")


@app.get("/companies/{company_id}/spends/{spend_id}", response_model=models.SpendResponse, tags=["Spends"])
async def get_company_spend(
    company_id: int,
    spend_id: int,
    include_company: bool = False,
    db_ops: DatabaseOperations = Depends(get_db_operations),
):
    """Get specific spend by ID for a specific company"""
    logger.info("Getting company spend", company_id=company_id, spend_id=spend_id, include_company=include_company)

    try:
        # Validate company exists
        if not db_ops.companies.company_exists(company_id):
            logger.warning("Company not found for spend retrieval", company_id=company_id)
            raise HTTPException(status_code=404, detail="Company not found")

        # Get spend with optional company relationship
        if include_company:
            from sqlalchemy.orm import joinedload
            from src.python.db.schemas import Spend

            spend = (
                db_ops.db.query(Spend)
                .options(joinedload("company"))
                .filter(Spend.id == spend_id, Spend.company_id == company_id)
                .first()
            )
        else:
            spend = db_ops.spends.get_spend_by_id(spend_id)

        if not spend:
            logger.warning("Spend not found", company_id=company_id, spend_id=spend_id)
            raise HTTPException(status_code=404, detail="Spend not found")

        # Validate spend belongs to the company
        if spend.company_id != company_id:
            logger.warning(
                "Spend does not belong to company",
                company_id=company_id,
                spend_id=spend_id,
                spend_company_id=spend.company_id,
            )
            raise HTTPException(status_code=404, detail="Spend not found")

        return models.SpendResponse.from_db(spend, include_company=include_company)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get company spend", company_id=company_id, spend_id=spend_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to get spend")


@app.put("/companies/{company_id}/spends/{spend_id}", response_model=models.SpendResponse, tags=["Spends"])
async def update_company_spend(
    company_id: int, spend_id: int, spend_update: models.SpendUpdate, db_ops: DatabaseOperations = Depends(get_db_operations)
):
    """Update an existing spend record for a specific company"""
    logger.info("Updating company spend", company_id=company_id, spend_id=spend_id)

    try:
        # Validate company exists
        if not db_ops.companies.company_exists(company_id):
            logger.warning("Company not found for spend update", company_id=company_id)
            raise HTTPException(status_code=404, detail="Company not found")

        # Check if spend exists and belongs to the company
        existing_spend = db_ops.spends.get_spend_by_id(spend_id)
        if not existing_spend:
            logger.warning("Spend not found for update", company_id=company_id, spend_id=spend_id)
            raise HTTPException(status_code=404, detail="Spend not found")

        if existing_spend.company_id != company_id:
            logger.warning(
                "Spend does not belong to company",
                company_id=company_id,
                spend_id=spend_id,
                spend_company_id=existing_spend.company_id,
            )
            raise HTTPException(status_code=404, detail="Spend not found")

        # Prevent changing company_id in company-scoped endpoint
        if spend_update.company_id is not None and spend_update.company_id != company_id:
            logger.warning(
                "Cannot change company_id in company-scoped endpoint",
                company_id=company_id,
                new_company_id=spend_update.company_id,
            )
            raise HTTPException(status_code=400, detail="Cannot change company_id for spend in company-scoped endpoint")

        # Check for duplicate if cohort_month is being updated
        if spend_update.cohort_month is not None:
            existing_duplicate = db_ops.spends.get_spend_by_company_and_cohort(company_id, spend_update.cohort_month)
            if existing_duplicate and existing_duplicate.id != spend_id:
                logger.warning(
                    "Spend already exists for updated cohort month",
                    company_id=company_id,
                    cohort_month=spend_update.cohort_month,
                )
                raise HTTPException(status_code=400, detail="Spend for this company and cohort month already exists")

        # Validate spend amount is positive if being updated
        if spend_update.spend is not None and spend_update.spend <= 0:
            logger.warning("Invalid spend amount", spend_amount=spend_update.spend)
            raise HTTPException(status_code=400, detail="Spend amount must be positive")

        # Update spend (don't allow company_id change in company-scoped context)
        updated_spend = db_ops.spends.update_spend(
            spend_id=spend_id,
            company_id=None,  # Keep original company_id
            cohort_month=spend_update.cohort_month,
            spend=spend_update.spend,
        )

        if not updated_spend:
            logger.error("Failed to update company spend", company_id=company_id, spend_id=spend_id)
            raise HTTPException(status_code=500, detail="Failed to update spend")

        return models.SpendResponse.from_db(updated_spend)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update company spend", company_id=company_id, spend_id=spend_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to update spend")


@app.get("/companies/{company_id}/cashflows")
async def get_cashflows(company_id: int, db_ops: DatabaseOperations = Depends(get_db_operations)) -> models.CashflowResponse:
    """Get cashflow data with cohort trading details"""
    logger.info("Getting cashflows", company_id=company_id)

    try:
        # Validate company exists
        if not db_ops.companies.company_exists(company_id):
            logger.warning("Company not found for payment deletion", company_id=company_id)
            raise HTTPException(status_code=404, detail="Company not found")

        trades = db_ops.trades.list_trades_by_company(company_id)
        payments = db_ops.payments.list_payments_by_company(company_id)
        spends = db_ops.spends.list_spends_by_company(company_id)
        thresholds = db_ops.thresholds.list_thresholds_by_company(company_id)
        cohorts = compute_company_cohort_cashflows(
            company_id=company_id, trades=trades, payments=payments, spends=spends, thresholds=thresholds
        )
        logger.info("Cashflows generated", company_id=company_id)
        return models.CashflowResponse(cohorts=cohorts)

    except Exception as e:
        logger.error("Error generating cashflows", company_id=company_id, error=str(e))
        raise HTTPException(status_code=500, detail="Error generating cashflows")


# Analytics endpoints
@app.get("/companies/{company_id}/metrics", tags=["Analytics"])
async def get_metrics(company_id: int, db_ops: DatabaseOperations = Depends(get_db_operations)) -> models.MetricsResponse:
    """Get company metrics for a specific month"""
    logger.info("Getting metrics", company_id=company_id)

    # Get all company data for analytics
    try:
        data = db_ops.analytics.get_company_data_for_analytics(company_id)

        if data["payments_df"].empty:
            logger.warning("No payments data found", company_id=company_id)
            return models.MetricsResponse(
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
            return models.MetricsResponse(
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

        return models.MetricsResponse(
            owed_this_month=total_owed,
            breaches_count=0,  # Calculate based on thresholds
            moic_to_date=moic,
            ltv_estimate=ltv_estimate,
            cac_estimate=cac_estimate,
        )

    except Exception as e:
        logger.error("Error calculating metrics", company_id=company_id, error=str(e))
        return models.MetricsResponse(
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
        trades = db_ops.trades.list_trades_by_company(company_id)
        payments = db_ops.payments.list_payments_by_company(company_id)
        spends = db_ops.spends.list_spends_by_company(company_id)
        thresholds = db_ops.thresholds.list_thresholds_by_company(company_id)
        cohorts = compute_company_cohort_cashflows(
            company_id=company_id, trades=trades, payments=payments, spends=spends, thresholds=thresholds
        )
        df = cohorts_to_cvf_cashflows_df(cohorts)

        return {"df": df}

    except Exception as e:
        logger.error("Error generating cohorts table", company_id=company_id, error=str(e))
        return {"columns": [], "rows": []}
