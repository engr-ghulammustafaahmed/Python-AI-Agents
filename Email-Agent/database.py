import mysql.connector
from mysql.connector import Error
from config import MYSQL_CONFIG
import logging

logger = logging.getLogger(__name__)

def get_connection():
    """Return a MySQL connection to the specified database."""
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        return conn
    except Error as e:
        logger.error(f"MySQL connection error: {e}")
        raise

def ensure_database_exists():
    """Check if the database exists, if not, create it automatically."""
    # Copy config so we don't modify the original
    config = MYSQL_CONFIG.copy()
    
    # Remove the 'database' key temporarily to connect to the server without a specific DB
    db_name = config.pop('database')
    
    try:
        # Connect to the MySQL server (not the specific database)
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        
        # Create the database if it doesn't exist
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        conn.commit()
        cursor.close()
        conn.close()
        logger.info(f"Database '{db_name}' ensured (created if it didn't exist).")
    except Error as e:
        logger.error(f"Failed to create/ensure database: {e}")
        raise

def init_db():
    """Create the memory table if it doesn't exist."""
    # 1. First, make sure the database exists
    ensure_database_exists()
    
    # 2. Now connect to the actual database and create the table
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memory (
            id INT AUTO_INCREMENT PRIMARY KEY,
            sender VARCHAR(255),
            subject VARCHAR(255),
            body TEXT,
            reply TEXT,
            category VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()
    logger.info("Database table 'memory' ensured.")