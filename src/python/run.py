#!/usr/bin/env python3
"""
CVF Portfolio Management API Server
Run script with automatic setup and configuration
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path
import structlog

logger = structlog.get_logger("run")

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
        logger.info("Please run: pip install -r requirements.txt")
        return False

def setup_environment():
    """Setup environment variables and configuration"""
    env_file = Path(".env")
    env_example = Path(".env.example")
    
    if not env_file.exists() and env_example.exists():
        logger.info("Creating .env file from template")
        with open(env_example) as f:
            content = f.read()
        
        # Set default SQLite for development
        content = content.replace(
            "DATABASE_URL=postgresql://postgres:your_password@db.your_project.supabase.co:5432/postgres",
            "DATABASE_URL=sqlite:///./cvf.db"
        )
        content = content.replace("ENVIRONMENT=development", "ENVIRONMENT=development")
        
        with open(env_file, 'w') as f:
            f.write(content)
        
        logger.info("Created .env file with SQLite configuration")
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
        logger.info("Environment variables loaded")
    except ImportError:
        logger.warning("python-dotenv not installed, using default settings")

def initialize_database():
    """Initialize database with tables and sample data"""
    try:
        from init_db import init_database
        logger.info("Initializing database")
        init_database()
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error("Database initialization failed", error=str(e))
        return False

def run_server(host="0.0.0.0", port=8000, reload=True, log_level="info"):
    """Start the FastAPI server with uvicorn"""
    try:
        import uvicorn
        logger.info("Starting CVF API server", host=host, port=port)
        logger.info("API Documentation available", docs_url=f"http://{host}:{port}/docs")
        
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=reload,
            log_level=log_level,
            access_log=True
        )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error("Server error", error=str(e))
        sys.exit(1)

def run_tests():
    """Run the API test suite"""
    try:
        logger.info("Running API tests")
        result = subprocess.run([sys.executable, "test_api.py"], capture_output=True, text=True)
        
        if result.returncode == 0:
            logger.info("All tests passed")
            if result.stdout:
                logger.info("Test output", output=result.stdout)
        else:
            logger.error("Some tests failed", 
                        stdout=result.stdout, 
                        stderr=result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        logger.error("Test execution failed", error=str(e))
        return False

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="CVF Portfolio Management API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to (default: 8000)")
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload")
    parser.add_argument("--log-level", default="info", choices=["debug", "info", "warning", "error"], help="Log level")
    parser.add_argument("--test", action="store_true", help="Run tests instead of starting server")
    parser.add_argument("--setup-only", action="store_true", help="Only setup environment and database, don't start server")
    parser.add_argument("--skip-db-init", action="store_true", help="Skip database initialization")
    
    args = parser.parse_args()
    
    logger.info("Starting CVF Portfolio Management API", 
                command=sys.argv,
                args=vars(args))
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Setup environment
    setup_environment()
    
    # Initialize database unless skipped
    if not args.skip_db_init:
        if not initialize_database():
            logger.warning("Database initialization failed, continuing anyway")
    
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
    run_server(
        host=args.host,
        port=args.port,
        reload=reload,
        log_level=args.log_level
    )

if __name__ == "__main__":
    main()