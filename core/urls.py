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
    path(
        "work-orders/",
        views.work_order_list,
        name="work-order-list",
    ),
    path(
        "work-orders/new/",
        views.work_order_create,
        name="work-order-create",
    ),
    path(
        "work-orders/<int:pk>/",
        views.work_order_detail,
        name="work-order-detail",
    ),
]