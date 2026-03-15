"""
Google Sheets Integration Service
Handles OAuth flow and data import from Google Sheets
"""
import os
import logging
from datetime import datetime, timezone
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from django.conf import settings

logger = logging.getLogger(__name__)

# Google Sheets OAuth Scopes
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]

# Get redirect URI from environment or use default
def get_redirect_uri():
    frontend_url = os.environ.get('REACT_APP_BACKEND_URL', 'https://private-analyst.preview.emergentagent.com')
    return f"{frontend_url}/api/integrations/google-sheets/callback"


def get_google_credentials():
    """Get Google OAuth credentials from environment"""
    client_id = os.environ.get('GOOGLE_SHEETS_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_SHEETS_CLIENT_SECRET')
    
    if not client_id or not client_secret:
        return None
    
    return {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token"
        }
    }


def create_oauth_flow(state=None):
    """Create Google OAuth flow"""
    credentials = get_google_credentials()
    if not credentials:
        raise ValueError("Google Sheets credentials not configured")
    
    flow = Flow.from_client_config(
        credentials,
        scopes=SCOPES,
        redirect_uri=get_redirect_uri(),
        state=state
    )
    return flow


def get_authorization_url(user_id):
    """Generate OAuth authorization URL"""
    flow = create_oauth_flow()
    
    # Generate authorization URL with state containing user_id
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        prompt='consent',
        include_granted_scopes='true',
        state=str(user_id)
    )
    
    return authorization_url, state


def exchange_code_for_tokens(code, state):
    """Exchange authorization code for tokens"""
    import warnings
    
    flow = create_oauth_flow(state=state)
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        flow.fetch_token(code=code)
    
    creds = flow.credentials
    
    # Validate scopes
    required_scopes = {"https://www.googleapis.com/auth/spreadsheets.readonly"}
    granted_scopes = set(creds.scopes or [])
    
    if not required_scopes.issubset(granted_scopes):
        missing = required_scopes - granted_scopes
        logger.error(f"Missing required sheets scopes: {missing}")
        raise ValueError(f"Missing required scopes: {', '.join(missing)}")
    
    return creds


def build_credentials_from_token(token_data):
    """Build Credentials object from stored token data"""
    creds = Credentials(
        token=token_data.get('access_token'),
        refresh_token=token_data.get('refresh_token'),
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ.get('GOOGLE_SHEETS_CLIENT_ID'),
        client_secret=os.environ.get('GOOGLE_SHEETS_CLIENT_SECRET'),
        scopes=SCOPES
    )
    return creds


def refresh_credentials_if_needed(creds, token_data):
    """Refresh credentials if expired"""
    expires_at = token_data.get('expires_at')
    
    if expires_at:
        if isinstance(expires_at, str):
            expires_at = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
        
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        if datetime.now(timezone.utc) >= expires_at:
            creds.refresh(GoogleRequest())
            return creds, True
    
    return creds, False


def get_sheets_service(token_data):
    """Get Google Sheets service instance"""
    creds = build_credentials_from_token(token_data)
    creds, refreshed = refresh_credentials_if_needed(creds, token_data)
    
    service = build('sheets', 'v4', credentials=creds)
    return service, creds if refreshed else None


def list_spreadsheets(token_data):
    """List user's spreadsheets from Google Drive"""
    from googleapiclient.discovery import build
    
    creds = build_credentials_from_token(token_data)
    creds, _ = refresh_credentials_if_needed(creds, token_data)
    
    # Build Drive service to list files
    drive_service = build('drive', 'v3', credentials=creds)
    
    # Query for spreadsheets only
    results = drive_service.files().list(
        q="mimeType='application/vnd.google-apps.spreadsheet'",
        pageSize=50,
        fields="files(id, name, createdTime, modifiedTime)"
    ).execute()
    
    return results.get('files', [])


def get_spreadsheet_metadata(token_data, spreadsheet_id):
    """Get spreadsheet metadata including sheet names"""
    service, _ = get_sheets_service(token_data)
    
    spreadsheet = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    
    sheets = []
    for sheet in spreadsheet.get('sheets', []):
        props = sheet.get('properties', {})
        grid = props.get('gridProperties', {})
        sheets.append({
            'id': props.get('sheetId'),
            'title': props.get('title'),
            'index': props.get('index'),
            'row_count': grid.get('rowCount'),
            'column_count': grid.get('columnCount')
        })
    
    return {
        'id': spreadsheet.get('spreadsheetId'),
        'title': spreadsheet.get('properties', {}).get('title'),
        'sheets': sheets
    }


def read_sheet_data(token_data, spreadsheet_id, sheet_name=None, range_notation=None):
    """Read data from a Google Sheet"""
    service, _ = get_sheets_service(token_data)
    
    # Build range - default to first sheet if not specified
    if range_notation:
        data_range = range_notation
    elif sheet_name:
        data_range = f"'{sheet_name}'"
    else:
        data_range = 'Sheet1'
    
    result = service.spreadsheets().values().get(
        spreadsheetId=spreadsheet_id,
        range=data_range
    ).execute()
    
    values = result.get('values', [])
    
    if not values:
        return [], []
    
    # First row is headers
    headers = values[0] if values else []
    data = values[1:] if len(values) > 1 else []
    
    # Normalize data rows to match header length
    normalized_data = []
    for row in data:
        normalized_row = row + [''] * (len(headers) - len(row))
        normalized_data.append(normalized_row[:len(headers)])
    
    return headers, normalized_data


def revoke_token(token_data):
    """Revoke Google OAuth token"""
    import requests
    
    access_token = token_data.get('access_token')
    if access_token:
        requests.post(
            'https://oauth2.googleapis.com/revoke',
            params={'token': access_token},
            headers={'content-type': 'application/x-www-form-urlencoded'}
        )
