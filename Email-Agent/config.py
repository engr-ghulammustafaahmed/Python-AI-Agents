import os
from dotenv import load_dotenv

load_dotenv()

# MySQL
MYSQL_CONFIG = {
    'host': os.getenv('MYSQL_HOST', 'localhost'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
    'database': os.getenv('MYSQL_DATABASE'),
}

# Gmail API scopes
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Ollama
OLLAMA_MODEL = 'tinyllama'

# Agent settings
CHECK_INTERVAL_MINUTES = 1
SEND_AUTO = os.getenv('SEND_AUTO', 'False').lower() == 'true'  # default draft-only