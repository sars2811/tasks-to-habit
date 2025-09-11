from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="habits_index"),
]
