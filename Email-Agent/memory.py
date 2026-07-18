from database import get_connection
import logging

logger = logging.getLogger(__name__)

def store_memory(sender, subject, body, reply, category='general'):
    """Save an email and its reply to MySQL."""
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        INSERT INTO memory (sender, subject, body, reply, category)
        VALUES (%s, %s, %s, %s, %s)
    """
    try:
        cursor.execute(query, (sender, subject, body, reply, category))
        conn.commit()
        logger.info("Memory stored successfully.")
    except Exception as e:
        logger.error(f"Failed to store memory: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()