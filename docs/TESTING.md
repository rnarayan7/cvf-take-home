# CVF Test Suite

This directory contains comprehensive unit tests for the CVF Portfolio Management system, specifically focusing on the calculation functions in `calc.py`.

## Test Structure

```
tests/
├── __init__.py                # Package initialization
├── conftest.py               # Pytest fixtures and configuration
├── test_calc.py             # Main unit tests for calc.py functions
├── test_calc_edge_cases.py  # Edge cases and stress tests
└── README.md               # This file
```

## Test Coverage

The test suite covers all major functions in `calc.py`:

### Core Functions Tested
- `payment_df_to_cohort_df()` - Convert payment data to cohort matrix
- `apply_predictions_to_cohort_df()` - Apply predictive modeling
- `apply_threshold_to_cohort_df()` - Apply threshold checks
- `get_cvf_cashflows_df()` - Calculate CVF cashflows
- `calculate_ltv_cac_metrics()` - Calculate LTV/CAC metrics  
- `calculate_current_month_owed()` - Calculate current month amounts

### Test Categories

#### Unit Tests (`test_calc.py`)
- **Basic functionality** - Normal use cases with typical data
- **Data validation** - Correct handling of different data types
- **Business logic** - Accurate calculations and transformations
- **Error handling** - Graceful handling of invalid inputs

#### Edge Cases (`test_calc_edge_cases.py`)
- **Boundary conditions** - Zero values, empty data, extreme values
- **Data quality issues** - NaN values, duplicates, invalid dates
- **Performance** - Large datasets, memory efficiency
- **Stress testing** - Extreme parameter values

#### Integration Tests
- **Full pipeline** - End-to-end calculation workflows
- **Data consistency** - Type preservation through transformations
- **Cross-function compatibility** - Function output → input chains

## Running Tests

### Prerequisites
Install test dependencies:
```bash
pip install -r test-requirements.txt
```

### Basic Usage
```bash
# Run all tests
python run_tests.py

# Run all tests with coverage
python run_tests.py --coverage

# Run specific test categories  
python run_tests.py unit
python run_tests.py integration
python run_tests.py fast  # exclude slow tests

# Run specific test file
python run_tests.py tests/test_calc.py

# Run specific test class
python run_tests.py tests/test_calc.py::TestPaymentDfToCohortDf

# Run specific test method
python run_tests.py tests/test_calc.py::TestPaymentDfToCohortDf::test_basic_conversion
```

### Advanced Options
```bash
# Quiet mode
python run_tests.py --quiet

# No coverage reporting
python run_tests.py --no-coverage

# Parallel execution (requires pytest-xdist)
python run_tests.py --parallel 4
```

### Direct pytest Usage
```bash
# Basic test run
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=src/server --cov-report=html

# Run specific markers
pytest tests/ -m "not slow"  # Skip slow tests
pytest tests/ -m "unit"      # Only unit tests

# Generate coverage report
pytest tests/ --cov=src/server --cov-report=html --cov-report=term-missing
```

## Test Data

The test suite uses pytest fixtures defined in `conftest.py` to provide consistent test data:

- `sample_payment_data` - Realistic payment transaction data
- `sample_spend_data` - Marketing spend by cohort
- `sample_cohort_matrix` - Pre-calculated cohort payment matrix  
- `sample_predictions` - Prediction parameters (m0, churn rates)
- `sample_thresholds` - Threshold rules for different periods
- `sample_trades` - Trade definitions with sharing rates and caps

## Coverage Reports

After running tests with coverage, view the HTML report:
```bash
open htmlcov/index.html  # macOS
```

Or view the terminal summary for quick coverage overview.

## Test Organization

### Test Classes
Each major function has its own test class:
- `TestPaymentDfToCohortDf` - Payment matrix conversion tests
- `TestApplyPredictionsToCohortDf` - Prediction application tests
- `TestApplyThresholdToCohortDf` - Threshold checking tests
- `TestGetCvfCashflowsDf` - Cashflow calculation tests
- `TestCalculateLtvCacMetrics` - Metrics calculation tests
- `TestIntegrationScenarios` - End-to-end workflow tests

### Test Naming Convention
- `test_basic_*` - Happy path scenarios
- `test_*_failure` - Expected failure scenarios  
- `test_empty_*` - Edge cases with empty data
- `test_single_*` - Minimal data scenarios
- `test_edge_case_*` - Boundary conditions

## Key Test Scenarios

### Data Transformation Tests
- Payment data → cohort matrix conversion
- Date handling and period calculations
- Customer cohort assignment logic
- Payment aggregation by period

### Prediction Logic Tests
- m0 initial prediction application
- Geometric decay modeling  
- Scenario-based filtering
- Handling missing prediction parameters

### Business Rule Tests
- Threshold breach detection
- Sharing rate calculations (base vs. 100%)
- Cash cap enforcement
- Multiple trades per cohort

### Financial Calculation Tests
- LTV/CAC metrics computation
- MOIC calculations
- Current month owed calculations
- Cumulative collection tracking

## Contributing to Tests

When adding new functions to `calc.py`:

1. **Add fixtures** - Create representative test data in `conftest.py`
2. **Add unit tests** - Test normal usage in `test_calc.py`
3. **Add edge cases** - Test boundaries in `test_calc_edge_cases.py`
4. **Add integration tests** - Test interaction with other functions
5. **Update documentation** - Document new test scenarios

### Test Writing Guidelines
- **One concept per test** - Each test should verify one specific behavior
- **Descriptive names** - Test names should clearly describe what is being tested
- **Arrange-Act-Assert** - Structure tests with clear setup, execution, and verification
- **Use fixtures** - Leverage pytest fixtures for consistent test data
- **Test edge cases** - Include boundary conditions and error scenarios

## Performance Testing

Some tests are marked with `@pytest.mark.slow` for performance testing:
- Large dataset handling
- Memory efficiency verification
- Computation time scaling

Skip slow tests during development:
```bash
python run_tests.py fast
```

## Debugging Failed Tests

For debugging test failures:
```bash
# Run with more detailed output
pytest tests/test_calc.py::TestPaymentDfToCohortDf::test_basic_conversion -vvs

# Drop into debugger on failure
pytest tests/ --pdb

# Run only failed tests from last run
pytest tests/ --lf
```