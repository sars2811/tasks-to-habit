import os
from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from users.models import GoogleOAuthCredentials

load_dotenv()

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
SCOPES = [
    "https://www.googleapis.com/auth/tasks.readonly",
    "https://www.googleapis.com/auth/userinfo.email",
    "openid",
]

CLIENT_CONFIG = {
    "web": {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
    }
}

REDIRECT_URI = "http://localhost:8000/user/googleoauth2callback"


def get_stored_credentials(user):
    try:
        creds_data = GoogleOAuthCredentials.objects.get(user=user)
        credentials = Credentials(
            token=creds_data.access_token,
            refresh_token=creds_data.refresh_token,
            token_uri=creds_data.token_uri,
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            scopes=SCOPES,
        )
        GoogleOAuthCredentials.objects.filter(
            user=user,
        ).update(
            access_token=credentials.token, refresh_token=credentials.refresh_token
        )
        return credentials
    except GoogleOAuthCredentials.DoesNotExist:
        return None


def get_credentials_object(access_token, refresh_token, token_uri):
    return Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri=token_uri,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        scopes=SCOPES,
    )


def get_authorization_url_for_signup():
    flow = Flow.from_client_config(
        client_config=CLIENT_CONFIG,
        scopes=SCOPES,
    )
    flow.redirect_uri = REDIRECT_URI

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )

    return authorization_url, state


def get_authorization_url_for_signin():
    flow = Flow.from_client_config(
        client_config=CLIENT_CONFIG,
        scopes=SCOPES,
    )
    flow.redirect_uri = REDIRECT_URI

    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="select_account",
    )

    return authorization_url, state


def get_credentials_from_callback(response_url):
    flow = Flow.from_client_config(
        client_config=CLIENT_CONFIG,
        scopes=SCOPES,
    )
    flow.redirect_uri = REDIRECT_URI
    flow.fetch_token(authorization_response=response_url)
    return flow.credentials


def get_user_info(access_token, refresh_token, token_uri):
    credentials = get_credentials_object(access_token, refresh_token, token_uri)
    oauth2_client = build("oauth2", "v2", credentials=credentials)
    user_info = oauth2_client.userinfo().get().execute()
    oauth2_client.close()
    return user_info


def get_google_tasks_list(user):
    credentials = get_stored_credentials(user)
    tasks_service = build("tasks", "v1", credentials=credentials)
    tasklists = tasks_service.tasklists().list().execute()
    tasks_service.close()
    return sorted(tasklists.get("items", []), key=lambda x: x.get("id", ""))


def get_tasks_in_tasklist(user, tasklist_id):
    credentials = get_stored_credentials(user)
    tasks_service = build("tasks", "v1", credentials=credentials)
    tasks = tasks_service.tasks().list(tasklist=tasklist_id).execute()
    tasks_service.close()
    return tasks.get("items", [])
