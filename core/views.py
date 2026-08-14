from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import ProductionRunForm, WorkOrderForm
from .models import (
    Product,
    ProductionLine,
    ProductionRun,
    Shift,
    WorkOrder,
)


ROLE_ROUTES = [
    ("Operator", "operator-dashboard"),
    ("Production Supervisor", "supervisor-dashboard"),
    ("Quality Specialist", "quality-dashboard"),
    ("Manufacturing Engineer", "engineer-dashboard"),
    ("Operations Manager", "manager-dashboard"),
    ("System Administrator", "system-administrator-dashboard"),
]


def user_can_create_work_orders(user):
    if user.is_superuser:
        return True

    return user.groups.filter(
        name__in=[
            "Production Supervisor",
            "System Administrator",
        ]
    ).exists()


def user_can_create_production_runs(user):
    if user.is_superuser:
        return True

    return user.groups.filter(
        name__in=[
            "Production Supervisor",
            "System Administrator",
        ]
    ).exists()


def user_can_start_production_runs(user):
    if user.is_superuser:
        return True

    return user.groups.filter(
        name__in=[
            "Production Supervisor",
            "System Administrator",
        ]
    ).exists()


def user_can_pause_production_runs(user):
    if user.is_superuser:
        return True

    return user.groups.filter(
        name__in=[
            "Production Supervisor",
            "System Administrator",
        ]
    ).exists()


def user_can_resume_production_runs(user):
    if user.is_superuser:
        return True

    return user.groups.filter(
        name__in=[
            "Production Supervisor",
            "System Administrator",
        ]
    ).exists()


def user_can_complete_production_runs(user):
    if user.is_superuser:
        return True

    return user.groups.filter(
        name__in=[
            "Production Supervisor",
            "System Administrator",
        ]
    ).exists()


@login_required
def dashboard_router(request):
    if request.user.is_superuser:
        return redirect("system-administrator-dashboard")

    user_groups = set(
        request.user.groups.values_list("name", flat=True)
    )

    for group_name, route_name in ROLE_ROUTES:
        if group_name in user_groups:
            return redirect(route_name)

    raise PermissionDenied(
        "Your account does not have a ForgeOps role assigned."
    )


@login_required
def role_dashboard(request, role_name):
    has_role = request.user.groups.filter(name=role_name).exists()

    if not request.user.is_superuser and not has_role:
        raise PermissionDenied(
            "You do not have permission to access this dashboard."
        )

    return render(
        request,
        "core/home.html",
        {
            "role_name": role_name,
            "dashboard_title": f"{role_name} Dashboard",
        },
    )


@login_required
def work_order_list(request):
    work_orders = WorkOrder.objects.select_related(
        "product"
    ).all()

    selected_status = request.GET.get("status", "")
    selected_product = request.GET.get("product", "")

    if selected_status:
        work_orders = work_orders.filter(
            status=selected_status
        )

    if selected_product:
        work_orders = work_orders.filter(
            product_id=selected_product
        )

    products = Product.objects.filter(
        is_active=True
    ).order_by("code")

    return render(
        request,
        "core/work_order_list.html",
        {
            "work_orders": work_orders,
            "products": products,
            "status_choices": WorkOrder.Status.choices,
            "selected_status": selected_status,
            "selected_product": selected_product,
            "can_create_work_orders": user_can_create_work_orders(
                request.user
            ),
        },
    )


@login_required
def work_order_detail(request, pk):
    work_order = get_object_or_404(
        WorkOrder.objects.select_related("product"),
        pk=pk,
    )

    production_runs = work_order.production_runs.select_related(
        "production_line__production_area__site",
        "shift",
    ).all()

    return render(
        request,
        "core/work_order_detail.html",
        {
            "work_order": work_order,
            "production_runs": production_runs,
            "can_create_work_orders": user_can_create_work_orders(
                request.user
            ),
            "can_create_production_runs": user_can_create_production_runs(
                request.user
            ),
        },
    )


@login_required
def work_order_create(request):
    if not user_can_create_work_orders(request.user):
        raise PermissionDenied(
            "You do not have permission to create Work Orders."
        )

    if request.method == "POST":
        form = WorkOrderForm(request.POST)

        if form.is_valid():
            work_order = form.save()

            return redirect(
                "work-order-detail",
                pk=work_order.pk,
            )
    else:
        form = WorkOrderForm()

    return render(
        request,
        "core/work_order_form.html",
        {
            "form": form,
        },
    )


@login_required
def production_run_list(request):
    production_runs = ProductionRun.objects.select_related(
        "work_order__product",
        "production_line__production_area__site",
        "shift",
    ).all()

    selected_status = request.GET.get("status", "")
    selected_work_order = request.GET.get("work_order", "")
    selected_production_line = request.GET.get(
        "production_line",
        "",
    )
    selected_shift = request.GET.get("shift", "")

    if selected_status:
        production_runs = production_runs.filter(
            status=selected_status
        )

    if selected_work_order:
        production_runs = production_runs.filter(
            work_order_id=selected_work_order
        )

    if selected_production_line:
        production_runs = production_runs.filter(
            production_line_id=selected_production_line
        )

    if selected_shift:
        production_runs = production_runs.filter(
            shift_id=selected_shift
        )

    work_orders = WorkOrder.objects.filter(
        is_active=True
    ).select_related("product").order_by("order_number")

    production_lines = ProductionLine.objects.filter(
        is_active=True
    ).select_related(
        "production_area__site"
    ).order_by(
        "production_area__site__code",
        "production_area__code",
        "code",
    )

    shifts = Shift.objects.filter(
        is_active=True
    ).order_by("name")

    return render(
        request,
        "core/production_run_list.html",
        {
            "production_runs": production_runs,
            "work_orders": work_orders,
            "production_lines": production_lines,
            "shifts": shifts,
            "status_choices": ProductionRun.Status.choices,
            "selected_status": selected_status,
            "selected_work_order": selected_work_order,
            "selected_production_line": selected_production_line,
            "selected_shift": selected_shift,
        },
    )


@login_required
def production_run_detail(request, pk):
    production_run = get_object_or_404(
        ProductionRun.objects.select_related(
            "work_order__product",
            "production_line__production_area__site",
            "shift",
        ),
        pk=pk,
    )

    return render(
        request,
        "core/production_run_detail.html",
        {
            "production_run": production_run,
            "can_start_production_runs": user_can_start_production_runs(
                request.user
            ),
            "can_pause_production_runs": user_can_pause_production_runs(
                request.user
            ),
            "can_resume_production_runs": user_can_resume_production_runs(
                request.user
            ),
            "can_complete_production_runs": (
                user_can_complete_production_runs(
                    request.user
                )
            ),
        },
    )


@login_required
def production_run_create(request, work_order_pk):
    if not user_can_create_production_runs(request.user):
        raise PermissionDenied(
            "You do not have permission to create Production Runs."
        )

    work_order = get_object_or_404(
        WorkOrder.objects.select_related("product"),
        pk=work_order_pk,
    )

    if request.method == "POST":
        form = ProductionRunForm(request.POST)

        if form.is_valid():
            production_run = form.save(commit=False)
            production_run.work_order = work_order
            production_run.save()

            return redirect(
                "production-run-detail",
                pk=production_run.pk,
            )
    else:
        form = ProductionRunForm()

    return render(
        request,
        "core/production_run_form.html",
        {
            "form": form,
            "work_order": work_order,
        },
    )


@login_required
def production_run_start(request, pk):
    if not user_can_start_production_runs(request.user):
        raise PermissionDenied(
            "You do not have permission to start Production Runs."
        )

    production_run = get_object_or_404(
        ProductionRun,
        pk=pk,
    )

    if request.method != "POST":
        raise PermissionDenied(
            "Production Runs may only be started using POST."
        )

    if production_run.status != ProductionRun.Status.PLANNED:
        raise PermissionDenied(
            "Only PLANNED Production Runs may be started."
        )

    active_run_exists = (
        ProductionRun.objects.filter(
            work_order=production_run.work_order,
            status=ProductionRun.Status.ACTIVE,
        )
        .exclude(pk=production_run.pk)
        .exists()
    )

    if active_run_exists:
        raise PermissionDenied(
            "This Work Order already has an ACTIVE Production Run."
        )

    production_run.status = ProductionRun.Status.ACTIVE
    production_run.started_at = timezone.now()
    production_run.ended_at = None

    production_run.full_clean()
    production_run.save(
        update_fields=[
            "status",
            "started_at",
            "ended_at",
            "updated_at",
        ]
    )

    return redirect(
        "production-run-detail",
        pk=production_run.pk,
    )


@login_required
def production_run_pause(request, pk):
    if not user_can_pause_production_runs(request.user):
        raise PermissionDenied(
            "You do not have permission to pause Production Runs."
        )

    production_run = get_object_or_404(
        ProductionRun,
        pk=pk,
    )

    if request.method != "POST":
        raise PermissionDenied(
            "Production Runs may only be paused using POST."
        )

    if production_run.status != ProductionRun.Status.ACTIVE:
        raise PermissionDenied(
            "Only ACTIVE Production Runs may be paused."
        )

    production_run.status = ProductionRun.Status.PAUSED

    production_run.full_clean()
    production_run.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    return redirect(
        "production-run-detail",
        pk=production_run.pk,
    )


@login_required
def production_run_resume(request, pk):
    if not user_can_resume_production_runs(request.user):
        raise PermissionDenied(
            "You do not have permission to resume Production Runs."
        )

    production_run = get_object_or_404(
        ProductionRun,
        pk=pk,
    )

    if request.method != "POST":
        raise PermissionDenied(
            "Production Runs may only be resumed using POST."
        )

    if production_run.status != ProductionRun.Status.PAUSED:
        raise PermissionDenied(
            "Only PAUSED Production Runs may be resumed."
        )

    active_run_exists = (
        ProductionRun.objects.filter(
            work_order=production_run.work_order,
            status=ProductionRun.Status.ACTIVE,
        )
        .exclude(pk=production_run.pk)
        .exists()
    )

    if active_run_exists:
        raise PermissionDenied(
            "This Work Order already has an ACTIVE Production Run."
        )

    production_run.status = ProductionRun.Status.ACTIVE

    production_run.full_clean()
    production_run.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    return redirect(
        "production-run-detail",
        pk=production_run.pk,
    )


@login_required
def production_run_complete(request, pk):
    if not user_can_complete_production_runs(request.user):
        raise PermissionDenied(
            "You do not have permission to complete Production Runs."
        )

    production_run = get_object_or_404(
        ProductionRun,
        pk=pk,
    )

    if request.method != "POST":
        raise PermissionDenied(
            "Production Runs may only be completed using POST."
        )

    if production_run.status != ProductionRun.Status.ACTIVE:
        raise PermissionDenied(
            "Only ACTIVE Production Runs may be completed."
        )

    production_run.status = ProductionRun.Status.COMPLETED
    production_run.ended_at = timezone.now()

    production_run.full_clean()
    production_run.save(
        update_fields=[
            "status",
            "ended_at",
            "updated_at",
        ]
    )

    return redirect(
        "production-run-detail",
        pk=production_run.pk,
    )