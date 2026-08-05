from django.urls import path

from . import views


urlpatterns = [
    path("", views.dashboard_router, name="dashboard-router"),

    path(
        "operator/",
        views.role_dashboard,
        {"role_name": "Operator"},
        name="operator-dashboard",
    ),
    path(
        "supervisor/",
        views.role_dashboard,
        {"role_name": "Production Supervisor"},
        name="supervisor-dashboard",
    ),
    path(
        "quality/",
        views.role_dashboard,
        {"role_name": "Quality Specialist"},
        name="quality-dashboard",
    ),
    path(
        "engineering/",
        views.role_dashboard,
        {"role_name": "Manufacturing Engineer"},
        name="engineer-dashboard",
    ),
    path(
        "management/",
        views.role_dashboard,
        {"role_name": "Operations Manager"},
        name="manager-dashboard",
    ),
    path(
        "system-administration/",
        views.role_dashboard,
        {"role_name": "System Administrator"},
        name="system-administrator-dashboard",
    ),
]