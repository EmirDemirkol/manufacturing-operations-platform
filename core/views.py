from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import (
    DowntimeEventForm,
    ProductionEntryForm,
    ProductionRunForm,
    QualityInspectionCompleteForm,
    QualityInspectionCreateForm,
    WorkOrderForm,
)
from .models import (
    DowntimeEvent,
    Product,
    ProductionEntry,
    ProductionLine,
    ProductionRun,
    QualityInspection,
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


def user_can_cancel_production_runs(user):
    if user.is_superuser:
        return True

    return user.groups.filter(
        name__in=[
            "Production Supervisor",
            "System Administrator",
        ]
    ).exists()


def user_can_create_production_entries(user):
    if user.is_superuser:
        return True

    return user.groups.filter(
        name__in=[
            "Operator",
            "Production Supervisor",
            "System Administrator",
        ]
    ).exists()


def user_can_manage_downtime_events(user):
    if user.is_superuser:
        return True

    return user.groups.filter(
        name__in=[
            "Operator",
            "Production Supervisor",
            "System Administrator",
        ]
    ).exists()


def user_can_create_quality_inspections(user):
    if user.is_superuser:
        return True

    return user.groups.filter(
        name__in=[
            "Quality Specialist",
            "System Administrator",
        ]
    ).exists()


def user_can_complete_quality_inspections(user):
    if user.is_superuser:
        return True

    return user.groups.filter(
        name__in=[
            "Quality Specialist",
            "System Administrator",
        ]
    ).exists()


@login_required
def dashboard_router(request):
    if request.user.is_superuser:
        return redirect("system-administrator-dashboard")

    user_groups = set(
        request.user.groups.values_list(
            "name",
            flat=True,
        )
    )

    for group_name, route_name in ROLE_ROUTES:
        if group_name in user_groups:
            return redirect(route_name)

    raise PermissionDenied(
        "Your account does not have a ForgeOps role assigned."
    )


@login_required
def role_dashboard(request, role_name):
    has_role = request.user.groups.filter(
        name=role_name
    ).exists()

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
            "can_create_work_orders": (
                user_can_create_work_orders(
                    request.user
                )
            ),
        },
    )


@login_required
def work_order_detail(request, pk):
    work_order = get_object_or_404(
        WorkOrder.objects.select_related("product"),
        pk=pk,
    )

    production_runs = (
        work_order.production_runs.select_related(
            "production_line__production_area__site",
            "shift",
        ).all()
    )

    return render(
        request,
        "core/work_order_detail.html",
        {
            "work_order": work_order,
            "production_runs": production_runs,
            "can_create_work_orders": (
                user_can_create_work_orders(
                    request.user
                )
            ),
            "can_create_production_runs": (
                user_can_create_production_runs(
                    request.user
                )
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
    selected_work_order = request.GET.get(
        "work_order",
        "",
    )
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

    work_orders = (
        WorkOrder.objects.filter(
            is_active=True
        )
        .select_related("product")
        .order_by("order_number")
    )

    production_lines = (
        ProductionLine.objects.filter(
            is_active=True
        )
        .select_related(
            "production_area__site"
        )
        .order_by(
            "production_area__site__code",
            "production_area__code",
            "code",
        )
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
            "selected_production_line": (
                selected_production_line
            ),
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

    production_entries = (
        production_run.production_entries.select_related(
            "recorded_by"
        ).all()
    )

    downtime_events = (
        production_run.downtime_events.select_related(
            "downtime_reason",
            "opened_by",
            "closed_by",
        ).all()
    )

    open_downtime_exists = downtime_events.filter(
        ended_at__isnull=True
    ).exists()

    quality_inspections = (
        production_run.quality_inspections.select_related(
            "completed_by"
        ).all()
    )

    return render(
        request,
        "core/production_run_detail.html",
        {
            "production_run": production_run,
            "production_entries": production_entries,
            "downtime_events": downtime_events,
            "open_downtime_exists": open_downtime_exists,
            "quality_inspections": quality_inspections,
            "can_start_production_runs": (
                user_can_start_production_runs(
                    request.user
                )
            ),
            "can_pause_production_runs": (
                user_can_pause_production_runs(
                    request.user
                )
            ),
            "can_resume_production_runs": (
                user_can_resume_production_runs(
                    request.user
                )
            ),
            "can_complete_production_runs": (
                user_can_complete_production_runs(
                    request.user
                )
            ),
            "can_cancel_production_runs": (
                user_can_cancel_production_runs(
                    request.user
                )
            ),
            "can_create_production_entries": (
                user_can_create_production_entries(
                    request.user
                )
            ),
            "can_manage_downtime_events": (
                user_can_manage_downtime_events(
                    request.user
                )
            ),
            "can_create_quality_inspections": (
                user_can_create_quality_inspections(
                    request.user
                )
            ),
            "can_complete_quality_inspections": (
                user_can_complete_quality_inspections(
                    request.user
                )
            ),
        },
    )


@login_required
def production_run_create(
    request,
    work_order_pk,
):
    if not user_can_create_production_runs(
        request.user
    ):
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
def production_entry_create(
    request,
    production_run_pk,
):
    if not user_can_create_production_entries(
        request.user
    ):
        raise PermissionDenied(
            "You do not have permission to record "
            "Production Entries."
        )

    production_run = get_object_or_404(
        ProductionRun.objects.select_related(
            "work_order__product",
            "production_line__production_area__site",
            "shift",
        ),
        pk=production_run_pk,
    )

    if (
        production_run.status
        != ProductionRun.Status.ACTIVE
    ):
        raise PermissionDenied(
            "Production Entries may only be recorded "
            "against ACTIVE Production Runs."
        )

    if request.method == "POST":
        form = ProductionEntryForm(request.POST)

        if form.is_valid():
            production_entry = form.save(
                commit=False
            )
            production_entry.production_run = (
                production_run
            )
            production_entry.recorded_by = (
                request.user
            )

            production_entry.full_clean()
            production_entry.save()

            return redirect(
                "production-run-detail",
                pk=production_run.pk,
            )
    else:
        form = ProductionEntryForm()

    return render(
        request,
        "core/production_entry_form.html",
        {
            "form": form,
            "production_run": production_run,
        },
    )


@login_required
def downtime_event_create(
    request,
    production_run_pk,
):
    if not user_can_manage_downtime_events(
        request.user
    ):
        raise PermissionDenied(
            "You do not have permission to open "
            "Downtime Events."
        )

    production_run = get_object_or_404(
        ProductionRun.objects.select_related(
            "work_order__product",
            "production_line__production_area__site",
            "shift",
        ),
        pk=production_run_pk,
    )

    if (
        production_run.status
        != ProductionRun.Status.ACTIVE
    ):
        raise PermissionDenied(
            "Downtime Events may only be opened against "
            "ACTIVE Production Runs."
        )

    open_downtime_exists = (
        production_run.downtime_events.filter(
            ended_at__isnull=True
        ).exists()
    )

    if open_downtime_exists:
        raise PermissionDenied(
            "This Production Run already has an open "
            "Downtime Event."
        )

    if request.method == "POST":
        form = DowntimeEventForm(request.POST)

        if form.is_valid():
            downtime_event = form.save(
                commit=False
            )
            downtime_event.production_run = (
                production_run
            )
            downtime_event.opened_by = (
                request.user
            )
            downtime_event.ended_at = None
            downtime_event.closed_by = None

            downtime_event.full_clean()
            downtime_event.save()

            return redirect(
                "production-run-detail",
                pk=production_run.pk,
            )
    else:
        form = DowntimeEventForm()

    return render(
        request,
        "core/downtime_event_form.html",
        {
            "form": form,
            "production_run": production_run,
        },
    )


@login_required
def downtime_event_close(request, pk):
    if not user_can_manage_downtime_events(
        request.user
    ):
        raise PermissionDenied(
            "You do not have permission to close "
            "Downtime Events."
        )

    downtime_event = get_object_or_404(
        DowntimeEvent.objects.select_related(
            "production_run",
            "downtime_reason",
            "opened_by",
            "closed_by",
        ),
        pk=pk,
    )

    if request.method != "POST":
        raise PermissionDenied(
            "Downtime Events may only be closed using POST."
        )

    if downtime_event.ended_at is not None:
        raise PermissionDenied(
            "Only open Downtime Events may be closed."
        )

    downtime_event.ended_at = timezone.now()
    downtime_event.closed_by = request.user

    downtime_event.full_clean()
    downtime_event.save(
        update_fields=[
            "ended_at",
            "closed_by",
            "updated_at",
        ]
    )

    return redirect(
        "production-run-detail",
        pk=downtime_event.production_run.pk,
    )


@login_required
def quality_inspection_create(
    request,
    production_run_pk,
):
    if not user_can_create_quality_inspections(
        request.user
    ):
        raise PermissionDenied(
            "You do not have permission to create "
            "Quality Inspections."
        )

    production_run = get_object_or_404(
        ProductionRun.objects.select_related(
            "work_order__product",
            "production_line__production_area__site",
            "shift",
        ),
        pk=production_run_pk,
    )

    if request.method == "POST":
        form = QualityInspectionCreateForm(
            request.POST
        )

        if form.is_valid():
            quality_inspection = form.save(
                commit=False
            )
            quality_inspection.production_run = (
                production_run
            )
            quality_inspection.result = (
                QualityInspection.Result.PENDING
            )
            quality_inspection.completed_by = None
            quality_inspection.completed_at = None

            quality_inspection.full_clean()
            quality_inspection.save()

            return redirect(
                "production-run-detail",
                pk=production_run.pk,
            )
    else:
        form = QualityInspectionCreateForm()

    return render(
        request,
        "core/quality_inspection_form.html",
        {
            "form": form,
            "production_run": production_run,
        },
    )


@login_required
def quality_inspection_complete(request, pk):
    if not user_can_complete_quality_inspections(
        request.user
    ):
        raise PermissionDenied(
            "You do not have permission to complete "
            "Quality Inspections."
        )

    quality_inspection = get_object_or_404(
        QualityInspection.objects.select_related(
            "production_run__work_order__product",
            "production_run__production_line"
            "__production_area__site",
            "production_run__shift",
            "completed_by",
        ),
        pk=pk,
    )

    if request.method != "POST":
        raise PermissionDenied(
            "Quality Inspections may only be completed "
            "using POST."
        )

    if (
        quality_inspection.result
        != QualityInspection.Result.PENDING
    ):
        raise PermissionDenied(
            "Only PENDING Quality Inspections "
            "may be completed."
        )

    if "result" not in request.POST:
        form = QualityInspectionCompleteForm(
            instance=quality_inspection
        )

        return render(
            request,
            "core/quality_inspection_complete_form.html",
            {
                "form": form,
                "quality_inspection": quality_inspection,
                "production_run": (
                    quality_inspection.production_run
                ),
            },
        )

    quality_inspection.completed_by = request.user
    quality_inspection.completed_at = timezone.now()

    form = QualityInspectionCompleteForm(
        request.POST,
        instance=quality_inspection,
    )

    if form.is_valid():
        completed_inspection = form.save(
            commit=False
        )

        completed_inspection.full_clean()
        completed_inspection.save()

        return redirect(
            "production-run-detail",
            pk=completed_inspection.production_run.pk,
        )

    return render(
        request,
        "core/quality_inspection_complete_form.html",
        {
            "form": form,
            "quality_inspection": quality_inspection,
            "production_run": (
                quality_inspection.production_run
            ),
        },
    )


@login_required
def production_run_start(request, pk):
    if not user_can_start_production_runs(
        request.user
    ):
        raise PermissionDenied(
            "You do not have permission to start "
            "Production Runs."
        )

    production_run = get_object_or_404(
        ProductionRun,
        pk=pk,
    )

    if request.method != "POST":
        raise PermissionDenied(
            "Production Runs may only be started using POST."
        )

    if (
        production_run.status
        != ProductionRun.Status.PLANNED
    ):
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
            "This Work Order already has an ACTIVE "
            "Production Run."
        )

    production_run.status = (
        ProductionRun.Status.ACTIVE
    )
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
    if not user_can_pause_production_runs(
        request.user
    ):
        raise PermissionDenied(
            "You do not have permission to pause "
            "Production Runs."
        )

    production_run = get_object_or_404(
        ProductionRun,
        pk=pk,
    )

    if request.method != "POST":
        raise PermissionDenied(
            "Production Runs may only be paused using POST."
        )

    if (
        production_run.status
        != ProductionRun.Status.ACTIVE
    ):
        raise PermissionDenied(
            "Only ACTIVE Production Runs may be paused."
        )

    production_run.status = (
        ProductionRun.Status.PAUSED
    )

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
    if not user_can_resume_production_runs(
        request.user
    ):
        raise PermissionDenied(
            "You do not have permission to resume "
            "Production Runs."
        )

    production_run = get_object_or_404(
        ProductionRun,
        pk=pk,
    )

    if request.method != "POST":
        raise PermissionDenied(
            "Production Runs may only be resumed using POST."
        )

    if (
        production_run.status
        != ProductionRun.Status.PAUSED
    ):
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
            "This Work Order already has an ACTIVE "
            "Production Run."
        )

    production_run.status = (
        ProductionRun.Status.ACTIVE
    )

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
    if not user_can_complete_production_runs(
        request.user
    ):
        raise PermissionDenied(
            "You do not have permission to complete "
            "Production Runs."
        )

    production_run = get_object_or_404(
        ProductionRun,
        pk=pk,
    )

    if request.method != "POST":
        raise PermissionDenied(
            "Production Runs may only be completed using POST."
        )

    if (
        production_run.status
        != ProductionRun.Status.ACTIVE
    ):
        raise PermissionDenied(
            "Only ACTIVE Production Runs may be completed."
        )

    production_run.status = (
        ProductionRun.Status.COMPLETED
    )
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


@login_required
def production_run_cancel(request, pk):
    if not user_can_cancel_production_runs(
        request.user
    ):
        raise PermissionDenied(
            "You do not have permission to cancel "
            "Production Runs."
        )

    production_run = get_object_or_404(
        ProductionRun,
        pk=pk,
    )

    if request.method != "POST":
        raise PermissionDenied(
            "Production Runs may only be cancelled using POST."
        )

    if production_run.status not in [
        ProductionRun.Status.PLANNED,
        ProductionRun.Status.ACTIVE,
        ProductionRun.Status.PAUSED,
    ]:
        raise PermissionDenied(
            "Only PLANNED, ACTIVE or PAUSED Production Runs "
            "may be cancelled."
        )

    previous_status = production_run.status

    production_run.status = (
        ProductionRun.Status.CANCELLED
    )

    if previous_status in [
        ProductionRun.Status.ACTIVE,
        ProductionRun.Status.PAUSED,
    ]:
        production_run.ended_at = timezone.now()

    production_run.full_clean()

    if (
        previous_status
        == ProductionRun.Status.PLANNED
    ):
        production_run.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )
    else:
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