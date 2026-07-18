import sys
import schedule
import time
import logging
from gmail_auth import authenticate_gmail
from agent import run_agent
from database import init_db
from config import CHECK_INTERVAL_MINUTES

# --- Fix for Windows Emoji/Unicode logging ---
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Setup logging with UTF-8 support
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/agent.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# --- Main function ---
def main():
    logger.info("Initializing database...")
    init_db()

    logger.info("Authenticating Gmail...")
    service = authenticate_gmail()

    logger.info(f"Starting agent. Checking every {CHECK_INTERVAL_MINUTES} minute(s).")
    schedule.every(CHECK_INTERVAL_MINUTES).minutes.do(run_agent, service)

    # Run once immediately
    run_agent(service)

    while True:
        schedule.run_pending()
        time.sleep(10)

if __name__ == "__main__":
    main()