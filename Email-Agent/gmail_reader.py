import base64
from bs4 import BeautifulSoup
from googleapiclient.errors import HttpError
import logging

logger = logging.getLogger(__name__)

def get_unread_emails(service, max_results=5):
    """Fetch unread emails from Gmail."""
    try:
        results = service.users().messages().list(
            userId='me', labelIds=['INBOX'], q='is:unread', maxResults=max_results
        ).execute()
        messages = results.get('messages', [])
        if not messages:
            return []

        email_data = []
        for msg in messages:
            msg_id = msg['id']
            msg_detail = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
            headers = msg_detail['payload']['headers']
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')

            # Extract body
            body = extract_body(msg_detail)
            email_data.append({
                'id': msg_id,
                'sender': sender,
                'subject': subject,
                'body': body
            })
        return email_data
    except HttpError as e:
        logger.error(f"Gmail API error: {e}")
        return []

def extract_body(msg_detail):
    """Extract plain text or HTML body from email payload."""
    payload = msg_detail['payload']
    body = ''
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain':
                data = part['body'].get('data')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
                    break
            elif part['mimeType'] == 'text/html':
                data = part['body'].get('data')
                if data:
                    html = base64.urlsafe_b64decode(data).decode('utf-8')
                    soup = BeautifulSoup(html, 'html.parser')
                    body = soup.get_text()
                    break
    else:
        if payload['mimeType'] == 'text/plain':
            data = payload['body'].get('data')
            if data:
                body = base64.urlsafe_b64decode(data).decode('utf-8')
        elif payload['mimeType'] == 'text/html':
            data = payload['body'].get('data')
            if data:
                html = base64.urlsafe_b64decode(data).decode('utf-8')
                soup = BeautifulSoup(html, 'html.parser')
                body = soup.get_text()
    return body.strip()