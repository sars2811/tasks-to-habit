from django.shortcuts import render
from google_apis import (
    get_authorization_url_for_signup,
    get_credentials_from_callback,
    get_authorization_url_for_signin,
)
from django.http import HttpResponseRedirect

from google_apis.main import get_user_info
from .models import GoogleOAuthState, User, GoogleOAuthCredentials
from django.contrib.auth import login
from django.utils import timezone


# Create your views here.
def signup_view(request):
    return render(request, "users/signup.html")


def signin_view(request):
    return render(request, "users/signin.html")


def google_oauth_initiate_signup(request):
    authorization_url, state = get_authorization_url_for_signup()
    GoogleOAuthState.objects.create(state=state)
    return HttpResponseRedirect(authorization_url)


def google_oauth_initiate_signin(request):
    authorization_url, state = get_authorization_url_for_signin()
    GoogleOAuthState.objects.create(state=state)
    return HttpResponseRedirect(authorization_url)


def google_oauth_callback(request):
    url = request.build_absolute_uri()
    storedState = GoogleOAuthState.objects.get(state=request.GET.get("state"))
    if (
        not storedState
        or storedState.is_used
        or timezone.now() > storedState.valid_until
    ):
        return HttpResponseRedirect("/user/signin")  # Invalid state, redirect to signin

    storedState.is_used = True
    storedState.save()

    credentials = get_credentials_from_callback(url)

    user_info = get_user_info(credentials)

    user, created = User.objects.get_or_create(auth_id=user_info["sub"])
    if created:
        user.set_unusable_password()
        user.save()

    default_credentials = {
        "access_token": credentials.token,
        "token_uri": credentials.token_uri,
        "scopes": ",".join(credentials.scopes),
    }
    if credentials.refresh_token:
        default_credentials["refresh_token"] = credentials.refresh_token
    OAuthCred, created = GoogleOAuthCredentials.objects.update_or_create(
        user=user,
        defaults=default_credentials,
    )

    login(request, user)
    return HttpResponseRedirect("/task/lists")
