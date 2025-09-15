# CVF Portfolio Management API - Architecture Documentation

## Table of Contents
1. [Technology Stack & Framework Choices](#technology-stack--framework-choices)
2. [API Design](#api-design)
3. [Database Design](#database-design)
4. [Calculations & Business Logic](#calculations--business-logic)
5. [Future Investment Areas](#future-investment-areas)

---

## Technology Stack & Framework Choices

### Core Technologies

#### **Backend Framework: FastAPI**
- **Choice Rationale**: FastAPI was selected for its:
  - Automatic OpenAPI/Swagger documentation generation
  - Built-in request/response validation with Pydantic
  - High performance (similar to Node.js and Go)
  - Native async/await support
  - Type hints integration for better developer experience

#### **Database: SQLAlchemy + Alembic**
- **ORM**: SQLAlchemy 2.0 for database operations
- **Migrations**: Alembic for schema versioning and migrations
- **Storage**: SQLite for development, PostgreSQL-ready for production
- **Choice Rationale**:
  - SQLAlchemy provides robust ORM with relationship management
  - Alembic ensures database schema versioning
  - PostgreSQL compatibility for production scalability

#### **Data Processing: Pandas + NumPy**
- **Pandas**: For cohort analysis and cashflow calculations
- **NumPy**: For numerical computations
- **NumPy-Financial**: For IRR (Internal Rate of Return) calculations
- **Choice Rationale**: 
  - Pandas excels at time-series and cohort analysis
  - NumPy provides efficient numerical computations
  - Established ecosystem for financial calculations

#### **Validation & Serialization: Pydantic**
- **Models**: Type-safe request/response schemas
- **Validation**: Automatic input validation
- **Serialization**: JSON serialization with type conversion
- **Choice Rationale**: Tight integration with FastAPI, compile-time type checking

#### **Logging: Structlog**
- **Structured Logging**: JSON-formatted logs for better observability
- **Context Preservation**: Request tracing and debugging capabilities

#### **Testing: Pytest**
- **Framework**: Pytest for unit and integration testing
- **API Testing**: Direct HTTP calls for endpoint validation
- **Coverage**: Comprehensive test suite for calculations and API endpoints

### Development Tools

#### **Code Quality**
- **Ruff**: Fast Python linter and formatter
- **Type Hints**: Full type annotation coverage
- **Pre-commit**: Code quality enforcement

#### **Model Context Protocol (MCP)**
- **FastMCP**: Integration for AI assistant tool access
- **Purpose**: Enables AI assistants to interact with the API programmatically

---

## API Design

### Architecture Pattern: RESTful API with Resource Nesting

#### **Core Design Principles**

1. **Resource-Oriented Design**
   - Companies as primary resources
   - Nested resources under companies (trades, payments, spends, thresholds)
   - Clear hierarchical relationships

2. **Company-Scoped Endpoints**
   ```
   /companies/{company_id}/payments/
   /companies/{company_id}/trades/
   /companies/{company_id}/spends/
   /companies/{company_id}/thresholds/
   /companies/{company_id}/cashflows/
   ```

3. **Consistent HTTP Methods**
   - `GET`: Retrieve resources
   - `POST`: Create new resources
   - `PUT`: Update existing resources
   - `DELETE`: Remove resources

#### **Key Endpoint Categories**

##### **Company Management**
```http
GET    /companies/              # List all companies
POST   /companies/              # Create company
GET    /companies/{id}          # Get company details
```

##### **Financial Data Management**
```http
# Trades (Investment Terms)
POST   /companies/{id}/trades/           # Create trade terms
GET    /companies/{id}/trades/           # List company trades

# Payments (Customer Revenue)
POST   /companies/{id}/payments/upload   # Bulk upload via CSV
GET    /companies/{id}/payments/         # List payments
PUT    /companies/{id}/payments/{pid}    # Update payment
DELETE /companies/{id}/payments/{pid}    # Delete payment

# Spends (Marketing Investment)
POST   /companies/{id}/spends/           # Create spend record
GET    /companies/{id}/spends/           # List spends
PUT    /companies/{id}/spends/{sid}      # Update spend

# Thresholds (Performance Benchmarks)
POST   /companies/{id}/thresholds/       # Create threshold
GET    /companies/{id}/thresholds/       # List thresholds
PUT    /companies/{id}/thresholds/{tid}  # Update threshold
```

##### **Analytics & Reporting**
```http
GET    /companies/{id}/cashflows         # Current cashflow projections
POST   /companies/{id}/cashflows/predicted  # Predicted cashflows with churn
GET    /companies/{id}/cohorts_table     # Cohort analysis matrix
```

#### **Request/Response Design**

##### **Consistent Response Structure**
- All responses use Pydantic models for type safety
- Standardized error responses with HTTP status codes
- Date formatting: ISO 8601 strings
- Monetary values: Decimal precision

##### **Input Validation**
- Automatic validation via Pydantic schemas
- Business rule validation (e.g., positive amounts, valid date ranges)
- Custom validation for financial constraints

##### **Error Handling**
```python
# Standard error responses
404: Resource not found
400: Invalid input data
500: Internal server error
409: Conflict (e.g., duplicate resources)
```

#### **CSV Upload Support**
- Bulk payment upload via `/companies/{id}/payments/upload`
- Automatic parsing and validation
- Error reporting for invalid rows
- Transaction-safe bulk inserts

---

## Database Design

### Schema Overview

The database follows a normalized relational design with clear entity relationships:

```sql
Companies (1) -> (N) Trades
Companies (1) -> (N) Payments
Companies (1) -> (N) Spends
Companies (1) -> (N) Thresholds
Spends (1) -> (N) Customers
```

### Core Tables

#### **Companies Table**
```sql
CREATE TABLE companies (
    id INTEGER PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```
- **Purpose**: Portfolio companies managed by the CVF
- **Key Constraints**: Unique company names

#### **Trades Table**
```sql
CREATE TABLE trades (
    id INTEGER PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    cohort_month DATE NOT NULL,
    sharing_percentage NUMERIC NOT NULL DEFAULT 0.5,
    cash_cap NUMERIC NOT NULL DEFAULT 0.0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_id, cohort_month)
);
```
- **Purpose**: Investment terms for each company cohort
- **Key Constraints**: One trade per company per cohort month
- **Business Logic**: Defines revenue sharing terms

#### **Payments Table**
```sql
CREATE TABLE payments (
    id INTEGER PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    customer_id VARCHAR NOT NULL,
    payment_date DATE NOT NULL,
    cohort_month DATE NOT NULL,
    amount NUMERIC NOT NULL CHECK (amount >= 0),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```
- **Purpose**: Customer payment records from portfolio companies
- **Key Features**: 
  - Tracks individual customer payments
  - Links payments to cohorts for analysis
  - Amount validation

#### **Spends Table**
```sql
CREATE TABLE spends (
    id INTEGER PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    cohort_month DATE NOT NULL,
    spend NUMERIC NOT NULL CHECK (spend >= 0),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(company_id, cohort_month)
);
```
- **Purpose**: Marketing/acquisition spend by company and cohort
- **Key Constraints**: One spend record per company per cohort month

#### **Thresholds Table**
```sql
CREATE TABLE thresholds (
    id INTEGER PRIMARY KEY,
    company_id INTEGER REFERENCES companies(id) ON DELETE CASCADE,
    payment_period_month INTEGER NOT NULL CHECK (payment_period_month >= 0),
    minimum_payment_percent NUMERIC NOT NULL CHECK (minimum_payment_percent BETWEEN 0 AND 1),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```
- **Purpose**: Performance benchmarks for payment collections
- **Business Logic**: Defines minimum payment thresholds by period

#### **Customers Table**
```sql
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    customer_name VARCHAR NOT NULL,
    cohort_month DATE NOT NULL,
    spend_id INTEGER REFERENCES spends(id) ON DELETE CASCADE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```
- **Purpose**: Customer records linked to acquisition spends
- **Relationship**: Many customers per spend record

### Database Operations Layer

#### **Repository Pattern Implementation**
The codebase implements a repository pattern through `DatabaseOperations`:

```python
class DatabaseOperations:
    def __init__(self, db: Session):
        self.companies = CompanyOperations(db)
        self.trades = TradeOperations(db)
        self.payments = PaymentOperations(db)
        self.spends = SpendOperations(db)
        self.thresholds = ThresholdOperations(db)
```

#### **Migration Strategy**
- **Alembic**: Manages database schema versions
- **Migration Files**: Located in `/alembic/versions/`
- **Key Migrations**:
  - Initial schema creation
  - Table renames (cohorts → trades)
  - Precision improvements (Float → Numeric)
  - New table additions (spends, customers)

### Data Integrity

#### **Foreign Key Constraints**
- All child tables reference companies with `ON DELETE CASCADE`
- Ensures data consistency when companies are removed

#### **Check Constraints**
- Positive amounts for payments and spends
- Valid percentage ranges for thresholds and sharing rates

#### **Unique Constraints**
- Company names must be unique
- One trade/spend per company per cohort month

---

## Calculations & Business Logic

### Core Financial Calculation Engine: Deep Dive into calc.py

The `calc.py` file serves as the heart of the CVF portfolio management system, implementing sophisticated financial modeling for venture capital fund analysis. The calculations center around cohort-based analytics, churn predictions, and complex revenue sharing algorithms.

#### **Primary Function: `compute_company_cohort_cashflows`**

This is the main orchestrator function that processes all financial data for a company and returns structured cohort analysis:

```python
def compute_company_cohort_cashflows(
    company_id: str, 
    trades: List[Trade], 
    payments: List[Payment], 
    spends: List[Spend], 
    thresholds: List[Threshold], 
    churn: Optional[float] = None
) -> List[FundedCohort | Cohort]
```

**Function Architecture**:
1. **Data Consolidation**: Creates a unified view of all financial data by cohort month
2. **Period Processing**: Iterates through payment periods with actual and predicted data
3. **Revenue Sharing**: Applies complex business rules for fund collections
4. **IRR Calculation**: Computes investment returns for funded cohorts

#### **Data Consolidation Logic**

The function begins by creating a `ConsolidatedCohort` dataclass that unifies all related financial data:

```python
@dataclass
class ConsolidatedCohort:
    spend: Spend              # Marketing investment data
    trade: Optional[Trade]    # Revenue sharing terms (if funded)
    payments: List[Payment]   # Customer payment history
```

**Consolidation Process**:
- Groups all spends by cohort month as the foundation
- Associates trades (funding terms) with their respective cohorts
- Aggregates all payments by cohort month for analysis

This approach ensures that each cohort has a complete financial picture before processing begins.

#### **Payment Aggregation by Month**

The `_aggregate_payments_by_month` helper function creates a time-series structure:

```python
def _aggregate_payments_by_month(payments: List[Payment]) -> Dict:
    payments_by_month = defaultdict(list)
    for p in payments:
        month_key = p.payment_date.replace(day=1)  # Normalize to month start
        payments_by_month[month_key].append(p)
    return payments_by_month
```

**Purpose**: Transforms individual payment records into monthly aggregations for period-based analysis, essential for cohort retention analysis and churn modeling.

#### **Period Processing Engine**

The core calculation loop processes each payment period with sophisticated logic:

##### **Period Length Determination**
```python
num_periods_base = len(payments_by_month)
num_periods = max(num_periods_base, PREDICTION_LENGTH_MONTHS) if churn is not None and ch.trade else num_periods_base
```

**Logic**:
- **Actual Data Only**: Uses historical payment periods when no churn provided
- **Predictive Modeling**: Extends to 36 months when churn modeling is enabled for funded cohorts
- **Business Rationale**: Investors need long-term projections to evaluate fund performance

##### **Actual vs Predicted Period Detection**
```python
def _is_predicted_period(period_num: int, payments_by_month: Dict, churn: Optional[float]) -> bool:
    return False if churn is None else period_num >= len(payments_by_month)-1
```

**Decision Logic**: Periods beyond historical data become predicted when churn modeling is enabled.

##### **Payment Amount Calculation**

For each period, the system calculates payment amounts using different methods:

**Actual Periods** (Historical Data):
```python
payment_period_month = list(payments_by_month.keys())[period_num]
payments = payments_by_month[payment_period_month]
payment_sum = sum([p.amount for p in payments])
```

**Predicted Periods** (Churn-Based Forecasting):
```python
payment_period_month = latest_period_month + relativedelta(months = 1)
payment_sum = _compute_prediction_for_period(periods, churn)
```

The prediction algorithm implements exponential decay:
```python
def _compute_prediction_for_period(periods: List[FundedPeriod | PredictedFundedPeriod], churn: float) -> Decimal:
    return Decimal(periods[-1].payment * (1-churn))
```

**Mathematical Model**: `future_payment = last_payment × (1 - churn_rate)`

This creates a geometric decay series that models customer attrition over time.

#### **Revenue Sharing Algorithm**

For funded cohorts (those with trades), the system implements complex revenue sharing rules:

##### **Threshold Analysis**
```python
payment_percentage = payment_sum / ch.spend.spend
threshold = thresholds_by_period_num.get(period_num, None)
threshold_failed = threshold is not None and payment_percentage < threshold.minimum_payment_percent
```

**Business Logic**: If the payment-to-spend ratio falls below the defined threshold, the fund applies penalty terms.

##### **Share Calculation**
```python
share_applied = 1 if threshold_failed else ch.trade.sharing_percentage
collected = min(share_applied * payment_sum, ch.trade.cash_cap - cumulative_collected)
```

**Algorithm Components**:
1. **Threshold Override**: 100% collection (share_applied = 1) when performance is below threshold
2. **Normal Sharing**: Apply the negotiated sharing percentage for meeting targets
3. **Cash Cap Enforcement**: Respect the maximum collection limit across all periods

##### **Cash Cap Management**
```python
cumulative_collected += collected
period_capped = collected == ch.trade.cash_cap
capped = True if period_capped else capped

# Early termination for predicted periods
if _is_predicted_period(period_num, payments_by_month, churn) and capped:
    break
```

**Optimization**: Stops processing predicted periods once the cash cap is reached, improving performance for long-term projections.

#### **IRR (Internal Rate of Return) Calculation**

The system calculates investment returns using industry-standard IRR methodology:

```python
def _calculate_funded_cohort_irr(spend: float, periods: List[FundedPeriod | PredictedFundedPeriod]) -> Optional[float]:
    cash_flows = [-spend]  # Initial investment (negative cash flow)
    cash_flows += [p.payment for p in periods]  # Collection cash flows
    monthly_irr = npf.irr(cash_flows)
    annual_irr = (1 + monthly_irr) ** 12 - 1  # Convert to annualized rate
    return annual_irr
```

**Financial Mathematics**:
- Uses numpy-financial's IRR function for accurate calculation
- Converts monthly IRR to annualized equivalent using compound growth formula
- Models the fund's investment (-spend) and returns (+collections) over time

#### **Dual Cohort Model Creation**

The function creates different cohort types based on funding status:

##### **Funded Cohorts** (With Trades)
```python
FundedCohort(
    cohort_month=cohort_month,
    company_id=company_id,
    spend=ch.spend.spend,
    periods=periods,  # List[FundedPeriod | PredictedFundedPeriod]
    customers=customers,
    cumulative_payment=cumulative_payment,
    trade_id=ch.trade.id,
    sharing_percentage=ch.trade.sharing_percentage,
    cash_cap=ch.trade.cash_cap,
    cumulative_collected=cumulative_collected,
    capped=capped,
    annual_irr=annual_irr
)
```

##### **Unfunded Cohorts** (No Trades)
```python
Cohort(
    cohort_month=cohort_month,
    company_id=company_id,
    spend=ch.spend.spend,
    periods=periods,  # List[Period]
    customers=customers,
    cumulative_payment=cumulative_payment,
)
```

**Design Rationale**: Separate models allow for different analytics and reporting based on funding status, while maintaining type safety.

#### **Period-Level Data Structures**

The system creates detailed period records with different types based on context:

##### **Base Period** (Unfunded Cohorts)
```python
Period(
    period=period_num,
    month=payment_period_month,
    payment=payment_sum,
    cumulative_payment=cumulative_payment,
)
```

##### **Funded Period** (Actual Data)
```python
FundedPeriod(
    period=period_num,
    month=payment_period_month,
    payment=payment_sum,
    cumulative_payment=cumulative_payment,
    threshold_payment_percentage=threshold_payment_percentage,
    threshold_expected_payment=threshold_expected_payment,
    threshold_failed=threshold_failed,
    share_applied=share_applied,
    collected=collected,
    cumulative_collected=cumulative_collected,
    capped=period_capped,
)
```

##### **Predicted Funded Period** (Forecasted Data)
```python
PredictedFundedPeriod(
    # Inherits all FundedPeriod fields
    predicted=True  # Distinguishes predicted from actual data
)
```

**Business Value**: These metrics help evaluate the effectiveness of marketing spend and predict future profitability.

#### **Design Patterns and Architecture**

##### **Functional Decomposition**
The code follows clear functional decomposition with helper functions for specific calculations:
- `_aggregate_payments_by_month`: Time-series aggregation
- `_calculate_funded_cohort_irr`: Financial calculations
- `_is_predicted_period`: Business logic for data classification
- `_compute_prediction_for_period`: Churn modeling

##### **Type Safety and Validation**
- Comprehensive type hints using `Union` types for period variations
- Pydantic model integration for API validation
- Decimal precision for financial calculations to avoid floating-point errors

##### **Performance Considerations**
- Early termination when cash caps are reached
- Efficient dictionary lookups for thresholds
- Minimal object creation in calculation loops

#### **Business Model Implementation**

The calculation engine implements a sophisticated venture capital funding model:

1. **Customer Value Fund Concept**: The fund provides marketing capital to companies in exchange for a percentage of future customer payments
2. **Performance-Based Terms**: Threshold mechanisms ensure companies meet performance targets
3. **Risk Management**: Cash caps limit the fund's exposure per investment
4. **Predictive Analytics**: Churn modeling enables scenario planning and risk assessment

This calculation framework provides the foundation for portfolio-level analytics, enabling fund managers to evaluate performance, optimize allocation strategies, and make data-driven investment decisions.

### Data Models & Response Types

#### **Cohort Representation**
```python
class Cohort(BaseModel):
    cohort_month: date
    company_id: int
    spend: float
    periods: List[Period]
    customers: List[str]
    cumulative_payment: float
    funded: bool = False

class FundedCohort(Cohort):
    trade_id: int
    sharing_percentage: float
    cash_cap: float
    cumulative_collected: float
    periods: List[FundedPeriod | PredictedFundedPeriod]
    capped: bool
    annual_irr: float
    funded: bool = True
```

#### **Period-Level Details**
```python
class Period(BaseModel):
    period: int
    month: date
    payment: float
    cumulative_payment: float

class FundedPeriod(Period):
    threshold_payment_percentage: Optional[float]
    threshold_expected_payment: Optional[float]
    threshold_failed: bool
    share_applied: float
    collected: float
    cumulative_collected: float
    capped: bool

class PredictedFundedPeriod(FundedPeriod):
    predicted: bool = True
```

### Analytics Calculations

#### **Cashflow Projection**
The system supports two cashflow endpoints:
1. **Current Cashflows**: Based on actual payment data
2. **Predicted Cashflows**: Incorporates churn-based forecasting

**Input for Predictions**:
```python
class CashflowRequest(BaseModel):
    churn: float  # Monthly churn rate for predictions
```

---

## Future Investment Areas

### 1. **Scalability & Performance**

#### **Database Optimization**
- **Current State**: SQLite for development
- **Investment Needed**:
  - PostgreSQL migration for production
  - Database indexing optimization
  - Query performance monitoring
  - Connection pooling implementation

#### **Caching Strategy**
- **Problem**: Expensive cohort calculations on every request
- **Solutions**:
  - Redis caching for calculated cashflows
  - Background job processing for large calculations
  - Incremental calculation updates

#### **API Performance**
- **Current Limitations**: Synchronous processing
- **Improvements**:
  - Async database operations
  - Bulk operation endpoints
  - Pagination for large datasets
  - Response compression

### 2. **Advanced Analytics & ML**

#### **Predictive Modeling**
- **Current**: Simple churn-based projections
- **Enhancement Opportunities**:
  - Machine learning models for churn prediction
  - Cohort behavior clustering
  - Seasonal adjustment algorithms
  - External data integration (economic indicators)

#### **Real-time Analytics**
- **Investment Areas**:
  - Streaming data processing
  - Real-time dashboards
  - Alert systems for threshold breaches
  - Automated reporting

#### **Advanced Financial Metrics**
- **Additional Calculations**:
  - Risk-adjusted returns
  - Portfolio diversification metrics
  - Stress testing scenarios
  - Monte Carlo simulations

### 3. **Data Integration & ETL**

#### **Data Pipeline Architecture**
- **Current**: Manual CSV uploads
- **Future State**:
  - Automated data ingestion from company systems
  - API integrations with payment processors
  - Data validation and cleansing pipelines
  - Real-time sync capabilities

#### **Data Quality & Governance**
- **Investment Needs**:
  - Data validation frameworks
  - Audit trails for data changes
  - Data lineage tracking
  - Compliance reporting

### 4. **User Interface & Experience**

#### **Frontend Development**
- **Current State**: API-only (Swagger docs)
- **Investment Opportunities**:
  - React/Vue.js dashboard
  - Interactive data visualizations
  - Mobile-responsive design
  - User authentication & authorization

#### **Reporting & Visualization**
- **Enhanced Features**:
  - Automated report generation
  - Custom dashboard creation
  - Export capabilities (PDF, Excel)
  - Embedding analytics in external systems

### 5. **Security & Compliance**

#### **Authentication & Authorization**
- **Current Gap**: No authentication system
- **Implementation Needs**:
  - JWT-based authentication
  - Role-based access control (RBAC)
  - API key management
  - OAuth2 integration

#### **Data Security**
- **Investment Areas**:
  - Data encryption at rest and in transit
  - Audit logging for sensitive operations
  - GDPR compliance features
  - Data anonymization capabilities

#### **Financial Compliance**
- **Considerations**:
  - SOX compliance for financial data
  - Audit trail requirements
  - Data retention policies
  - Regulatory reporting features

### 6. **DevOps & Infrastructure**

#### **Deployment & Monitoring**
- **Current State**: Local development environment
- **Production Readiness**:
  - Container orchestration (Docker/Kubernetes)
  - CI/CD pipelines
  - Infrastructure as Code (Terraform)
  - Comprehensive monitoring (Prometheus/Grafana)

#### **Backup & Disaster Recovery**
- **Investment Needs**:
  - Automated backup strategies
  - Point-in-time recovery
  - Multi-region deployment
  - Disaster recovery testing

### 7. **Integration & Ecosystem**

#### **Third-party Integrations**
- **Potential Integrations**:
  - Accounting systems (QuickBooks, Xero)
  - CRM platforms (Salesforce, HubSpot)
  - Payment processors (Stripe, PayPal)
  - Business intelligence tools (Tableau, Looker)

#### **API Ecosystem**
- **Expansion Opportunities**:
  - Public API documentation
  - SDK development (Python, JavaScript)
  - Webhook support for real-time notifications
  - GraphQL endpoint for flexible queries

---

## Summary

The CVF Portfolio Management API demonstrates a well-architected system with clear separation of concerns, robust financial calculations, and a solid foundation for future growth. The technology choices (FastAPI, SQLAlchemy, Pandas) provide an excellent balance of developer productivity, performance, and maintainability.

Key strengths include:
- Comprehensive cohort analysis capabilities
- Type-safe API design with automatic documentation
- Sophisticated financial calculations (IRR, cashflow projections)
- Clean database schema with proper constraints
- Extensive testing coverage

The identified future investment areas provide a clear roadmap for scaling the system from a development prototype to a production-ready financial analytics platform capable of serving enterprise customers with demanding performance and compliance requirements.