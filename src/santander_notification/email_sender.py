import os
import base64
from email.message import EmailMessage
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from dotenv import load_dotenv

load_dotenv()

# If modifying these scopes, delete the token.json file
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


def get_gmail_service():
    """
    Authenticate and get Gmail API service.

    Returns:
        A Gmail API service object or None if authentication fails
    """
    creds = None
    token_path = Path("token.json")
    credentials_path = Path("credentials.json")

    # Check if token.json exists with stored credentials
    if token_path.exists():
        creds = Credentials.from_authorized_user_info(
            info=load_json(token_path), scopes=SCOPES
        )

    # If credentials don't exist or are invalid, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Check if credentials.json exists
            if not credentials_path.exists():
                print("Error: credentials.json file not found.")
                print("1. Go to https://console.cloud.google.com/")
                print("2. Create a project and enable the Gmail API")
                print("3. Create OAuth credentials and download as credentials.json")
                print("4. Place credentials.json in the project directory")
                return None

            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for future runs
        save_json(
            token_path,
            {
                "token": creds.token,
                "refresh_token": creds.refresh_token,
                "token_uri": creds.token_uri,
                "client_id": creds.client_id,
                "client_secret": creds.client_secret,
                "scopes": creds.scopes,
            },
        )

    # Return Gmail API service
    try:
        service = build("gmail", "v1", credentials=creds)
        return service
    except Exception as e:
        print(f"Error building Gmail service: {e}")
        return None


def load_json(file_path):
    """Load JSON from a file."""
    import json

    with open(file_path, "r") as file:
        return json.load(file)


def save_json(file_path, data):
    """Save data as JSON to a file."""
    import json

    with open(file_path, "w") as file:
        json.dump(data, file)


def send_notification_email(subject, message_body):
    """
    Send an email notification with the specified subject and message body using Gmail API.

    Args:
        subject (str): Email subject line
        message_body (str): Content of the email

    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    # Get recipient email from environment variables or use placeholder
    recipient_email = os.getenv("RECIPIENT_EMAIL")

    # Check if recipient email is set
    if not recipient_email:
        print("Error: RECIPIENT_EMAIL environment variable must be set.")
        print("Set it in your .env file or environment variables.")
        return False

    try:
        # Get Gmail API service
        service = get_gmail_service()
        if not service:
            return False

        # Create the email message
        message = EmailMessage()
        message.set_content(message_body)
        message["To"] = recipient_email
        message["Subject"] = subject

        # Encode the message for the Gmail API
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        # Create the message for the API
        gmail_message = {"raw": encoded_message}

        # Send the message
        send_message = (
            service.users().messages().send(userId="me", body=gmail_message).execute()
        )

        print(
            f"Email notification sent to {recipient_email} (Message ID: {send_message['id']})"
        )
        return True

    except HttpError as error:
        print(f"Gmail API error occurred: {error}")
        return False
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


if __name__ == "__main__":
    # Test the email functionality
    test_subject = "Santander Cycle Station Alert"
    test_body = "This is a test email from your Santander Cycle notification app using the Gmail API."
    send_notification_email(test_subject, test_body)
