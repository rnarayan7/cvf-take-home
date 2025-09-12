"""
CSV processing functionality for CVF API
"""

import pandas as pd
import io
from typing import List, Dict, Any
import structlog
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from src.python.models.models import Payment

logger = structlog.get_logger(__file__)


class CSVProcessor:
    """Handles CSV file processing and validation"""

    def __init__(self):
        self.logger = logger

    def validate_csv_file(self, file: UploadFile) -> None:
        """Validate that the uploaded file is a CSV"""
        if not file.filename:
            self.logger.error("No filename provided")
            raise HTTPException(status_code=400, detail="No file provided")

        if not file.filename.endswith(".csv"):
            self.logger.error("Invalid file format", filename=file.filename, expected="CSV")
            raise HTTPException(status_code=400, detail="File must be a CSV")

    async def read_csv_content(self, file: UploadFile) -> pd.DataFrame:
        """Read CSV file content into a pandas DataFrame"""
        try:
            content = await file.read()
            csv_string = content.decode("utf-8")
            df = pd.read_csv(io.StringIO(csv_string))

            self.logger.info(
                "CSV file read successfully", filename=file.filename, rows=len(df), columns=list(df.columns)
            )
            return df

        except UnicodeDecodeError as e:
            self.logger.error("File encoding error", filename=file.filename, error=str(e))
            raise HTTPException(status_code=400, detail="File must be UTF-8 encoded")

        except pd.errors.EmptyDataError:
            self.logger.error("Empty CSV file", filename=file.filename)
            raise HTTPException(status_code=400, detail="CSV file is empty")

        except Exception as e:
            self.logger.error("Failed to read CSV", filename=file.filename, error=str(e))
            raise HTTPException(status_code=400, detail="Invalid CSV format")

    def validate_required_columns(self, df: pd.DataFrame, required_columns: List[str]) -> None:
        """Validate that DataFrame contains all required columns"""
        missing_columns = [col for col in required_columns if col not in df.columns]

        if missing_columns:
            self.logger.error(
                "Missing required columns",
                found_columns=list(df.columns),
                required_columns=required_columns,
                missing_columns=missing_columns,
            )
            raise HTTPException(
                status_code=400, detail=f"CSV must contain columns: {required_columns}. Missing: {missing_columns}"
            )

        self.logger.info("Column validation passed", required_columns=required_columns)

    def validate_data_types(self, df: pd.DataFrame, column_types: Dict[str, str]) -> pd.DataFrame:
        """Validate and convert data types"""
        validated_df = df.copy()

        for column, expected_type in column_types.items():
            if column not in validated_df.columns:
                continue

            try:
                if expected_type == "datetime":
                    validated_df[column] = pd.to_datetime(validated_df[column])
                elif expected_type == "float":
                    validated_df[column] = pd.to_numeric(validated_df[column], errors="coerce")
                    # Check for NaN values after conversion
                    if validated_df[column].isna().any():
                        invalid_count = validated_df[column].isna().sum()
                        self.logger.warning("Invalid numeric values found", column=column, invalid_count=invalid_count)
                elif expected_type == "string":
                    validated_df[column] = validated_df[column].astype(str)

            except Exception as e:
                self.logger.error(
                    "Data type validation failed", column=column, expected_type=expected_type, error=str(e)
                )
                raise HTTPException(
                    status_code=400, detail=f"Invalid data type in column '{column}'. Expected: {expected_type}"
                )

        self.logger.info("Data type validation completed", column_types=column_types)
        return validated_df

    def process_payments_csv(self, company_id: int, df: pd.DataFrame, db: Session) -> List[Payment]:
        """Process payments CSV and create Payment objects"""
        self.logger.info("Processing payments CSV", company_id=company_id, row_count=len(df))

        from src.python.db.db_operations import DatabaseOperations
        db_ops = DatabaseOperations(db)

        # Validate company exists
        if not db_ops.companies.company_exists(company_id):
            self.logger.error("Company not found", company_id=company_id)
            raise HTTPException(status_code=404, detail="Company not found")

        payments_created = []
        errors = []

        for index, row in df.iterrows():
            try:
                # Calculate cohort month (first payment month for customer)
                existing_payments = db_ops.payments.get_customer_payments(company_id, str(row["customer_id"]))

                if existing_payments:
                    cohort_month = min(p.payment_date for p in existing_payments).replace(day=1)
                else:
                    cohort_month = row["payment_date"].replace(day=1)

                payment = db_ops.payments.create_payment(
                    company_id=company_id,
                    customer_id=str(row["customer_id"]),
                    payment_date=row["payment_date"],
                    cohort_month=cohort_month,
                    amount=float(row["amount"]),
                )

                payments_created.append(payment)

            except Exception as e:
                error_msg = f"Row {index + 1}: {str(e)}"
                errors.append(error_msg)
                self.logger.warning(
                    "Failed to process payment row", row_index=index + 1, error=str(e), row_data=row.to_dict()
                )

        if errors:
            self.logger.error(
                "Errors occurred during CSV processing", error_count=len(errors), errors=errors[:5]
            )  # Log first 5 errors
            raise HTTPException(
                status_code=400, detail=f"Failed to process {len(errors)} rows. First error: {errors[0]}"
            )

        self.logger.info("Payments processing completed", company_id=company_id, payments_created=len(payments_created))

        return payments_created


class PaymentsCSVProcessor(CSVProcessor):
    """Specialized processor for payments CSV files"""

    REQUIRED_COLUMNS = ["customer_id", "payment_date", "amount"]
    COLUMN_TYPES = {"customer_id": "string", "payment_date": "datetime", "amount": "float"}

    async def process_file(self, company_id: int, file: UploadFile, db: Session) -> Dict[str, Any]:
        """Process a payments CSV file end-to-end"""
        self.logger.info("Starting payments CSV processing", company_id=company_id, filename=file.filename)

        # Validate file format
        self.validate_csv_file(file)

        # Read CSV content
        df = await self.read_csv_content(file)

        # Validate columns
        self.validate_required_columns(df, self.REQUIRED_COLUMNS)

        # Validate and convert data types
        validated_df = self.validate_data_types(df, self.COLUMN_TYPES)

        # Process payments
        payments_created = self.process_payments_csv(company_id, validated_df, db)

        # Commit to database
        try:
            db.commit()
            self.logger.info(
                "Payments CSV processing completed successfully",
                company_id=company_id,
                filename=file.filename,
                payments_count=len(payments_created),
            )

            return {
                "message": f"Successfully uploaded {len(payments_created)} payments",
                "count": len(payments_created),
                "filename": file.filename,
            }

        except Exception as e:
            db.rollback()
            self.logger.error("Database commit failed", company_id=company_id, error=str(e))
            raise HTTPException(status_code=500, detail="Failed to save payments to database")


# Factory function for easy instantiation
def get_payments_csv_processor() -> PaymentsCSVProcessor:
    """Factory function to get a PaymentsCSVProcessor instance"""
    return PaymentsCSVProcessor()
