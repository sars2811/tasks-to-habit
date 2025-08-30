from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.signup_view, name="signup"),
    path("signin/", views.signin_view, name="signin"),
    path(
        "initiate-google-oauth-singup/",
        views.google_oauth_initiate_signup,
        name="initiate_google_oauth_signup",
    ),
    path(
        "initiate-google-oauth-singin/",
        views.google_oauth_initiate_signin,
        name="initiate_google_oauth_signin",
    ),
    path(
        "googleoauth2callback/",
        views.google_oauth_callback,
        name="google_oauth2_callback",
    ),
]
