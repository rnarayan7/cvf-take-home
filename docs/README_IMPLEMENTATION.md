# CVF Portfolio Management System

A comprehensive cohort-based payment tracking and cashflow management system built with FastAPI and designed for Supabase.

## Overview

This system implements the CVF technical take-home assignment, providing:

1. **Part 1: Data Pipeline** - Cohort analysis, predictions, threshold checks, and cashflow calculations
2. **Part 2: Web Application** - Portfolio company portal with data upload, analytics, and real-time recalculations

## Features

### Core Data Pipeline
- **Cohort Analysis**: Convert raw payments into cohort matrices
- **Predictive Modeling**: Apply m0 and churn rates for future payment projections
- **Threshold Management**: Monitor payment performance against minimum thresholds
- **Cashflow Calculations**: Calculate CVF collections with sharing rates, caps, and threshold flips

### Web Application
- **Company Portal**: Multi-tenant interface for portfolio companies
- **Data Management**: CSV upload for payments and spend adjustments
- **Real-time Analytics**: Metrics, cohort tables, and cashflow visualizations
- **Administrative Controls**: Threshold management and trade configuration

### Technical Architecture
- **Backend**: FastAPI with SQLAlchemy ORM
- **Database**: PostgreSQL (Supabase) with Row-Level Security
- **Frontend**: Designed for Lovable with provided prompts
- **Authentication**: Supabase Auth with role-based access control

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository>
cd cvf-take-home/src
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy `.env.example` to `.env` and configure:

```env
# For local development (SQLite)
DATABASE_URL=sqlite:///./cvf.db
ENVIRONMENT=development

# For production (Supabase)
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
DATABASE_URL=postgresql://postgres:password@db.project.supabase.co:5432/postgres
```

### 4. Initialize Database

```bash
# For local development
python init_db.py

# For Supabase production
# Run supabase_setup.sql in your Supabase SQL editor
# Then run seed_data.sql for sample data
```

### 5. Start the API

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### 6. Test the API

```bash
python test_api.py
```

## API Endpoints

### Core Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `GET /companies/` - List companies
- `POST /companies/` - Create company

### Company Data Management

- `GET /companies/{id}/cohorts/` - List cohorts (spend plans)
- `POST /companies/{id}/cohorts/` - Create cohort
- `POST /companies/{id}/payments/upload` - Upload payments CSV
- `GET /companies/{id}/payments/` - List payments
- `GET /companies/{id}/trades/` - List trades
- `GET /companies/{id}/thresholds/` - List thresholds

### Analytics

- `GET /companies/{id}/metrics` - Get company metrics
- `GET /companies/{id}/cohorts_table` - Get cohort payment matrix
- `GET /companies/{id}/cashflows` - Get cashflow analysis
- `POST /companies/{id}/recalc` - Trigger recalculation

## Data Models

### Company
- Basic company information
- Links to all other entities

### Cohort
- Monthly S&M spend plans
- Cohort acquisition month
- Planned spend amount

### Payment
- Customer payment records
- Automatic cohort assignment
- Payment date and amount

### Trade
- Investment trade details
- Cohort start date
- Sharing percentage and cash cap

### Threshold
- Performance thresholds by payment period
- Minimum payment percentages
- Triggers 100% sharing when breached

## Calculation Logic

### Cohort Matrix Generation
1. Group customers by first payment month (cohort)
2. Calculate payment periods (months since cohort)
3. Aggregate payments by (cohort, period)

### Predictive Modeling
1. Apply m0 rate to estimate initial payment (% of spend)
2. Use churn rate for geometric decay of future payments
3. Preserve actual payments where available

### Threshold Analysis
1. Compare actual payments vs minimum thresholds
2. Generate failure mask for periods below threshold
3. Trigger 100% sharing rate for failed periods

### Cashflow Calculation
1. Apply sharing rates to cohort payments
2. Implement 100% sharing for threshold failures
3. Enforce cash cap limits per trade
4. Calculate cumulative collections

## Frontend Integration

### Lovable Setup

The system includes comprehensive Lovable prompts for building the frontend:

1. **Global App Scaffold** - Navigation, authentication, utilities
2. **Read UI** - Summary, cohorts table, cashflows visualization
3. **Write UI** - Data uploads, spend management, threshold editing
4. **Analytics** - Metrics dashboard, audit trails

### Key Features
- Role-based access (Company vs Admin)
- Real-time data updates
- CSV upload with validation
- Interactive cohort matrices
- Cashflow visualizations with cap progress

## Deployment

### Local Development
1. Use SQLite for quick setup
2. Run `python init_db.py` for sample data
3. Test with `python test_api.py`

### Supabase Production
1. Create Supabase project
2. Run `supabase_setup.sql` for schema
3. Run `seed_data.sql` for sample data
4. Configure `.env` with Supabase credentials
5. Deploy FastAPI to your preferred platform

### Environment Variables
```env
DATABASE_URL=postgresql://...  # Supabase connection string
SUPABASE_URL=https://...       # Supabase project URL
SUPABASE_KEY=...              # Supabase anon key
ENVIRONMENT=production        # Environment setting
```

## Security

### Row-Level Security (RLS)
- Company users can only access their own data
- Admin users have full access
- Automatic user profile creation on signup

### API Security
- Input validation with Pydantic
- SQL injection protection via SQLAlchemy
- CORS configuration for frontend integration

## Testing

### Unit Tests
Run the calculation functions with the provided test data from the Jupyter notebook.

### Integration Tests
```bash
python test_api.py
```

### Manual Testing
1. Use the Swagger UI at `http://localhost:8000/docs`
2. Test CSV uploads with sample data
3. Verify calculations match notebook results

## Architecture Decisions

### Database Design
- Normalized schema for flexibility
- Separate tables for different entity types
- Computed snapshots for performance

### Calculation Approach
- Pure functions for testability
- Pandas for efficient matrix operations
- Configurable parameters for different scenarios

### API Design
- RESTful endpoints
- Consistent response formats
- Comprehensive error handling

### Frontend Strategy
- Lovable for rapid prototyping
- Mock authentication for demo
- Progressive enhancement from read-only to full CRUD

## Future Enhancements

### Immediate
- Enhanced prediction scenarios (Best/Average/Worst)
- More sophisticated threshold rules
- Audit logging for data changes

### Advanced
- Real-time notifications
- Advanced analytics and reporting
- Integration with external data sources
- Mobile application support

## Support

For questions or issues:
1. Check the API documentation at `/docs`
2. Review test cases in `test_api.py`
3. Examine calculation logic in `calc.py`
4. Reference the original Jupyter notebook for requirements