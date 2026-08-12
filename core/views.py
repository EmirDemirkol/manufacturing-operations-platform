from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from .forms import WorkOrderForm
from .models import Product, WorkOrder


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
        "production_line",
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