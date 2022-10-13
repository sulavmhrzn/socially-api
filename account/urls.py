from django.urls import path

from . import views

urlpatterns = [
    path("me", views.DashboardAPIView.as_view(), name="dashboard"),
]
