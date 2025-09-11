from django.urls import path
from . import views

urlpatterns = [
    path("lists/", views.get_task_lists_view, name="get_task_lists"),
]
