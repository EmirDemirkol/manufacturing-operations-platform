from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render


ROLE_ROUTES = [
    ("Operator", "operator-dashboard"),
    ("Production Supervisor", "supervisor-dashboard"),
    ("Quality Specialist", "quality-dashboard"),
    ("Manufacturing Engineer", "engineer-dashboard"),
    ("Operations Manager", "manager-dashboard"),
    ("System Administrator", "system-administrator-dashboard"),
]


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