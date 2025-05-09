from django.urls import path
from . import views

urlpatterns = [
    path("customer_dashboard/", views.customer_dashboard_view, name="customer_dashboard"),
    path("password_change/", views.password_change_view, name="password_change")
]
