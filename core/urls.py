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
    path(
        "production-runs/",
        views.production_run_list,
        name="production-run-list",
    ),
    path(
        "production-runs/<int:pk>/",
        views.production_run_detail,
        name="production-run-detail",
    ),
    path(
        "production-runs/<int:pk>/start/",
        views.production_run_start,
        name="production-run-start",
    ),
    path(
        "production-runs/<int:pk>/pause/",
        views.production_run_pause,
        name="production-run-pause",
    ),
    path(
        "production-runs/<int:pk>/resume/",
        views.production_run_resume,
        name="production-run-resume",
    ),
    path(
        "production-runs/<int:pk>/complete/",
        views.production_run_complete,
        name="production-run-complete",
    ),
    path(
        "production-runs/<int:pk>/cancel/",
        views.production_run_cancel,
        name="production-run-cancel",
    ),
    path(
        "production-runs/<int:production_run_pk>/entries/new/",
        views.production_entry_create,
        name="production-entry-create",
    ),
    path(
        "production-runs/<int:production_run_pk>/downtime/new/",
        views.downtime_event_create,
        name="downtime-event-create",
    ),
    path(
        "downtime-events/<int:pk>/close/",
        views.downtime_event_close,
        name="downtime-event-close",
    ),
    path(
        "work-orders/<int:work_order_pk>/production-runs/new/",
        views.production_run_create,
        name="production-run-create",
    ),
]