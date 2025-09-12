"""
Test script for CSV processor functionality
"""

import tempfile
import io
import asyncio
from fastapi import UploadFile
import pandas as pd
import structlog
from unittest.mock import Mock, MagicMock

from csv_processor import PaymentsCSVProcessor, get_payments_csv_processor
from models import Company, Payment

logger = structlog.get_logger("test_csv_processor")


def create_test_csv_content(data: list) -> str:
    """Create CSV content from list of dictionaries"""
    df = pd.DataFrame(data)
    return df.to_csv(index=False)


def create_mock_upload_file(filename: str, content: str) -> UploadFile:
    """Create a mock UploadFile for testing"""
    file_like = io.BytesIO(content.encode('utf-8'))
    return UploadFile(filename=filename, file=file_like)


async def test_valid_payments_csv():
    """Test processing a valid payments CSV"""
    logger.info("Testing valid payments CSV processing")
    
    # Create test data
    test_data = [
        {"customer_id": "cust_001", "payment_date": "2024-01-15", "amount": 1000.50},
        {"customer_id": "cust_002", "payment_date": "2024-01-20", "amount": 750.25},
        {"customer_id": "cust_001", "payment_date": "2024-02-15", "amount": 900.00},
    ]
    
    csv_content = create_test_csv_content(test_data)
    upload_file = create_mock_upload_file("test_payments.csv", csv_content)
    
    # Create processor
    processor = PaymentsCSVProcessor()
    
    try:
        # Test CSV reading
        df = await processor.read_csv_content(upload_file)
        logger.info("CSV read successfully", shape=df.shape, columns=list(df.columns))
        
        # Test column validation
        processor.validate_required_columns(df, processor.REQUIRED_COLUMNS)
        logger.info("Column validation passed")
        
        # Test data type validation
        validated_df = processor.validate_data_types(df, processor.COLUMN_TYPES)
        logger.info("Data type validation passed", 
                   dtypes=validated_df.dtypes.to_dict())
        
        return True
        
    except Exception as e:
        logger.error("Test failed", error=str(e))
        return False


async def test_invalid_csv_format():
    """Test handling of invalid CSV format"""
    logger.info("Testing invalid CSV format handling")
    
    # Create invalid content
    invalid_content = "This is not a CSV file content"
    upload_file = create_mock_upload_file("invalid.csv", invalid_content)
    
    processor = PaymentsCSVProcessor()
    
    try:
        df = await processor.read_csv_content(upload_file)
        logger.error("Should have failed but didn't")
        return False
    except Exception as e:
        logger.info("Correctly caught invalid format", error=str(e))
        return True


async def test_missing_columns():
    """Test handling of missing required columns"""
    logger.info("Testing missing columns handling")
    
    # Create CSV with missing columns
    test_data = [
        {"customer_id": "cust_001", "amount": 1000.50},  # Missing payment_date
        {"customer_id": "cust_002", "amount": 750.25},
    ]
    
    csv_content = create_test_csv_content(test_data)
    upload_file = create_mock_upload_file("missing_cols.csv", csv_content)
    
    processor = PaymentsCSVProcessor()
    
    try:
        df = await processor.read_csv_content(upload_file)
        processor.validate_required_columns(df, processor.REQUIRED_COLUMNS)
        logger.error("Should have failed but didn't")
        return False
    except Exception as e:
        logger.info("Correctly caught missing columns", error=str(e))
        return True


def test_non_csv_file():
    """Test handling of non-CSV file extensions"""
    logger.info("Testing non-CSV file handling")
    
    upload_file = create_mock_upload_file("document.txt", "some content")
    processor = PaymentsCSVProcessor()
    
    try:
        processor.validate_csv_file(upload_file)
        logger.error("Should have failed but didn't")
        return False
    except Exception as e:
        logger.info("Correctly rejected non-CSV file", error=str(e))
        return True


async def test_factory_function():
    """Test the factory function"""
    logger.info("Testing factory function")
    
    processor = get_payments_csv_processor()
    
    if isinstance(processor, PaymentsCSVProcessor):
        logger.info("Factory function works correctly")
        return True
    else:
        logger.error("Factory function returned wrong type")
        return False


async def main():
    """Run all tests"""
    logger.info("Starting CSV Processor Test Suite")
    
    tests = [
        ("Valid CSV Processing", test_valid_payments_csv()),
        ("Invalid CSV Format", test_invalid_csv_format()),
        ("Missing Columns", test_missing_columns()),
        ("Non-CSV File", test_non_csv_file()),
        ("Factory Function", test_factory_function()),
    ]
    
    results = []
    for test_name, test_coro in tests:
        logger.info("Running test", test_name=test_name)
        try:
            if asyncio.iscoroutine(test_coro):
                result = await test_coro
            else:
                result = test_coro
            results.append((test_name, result))
            status = "✅ PASSED" if result else "❌ FAILED"
            logger.info("Test completed", test_name=test_name, status=status)
        except Exception as e:
            logger.error("Test error", test_name=test_name, error=str(e))
            results.append((test_name, False))
    
    # Summary
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    logger.info("Test suite completed", 
               passed=passed, 
               total=total, 
               success_rate=f"{passed/total*100:.1f}%")
    
    if passed == total:
        logger.info("All tests passed! 🎉")
    else:
        logger.warning("Some tests failed", failed=total-passed)
    
    return passed == total


if __name__ == "__main__":
    asyncio.run(main())