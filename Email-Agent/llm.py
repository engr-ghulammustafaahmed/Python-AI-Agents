import ollama
from config import OLLAMA_MODEL
import logging

logger = logging.getLogger(__name__)

def generate_reply(sender, subject, body):
    """Generate a professional reply using TinyLlama."""
    try:
        # System message = The permanent rule (kept separate)
        # User message = The actual task
        messages = [
            {
                "role": "system",
                "content": "You are a professional email assistant. If an email is spam or promotional, reply with exactly the word NONE. Otherwise, write a short, polite, professional reply."
            },
            {
                "role": "user",
                "content": f"Reply to this email.\nSender: {sender}\nSubject: {subject}\nBody: {body}\n\nYour reply:"
            }
        ]
        
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=messages
        )
        reply = response['message']['content'].strip()
        
        # If the model still outputs "NONE", handle it
        if reply and 'NONE' in reply.upper():
            return None
        return reply
    except Exception as e:
        logger.error(f"Ollama error: {e}")
        return None