import base64
from email.mime.text import MIMEText
from googleapiclient.errors import HttpError
import logging

logger = logging.getLogger(__name__)

def create_draft(service, to, subject, body):
    """Create a draft email."""
    try:
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        draft = {
            'message': {
                'raw': raw
            }
        }
        draft = service.users().drafts().create(userId='me', body=draft).execute()
        logger.info(f"Draft created with ID: {draft['id']}")
        return draft
    except HttpError as e:
        logger.error(f"Failed to create draft: {e}")
        return None

def send_email(service, to, subject, body):
    """Send email directly (optional)."""
    try:
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        sent_msg = service.users().messages().send(userId='me', body={'raw': raw}).execute()
        logger.info(f"Email sent to {to}, message ID: {sent_msg['id']}")
        return sent_msg
    except HttpError as e:
        logger.error(f"Failed to send email: {e}")
        return None