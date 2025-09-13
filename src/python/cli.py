#!/usr/bin/env python3
"""
CVF Portfolio Management API Server
Run script with automatic setup and configuration
"""

import sys
import subprocess
import argparse
from pathlib import Path
import structlog


logger = structlog.get_logger(__file__)


def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import fastapi
        import uvicorn
        import sqlalchemy
        import pandas

        logger.info("Dependencies check passed")
        return True
    except ImportError as e:
        logger.error("Missing dependency", error=str(e))
        logger.info("Please run: uv pip install -r requirements.txt")
        return False


def setup_environment():
    """Setup environment variables and configuration"""
    env_file = Path(".env")
    env_example = Path(".env.example")

    # Load environment variables
    try:
        from dotenv import load_dotenv

        load_dotenv()
        logger.info("Environment variables loaded")
    except ImportError:
        logger.warning("python-dotenv not installed, using default settings")


def initialize_database():
    """Initialize database with tables"""
    from src.python.db.database import init_database

    logger.info("Initializing database")
    init_database()
    logger.info("Database initialized successfully")


def seed_database(force_recreate=False):
    """Seed database with sample data"""
    from src.python.db.seed_data import seed_database
    
    logger.info("Seeding database with sample data", force_recreate=force_recreate)
    seed_database(force_recreate=force_recreate)
    logger.info("Database seeding completed")


def run_server(host="0.0.0.0", port=8000, reload=True, log_level="info"):
    """Start the FastAPI server with uvicorn"""
    try:
        import uvicorn

        logger.info("Starting CVF API server", host=host, port=port)
        logger.info("API Documentation available", docs_url=f"http://{host}:{port}/docs")

        uvicorn.run("src.python.main:app", host=host, port=port, reload=reload, log_level=log_level, access_log=True)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error("Server error", error=str(e))
        sys.exit(1)


def run_tests():
    """Run the API test suite"""
    logger.info("Running API tests")
    result = subprocess.run([sys.executable, "test_api.py"], capture_output=True, text=True)

    if result.returncode == 0:
        logger.info("All tests passed")
        if result.stdout:
            logger.info("Test output", output=result.stdout)
    else:
        logger.error("Some tests failed", stdout=result.stdout, stderr=result.stderr)
        raise RuntimeError("Some tests failed")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="CVF Portfolio Management API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to (default: 8000)")
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload")
    parser.add_argument("--log-level", default="info", choices=["debug", "info", "warning", "error"], help="Log level")
    parser.add_argument("--test", action="store_true", help="Run tests instead of starting server")
    parser.add_argument(
        "--setup-only", action="store_true", help="Only setup environment and database, don't start server"
    )
    parser.add_argument("--skip-db-init", action="store_true", help="Skip database initialization")
    parser.add_argument("--seed", action="store_true", help="Seed database with sample data")
    parser.add_argument("--seed-force", action="store_true", help="Force recreate seed data (clears existing data)")

    args = parser.parse_args()

    logger.info("Starting CVF Portfolio Management API", command=sys.argv, args=vars(args))

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Setup environment
    setup_environment()

    # Initialize database unless skipped
    if not args.skip_db_init:
        initialize_database()

    # Seed database if requested
    if args.seed or args.seed_force:
        seed_database(force_recreate=args.seed_force)

    # Run tests if requested
    if args.test:
        if not run_tests():
            sys.exit(1)
        return

    # Exit if setup-only
    if args.setup_only:
        logger.info("Setup completed successfully")
        return

    # Start server
    reload = not args.no_reload
    run_server(host=args.host, port=args.port, reload=reload, log_level=args.log_level)


if __name__ == "__main__":
    main()
