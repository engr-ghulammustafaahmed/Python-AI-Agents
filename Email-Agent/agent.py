from gmail_reader import get_unread_emails
from gmail_sender import create_draft, send_email
from llm import generate_reply
from memory import store_memory
from config import SEND_AUTO
import logging

logger = logging.getLogger(__name__)

def process_email(service, email):
    """Process a single email: decide, generate reply, draft (or send)."""
    sender = email['sender']
    subject = email['subject']
    body = email['body']

    logger.info(f"Processing email from {sender} - Subject: {subject}")

    # Generate reply (or None)
    reply = generate_reply(sender, subject, body)
    if not reply:
        logger.info(f"No reply needed for email from {sender}.")
        # Mark as read? We'll archive it later (optional).
        return

    # Create a draft
    draft = create_draft(service, sender, subject, reply)
    if draft:
        # Optionally send immediately
        if SEND_AUTO:
            # Send the draft? Actually create_draft only creates draft; we can send separately.
            # For simplicity, we'll send a new email rather than sending draft.
            send_email(service, sender, subject, reply)
        # Store in memory
        store_memory(sender, subject, body, reply, category='replied')

    # Mark as read (remove UNREAD label) – optional but good
    service.users().messages().modify(
        userId='me', id=email['id'], body={'removeLabelIds': ['UNREAD']}
    ).execute()

def run_agent(service):
    """Main agent loop: fetch unread emails and process each."""
    emails = get_unread_emails(service, max_results=5)
    if not emails:
        logger.info("No unread emails found.")
        return
    for email in emails:
        process_email(service, email)