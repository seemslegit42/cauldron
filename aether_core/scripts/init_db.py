#!/usr/bin/env python3
"""
Database Initialization Script for AetherCore

This script initializes the database tables for AetherCore.
"""

import os
import sys
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import database models
from config.database import Base
from models.database_models import Agent, Task, HITLRequest, Message

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def init_db():
    """Initialize the database"""
    try:
        # Get database URL from environment
        db_user = os.getenv("DB_USER", "postgres")
        db_password = os.getenv("DB_PASSWORD", "cauldron_postgres_password")
        db_host = os.getenv("DB_HOST", "localhost")
        db_port = os.getenv("DB_PORT", "5432")
        db_name = os.getenv("DB_NAME", "aether_core")
        
        # Create database URL
        database_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        
        # Create engine
        engine = create_engine(database_url)
        
        # Create tables
        Base.metadata.create_all(engine)
        
        logger.info("Database tables created successfully")
        
        # Create session
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Check if tables were created
        tables = [
            "agents",
            "tasks",
            "hitl_requests",
            "messages"
        ]
        
        for table in tables:
            result = session.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')")
            exists = result.scalar()
            logger.info(f"Table '{table}' exists: {exists}")
        
        session.close()
        
        return True
        
    except SQLAlchemyError as e:
        logger.error(f"Error initializing database: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Initializing AetherCore database...")
    success = init_db()
    
    if success:
        logger.info("Database initialization completed successfully")
        sys.exit(0)
    else:
        logger.error("Database initialization failed")
        sys.exit(1)