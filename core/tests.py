from datetime import date, time
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import (
    Product,
    ProductionArea,
    ProductionEntry,
    ProductionLine,
    ProductionRun,
    Shift,
    Site,
    WorkOrder,
)

ROLE_NAMES = {
    "Operator",
    "Production Supervisor",
    "Quality Specialist",
    "Manufacturing Engineer",
    "Operations Manager",
    "System Administrator",
}

DEMO_USERS = {
    "operator_demo": "Operator",
    "supervisor_demo": "Production Supervisor",
    "quality_demo": "Quality Specialist",
    "engineer_demo": "Manufacturing Engineer",
    "manager_demo": "Operations Manager",
    "sysadmin_demo": "System Administrator",
}


class AuthenticationAndRoleTests(TestCase):
    password = "ForgeOps-Test-Password-2026!"

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()

        cls.operator_group = Group.objects.get(name="Operator")

        cls.operator = User.objects.create_user(
            username="operator_demo",
            password=cls.password,
        )
        cls.operator.groups.add(cls.operator_group)

        cls.unassigned_user = User.objects.create_user(
            username="unassigned_demo",
            password=cls.password,
        )

    def test_all_required_groups_exist(self):
        group_names = set(
            Group.objects.values_list("name", flat=True)
        )

        self.assertSetEqual(group_names, ROLE_NAMES)

    def test_home_page_requires_login(self):
        response = self.client.get(
            reverse("dashboard-router")
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            "/accounts/login/?next=/",
        )

    def test_invalid_credentials_are_rejected(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "operator_demo",
                "password": "incorrect-password",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "The username or password is incorrect.",
        )

    def test_valid_credentials_are_accepted(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "operator_demo",
                "password": self.password,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("dashboard-router"),
        )

    def test_operator_is_routed_to_operator_dashboard(self):
        self.client.force_login(self.operator)

        response = self.client.get(
            reverse("dashboard-router")
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("operator-dashboard"),
        )

    def test_operator_can_access_operator_dashboard(self):
        self.client.force_login(self.operator)

        response = self.client.get(
            reverse("operator-dashboard")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Operator Dashboard",
        )
        self.assertContains(
            response,
            "Signed in with the Operator role.",
        )

    def test_operator_cannot_access_quality_dashboard(self):
        self.client.force_login(self.operator)

        response = self.client.get(
            reverse("quality-dashboard")
        )

        self.assertEqual(response.status_code, 403)

    def test_user_without_role_is_denied(self):
        self.client.force_login(self.unassigned_user)

        response = self.client.get(
            reverse("dashboard-router")
        )

        self.assertEqual(response.status_code, 403)

    def test_logout_redirects_to_login_page(self):
        self.client.force_login(self.operator)

        response = self.client.post(
            reverse("logout")
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse("login"),
        )


class SeedDemoUsersCommandTests(TestCase):
    def test_command_creates_users_with_correct_groups(self):
        password = "ForgeOps-Demo-Command-Test-2026!"
        output = StringIO()

        with patch(
            "core.management.commands.seed_demo_users.getpass",
            side_effect=[password, password],
        ):
            call_command(
                "seed_demo_users",
                stdout=output,
            )

        User = get_user_model()

        for username, group_name in DEMO_USERS.items():
            user = User.objects.get(username=username)

            self.assertTrue(
                user.check_password(password)
            )
            self.assertTrue(
                user.groups.filter(name=group_name).exists()
            )
            self.assertTrue(user.is_active)

        system_admin = User.objects.get(
            username="sysadmin_demo"
        )
        self.assertTrue(system_admin.is_staff)
        self.assertFalse(system_admin.is_superuser)


class WorkOrderInterfaceTests(TestCase):
    password = "ForgeOps-Test-Password-2026!"

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()

        cls.operator_group = Group.objects.get(
            name="Operator"
        )
        cls.supervisor_group = Group.objects.get(
            name="Production Supervisor"
        )

        cls.operator = User.objects.create_user(
            username="fo011_operator",
            password=cls.password,
        )
        cls.operator.groups.add(cls.operator_group)

        cls.supervisor = User.objects.create_user(
            username="fo011_supervisor",
            password=cls.password,
        )
        cls.supervisor.groups.add(cls.supervisor_group)

        cls.product = Product.objects.create(
            code="PRD-FO011-A",
            name="Synthetic FO-011 Product A",
            description="Synthetic product for FO-011 interface tests.",
        )

        cls.second_product = Product.objects.create(
            code="PRD-FO011-B",
            name="Synthetic FO-011 Product B",
            description="Second synthetic product for filtering tests.",
        )

        cls.inactive_product = Product.objects.create(
            code="PRD-FO011-INACTIVE",
            name="Inactive Synthetic Product",
            description="Inactive product for FO-011 form testing.",
            is_active=False,
        )

        cls.draft_work_order = WorkOrder.objects.create(
            order_number="WO-FO011-0001",
            product=cls.product,
            planned_quantity=500,
            status=WorkOrder.Status.DRAFT,
            due_date=date(2026, 8, 20),
            notes="Synthetic draft Work Order.",
        )

        cls.released_work_order = WorkOrder.objects.create(
            order_number="WO-FO011-0002",
            product=cls.second_product,
            planned_quantity=1000,
            status=WorkOrder.Status.RELEASED,
            due_date=date(2026, 8, 25),
            notes="Synthetic released Work Order.",
        )

    def test_work_order_list_requires_login(self):
        response = self.client.get(
            reverse("work-order-list")
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            "/accounts/login/",
            response.url,
        )

    def test_authenticated_operator_can_view_work_order_list(self):
        self.client.force_login(self.operator)

        response = self.client.get(
            reverse("work-order-list")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            self.draft_work_order.order_number,
        )
        self.assertContains(
            response,
            self.released_work_order.order_number,
        )

    def test_work_order_detail_page_displays_work_order(self):
        self.client.force_login(self.supervisor)

        response = self.client.get(
            reverse(
                "work-order-detail",
                kwargs={"pk": self.draft_work_order.pk},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            self.draft_work_order.order_number,
        )
        self.assertContains(
            response,
            self.product.code,
        )
        self.assertContains(
            response,
            "500",
        )
        self.assertContains(
            response,
            "Draft",
        )

    def test_supervisor_can_access_work_order_create_page(self):
        self.client.force_login(self.supervisor)

        response = self.client.get(
            reverse("work-order-create")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Create Work Order",
        )

    def test_operator_cannot_access_work_order_create_page(self):
        self.client.force_login(self.operator)

        response = self.client.get(
            reverse("work-order-create")
        )

        self.assertEqual(response.status_code, 403)

    def test_operator_does_not_see_create_work_order_button(self):
        self.client.force_login(self.operator)

        response = self.client.get(
            reverse("work-order-list")
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            'href="/work-orders/new/"',
        )

    def test_supervisor_can_create_valid_work_order(self):
        self.client.force_login(self.supervisor)

        response = self.client.post(
            reverse("work-order-create"),
            {
                "order_number": "WO-FO011-0003",
                "product": self.product.pk,
                "planned_quantity": 750,
                "status": WorkOrder.Status.DRAFT,
                "due_date": "2026-08-30",
                "notes": "Synthetic FO-011 creation test.",
            },
        )

        created_work_order = WorkOrder.objects.get(
            order_number="WO-FO011-0003"
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse(
                "work-order-detail",
                kwargs={"pk": created_work_order.pk},
            ),
        )
        self.assertEqual(
            created_work_order.product,
            self.product,
        )
        self.assertEqual(
            created_work_order.planned_quantity,
            750,
        )
        self.assertEqual(
            created_work_order.status,
            WorkOrder.Status.DRAFT,
        )

    def test_duplicate_work_order_number_is_rejected(self):
        self.client.force_login(self.supervisor)

        initial_count = WorkOrder.objects.count()

        response = self.client.post(
            reverse("work-order-create"),
            {
                "order_number": self.draft_work_order.order_number,
                "product": self.product.pk,
                "planned_quantity": 250,
                "status": WorkOrder.Status.DRAFT,
                "due_date": "",
                "notes": "Synthetic duplicate test.",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            WorkOrder.objects.count(),
            initial_count,
        )
        self.assertIn(
            "order_number",
            response.context["form"].errors,
        )

    def test_zero_planned_quantity_is_rejected(self):
        self.client.force_login(self.supervisor)

        response = self.client.post(
            reverse("work-order-create"),
            {
                "order_number": "WO-FO011-0004",
                "product": self.product.pk,
                "planned_quantity": 0,
                "status": WorkOrder.Status.DRAFT,
                "due_date": "",
                "notes": "Synthetic invalid quantity test.",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            WorkOrder.objects.filter(
                order_number="WO-FO011-0004"
            ).exists()
        )
        self.assertIn(
            "planned_quantity",
            response.context["form"].errors,
        )

    def test_product_is_required_when_creating_work_order(self):
        self.client.force_login(self.supervisor)

        response = self.client.post(
            reverse("work-order-create"),
            {
                "order_number": "WO-FO011-0005",
                "product": "",
                "planned_quantity": 400,
                "status": WorkOrder.Status.DRAFT,
                "due_date": "",
                "notes": "Synthetic missing product test.",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            WorkOrder.objects.filter(
                order_number="WO-FO011-0005"
            ).exists()
        )
        self.assertIn(
            "product",
            response.context["form"].errors,
        )

    def test_invalid_status_is_rejected(self):
        self.client.force_login(self.supervisor)

        response = self.client.post(
            reverse("work-order-create"),
            {
                "order_number": "WO-FO011-0006",
                "product": self.product.pk,
                "planned_quantity": 400,
                "status": "INVALID",
                "due_date": "",
                "notes": "Synthetic invalid status test.",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            WorkOrder.objects.filter(
                order_number="WO-FO011-0006"
            ).exists()
        )
        self.assertIn(
            "status",
            response.context["form"].errors,
        )

    def test_work_order_list_can_filter_by_status(self):
        self.client.force_login(self.supervisor)

        response = self.client.get(
            reverse("work-order-list"),
            {
                "status": WorkOrder.Status.DRAFT,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            self.draft_work_order.order_number,
        )
        self.assertNotContains(
            response,
            self.released_work_order.order_number,
        )

    def test_work_order_list_can_filter_by_product(self):
        self.client.force_login(self.supervisor)

        response = self.client.get(
            reverse("work-order-list"),
            {
                "product": self.product.pk,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            self.draft_work_order.order_number,
        )
        self.assertNotContains(
            response,
            self.released_work_order.order_number,
        )

    def test_inactive_products_are_not_available_in_creation_form(self):
        self.client.force_login(self.supervisor)

        response = self.client.get(
            reverse("work-order-create")
        )

        product_queryset = (
            response.context["form"]
            .fields["product"]
            .queryset
        )

        self.assertIn(
            self.product,
            product_queryset,
        )
        self.assertIn(
            self.second_product,
            product_queryset,
        )
        self.assertNotIn(
            self.inactive_product,
            product_queryset,
        )


class ProductionRunInterfaceTests(TestCase):
    password = "ForgeOps-Test-Password-2026!"

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()

        cls.operator_group = Group.objects.get(
            name="Operator"
        )
        cls.supervisor_group = Group.objects.get(
            name="Production Supervisor"
        )

        cls.operator = User.objects.create_user(
            username="fo012_operator",
            password=cls.password,
        )
        cls.operator.groups.add(cls.operator_group)

        cls.supervisor = User.objects.create_user(
            username="fo012_supervisor",
            password=cls.password,
        )
        cls.supervisor.groups.add(cls.supervisor_group)

        cls.site = Site.objects.create(
            code="FO012-SITE",
            name="Synthetic FO-012 Site",
            description="Synthetic site for FO-012 interface tests.",
        )

        cls.production_area = ProductionArea.objects.create(
            site=cls.site,
            code="FO012-AREA",
            name="Synthetic FO-012 Area",
            description="Synthetic area for FO-012 interface tests.",
        )

        cls.production_line = ProductionLine.objects.create(
            production_area=cls.production_area,
            code="FO012-LINE-A",
            name="Synthetic FO-012 Line A",
            description="Primary synthetic Production Line.",
        )

        cls.second_production_line = ProductionLine.objects.create(
            production_area=cls.production_area,
            code="FO012-LINE-B",
            name="Synthetic FO-012 Line B",
            description="Second synthetic Production Line.",
        )

        cls.inactive_production_line = ProductionLine.objects.create(
            production_area=cls.production_area,
            code="FO012-LINE-INACTIVE",
            name="Inactive Synthetic FO-012 Line",
            description="Inactive line for FO-012 form testing.",
            is_active=False,
        )

        cls.shift = Shift.objects.create(
            name="FO-012 Day Shift",
            start_time=time(7, 0),
            end_time=time(15, 0),
        )

        cls.second_shift = Shift.objects.create(
            name="FO-012 Night Shift",
            start_time=time(23, 0),
            end_time=time(7, 0),
        )

        cls.inactive_shift = Shift.objects.create(
            name="FO-012 Inactive Shift",
            start_time=time(15, 0),
            end_time=time(23, 0),
            is_active=False,
        )

        cls.product = Product.objects.create(
            code="PRD-FO012-A",
            name="Synthetic FO-012 Product",
            description="Synthetic product for FO-012 interface tests.",
        )

        cls.work_order = WorkOrder.objects.create(
            order_number="WO-FO012-0001",
            product=cls.product,
            planned_quantity=1000,
            status=WorkOrder.Status.RELEASED,
            due_date=date(2026, 8, 25),
            notes="Synthetic Work Order for FO-012.",
        )

        cls.second_work_order = WorkOrder.objects.create(
            order_number="WO-FO012-0002",
            product=cls.product,
            planned_quantity=500,
            status=WorkOrder.Status.RELEASED,
            due_date=date(2026, 8, 30),
            notes="Second synthetic Work Order for FO-012.",
        )

        cls.active_production_run = ProductionRun.objects.create(
            work_order=cls.work_order,
            production_line=cls.production_line,
            shift=cls.shift,
            status=ProductionRun.Status.ACTIVE,
            notes="Synthetic active Production Run.",
        )

        cls.planned_production_run = ProductionRun.objects.create(
            work_order=cls.second_work_order,
            production_line=cls.second_production_line,
            shift=cls.second_shift,
            status=ProductionRun.Status.PLANNED,
            notes="Synthetic planned Production Run.",
        )

    def test_production_run_list_requires_login(self):
        response = self.client.get(
            reverse("production-run-list")
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            "/accounts/login/",
            response.url,
        )

    def test_authenticated_operator_can_view_production_run_list(self):
        self.client.force_login(self.operator)

        response = self.client.get(
            reverse("production-run-list")
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f"Run #{self.active_production_run.pk}",
        )
        self.assertContains(
            response,
            f"Run #{self.planned_production_run.pk}",
        )

    def test_production_run_detail_page_displays_production_run(self):
        self.client.force_login(self.supervisor)

        response = self.client.get(
            reverse(
                "production-run-detail",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f"Production Run #{self.active_production_run.pk}",
        )
        self.assertContains(
            response,
            self.work_order.order_number,
        )
        self.assertContains(
            response,
            self.production_line.code,
        )
        self.assertContains(
            response,
            self.shift.name,
        )
        self.assertContains(
            response,
            "Active",
        )

    def test_supervisor_can_access_production_run_create_page(self):
        self.client.force_login(self.supervisor)

        response = self.client.get(
            reverse(
                "production-run-create",
                kwargs={
                    "work_order_pk": self.work_order.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Create Production Run",
        )
        self.assertContains(
            response,
            self.work_order.order_number,
        )

    def test_operator_cannot_access_production_run_create_page(self):
        self.client.force_login(self.operator)

        response = self.client.get(
            reverse(
                "production-run-create",
                kwargs={
                    "work_order_pk": self.work_order.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_supervisor_can_create_valid_production_run(self):
        self.client.force_login(self.supervisor)

        response = self.client.post(
            reverse(
                "production-run-create",
                kwargs={
                    "work_order_pk": self.second_work_order.pk,
                },
            ),
            {
                "production_line": self.production_line.pk,
                "shift": self.shift.pk,
                "notes": "Synthetic FO-012 creation test.",
            },
        )

        created_run = ProductionRun.objects.get(
            work_order=self.second_work_order,
            production_line=self.production_line,
            shift=self.shift,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse(
                "production-run-detail",
                kwargs={"pk": created_run.pk},
            ),
        )
        self.assertEqual(
            created_run.status,
            ProductionRun.Status.PLANNED,
        )
        self.assertIsNone(created_run.started_at)
        self.assertIsNone(created_run.ended_at)

    def test_created_production_run_belongs_to_requested_work_order(self):
        self.client.force_login(self.supervisor)

        self.client.post(
            reverse(
                "production-run-create",
                kwargs={
                    "work_order_pk": self.second_work_order.pk,
                },
            ),
            {
                "production_line": self.production_line.pk,
                "shift": self.shift.pk,
                "notes": "Synthetic Work Order relationship test.",
            },
        )

        created_run = ProductionRun.objects.get(
            work_order=self.second_work_order,
            production_line=self.production_line,
            shift=self.shift,
        )

        self.assertEqual(
            created_run.work_order,
            self.second_work_order,
        )

    def test_production_line_is_required_when_creating_run(self):
        self.client.force_login(self.supervisor)

        initial_count = ProductionRun.objects.count()

        response = self.client.post(
            reverse(
                "production-run-create",
                kwargs={
                    "work_order_pk": self.second_work_order.pk,
                },
            ),
            {
                "production_line": "",
                "shift": self.shift.pk,
                "notes": "Synthetic missing Production Line test.",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            ProductionRun.objects.count(),
            initial_count,
        )
        self.assertIn(
            "production_line",
            response.context["form"].errors,
        )

    def test_shift_is_required_when_creating_run(self):
        self.client.force_login(self.supervisor)

        initial_count = ProductionRun.objects.count()

        response = self.client.post(
            reverse(
                "production-run-create",
                kwargs={
                    "work_order_pk": self.second_work_order.pk,
                },
            ),
            {
                "production_line": self.production_line.pk,
                "shift": "",
                "notes": "Synthetic missing Shift test.",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            ProductionRun.objects.count(),
            initial_count,
        )
        self.assertIn(
            "shift",
            response.context["form"].errors,
        )

    def test_inactive_production_lines_are_not_available_in_creation_form(
        self
    ):
        self.client.force_login(self.supervisor)

        response = self.client.get(
            reverse(
                "production-run-create",
                kwargs={
                    "work_order_pk": self.second_work_order.pk,
                },
            )
        )

        production_line_queryset = (
            response.context["form"]
            .fields["production_line"]
            .queryset
        )

        self.assertIn(
            self.production_line,
            production_line_queryset,
        )
        self.assertIn(
            self.second_production_line,
            production_line_queryset,
        )
        self.assertNotIn(
            self.inactive_production_line,
            production_line_queryset,
        )

    def test_inactive_shifts_are_not_available_in_creation_form(self):
        self.client.force_login(self.supervisor)

        response = self.client.get(
            reverse(
                "production-run-create",
                kwargs={
                    "work_order_pk": self.second_work_order.pk,
                },
            )
        )

        shift_queryset = (
            response.context["form"]
            .fields["shift"]
            .queryset
        )

        self.assertIn(
            self.shift,
            shift_queryset,
        )
        self.assertIn(
            self.second_shift,
            shift_queryset,
        )
        self.assertNotIn(
            self.inactive_shift,
            shift_queryset,
        )

    def test_production_run_list_can_filter_by_status(self):
        self.client.force_login(self.supervisor)

        response = self.client.get(
            reverse("production-run-list"),
            {
                "status": ProductionRun.Status.PLANNED,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f"Run #{self.planned_production_run.pk}",
        )
        self.assertNotContains(
            response,
            f"Run #{self.active_production_run.pk}",
        )

    def test_production_run_list_can_filter_by_work_order(self):
        self.client.force_login(self.supervisor)

        response = self.client.get(
            reverse("production-run-list"),
            {
                "work_order": self.work_order.pk,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f"Run #{self.active_production_run.pk}",
        )
        self.assertNotContains(
            response,
            f"Run #{self.planned_production_run.pk}",
        )

    def test_production_run_list_can_filter_by_production_line(self):
        self.client.force_login(self.supervisor)

        response = self.client.get(
            reverse("production-run-list"),
            {
                "production_line": self.production_line.pk,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f"Run #{self.active_production_run.pk}",
        )
        self.assertNotContains(
            response,
            f"Run #{self.planned_production_run.pk}",
        )

    def test_production_run_list_can_filter_by_shift(self):
        self.client.force_login(self.supervisor)

        response = self.client.get(
            reverse("production-run-list"),
            {
                "shift": self.second_shift.pk,
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f"Run #{self.planned_production_run.pk}",
        )
        self.assertNotContains(
            response,
            f"Run #{self.active_production_run.pk}",
        )

    def test_supervisor_sees_start_button_for_planned_production_run(self):
        self.client.force_login(self.supervisor)

        response = self.client.get(
            reverse(
                "production-run-detail",
                kwargs={
                    "pk": self.planned_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Start Production Run",
        )

    def test_start_button_is_not_shown_for_active_production_run(self):
        self.client.force_login(self.supervisor)

        response = self.client.get(
            reverse(
                "production-run-detail",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            "Start Production Run",
        )

    def test_operator_cannot_start_production_run(self):
        self.client.force_login(self.operator)

        response = self.client.post(
            reverse(
                "production-run-start",
                kwargs={
                    "pk": self.planned_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 403)

        self.planned_production_run.refresh_from_db()

        self.assertEqual(
            self.planned_production_run.status,
            ProductionRun.Status.PLANNED,
        )
        self.assertIsNone(
            self.planned_production_run.started_at
        )

    def test_production_run_start_requires_post(self):
        self.client.force_login(self.supervisor)

        response = self.client.get(
            reverse(
                "production-run-start",
                kwargs={
                    "pk": self.planned_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 403)

        self.planned_production_run.refresh_from_db()

        self.assertEqual(
            self.planned_production_run.status,
            ProductionRun.Status.PLANNED,
        )

    def test_supervisor_can_start_planned_production_run(self):
        self.client.force_login(self.supervisor)

        response = self.client.post(
            reverse(
                "production-run-start",
                kwargs={
                    "pk": self.planned_production_run.pk,
                },
            )
        )

        self.planned_production_run.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse(
                "production-run-detail",
                kwargs={
                    "pk": self.planned_production_run.pk,
                },
            ),
        )
        self.assertEqual(
            self.planned_production_run.status,
            ProductionRun.Status.ACTIVE,
        )
        self.assertIsNotNone(
            self.planned_production_run.started_at
        )
        self.assertIsNone(
            self.planned_production_run.ended_at
        )

    def test_active_production_run_cannot_be_started_again(self):
        self.client.force_login(self.supervisor)

        response = self.client.post(
            reverse(
                "production-run-start",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 403)

        self.active_production_run.refresh_from_db()

        self.assertEqual(
            self.active_production_run.status,
            ProductionRun.Status.ACTIVE,
        )

    def test_second_active_run_for_same_work_order_is_blocked(self):
        conflicting_planned_run = ProductionRun.objects.create(
            work_order=self.work_order,
            production_line=self.second_production_line,
            shift=self.second_shift,
            status=ProductionRun.Status.PLANNED,
            notes="Synthetic FO-013 active-run conflict test.",
        )

        self.client.force_login(self.supervisor)

        response = self.client.post(
            reverse(
                "production-run-start",
                kwargs={
                    "pk": conflicting_planned_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 403)

        conflicting_planned_run.refresh_from_db()

        self.assertEqual(
            conflicting_planned_run.status,
            ProductionRun.Status.PLANNED,
        )
        self.assertIsNone(
            conflicting_planned_run.started_at
        )

        self.active_production_run.refresh_from_db()

        self.assertEqual(
            self.active_production_run.status,
            ProductionRun.Status.ACTIVE,
        )
    def test_supervisor_sees_pause_button_for_active_production_run(self):
        self.client.force_login(self.supervisor)

        response = self.client.get(
            reverse(
                "production-run-detail",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Pause Production Run",
        )

    def test_pause_button_is_not_shown_for_planned_production_run(self):
        self.client.force_login(self.supervisor)

        response = self.client.get(
            reverse(
                "production-run-detail",
                kwargs={
                    "pk": self.planned_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            "Pause Production Run",
        )

    def test_operator_cannot_pause_production_run(self):
        self.client.force_login(self.operator)

        response = self.client.post(
            reverse(
                "production-run-pause",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 403)

        self.active_production_run.refresh_from_db()

        self.assertEqual(
            self.active_production_run.status,
            ProductionRun.Status.ACTIVE,
        )

    def test_production_run_pause_requires_post(self):
        self.client.force_login(self.supervisor)

        response = self.client.get(
            reverse(
                "production-run-pause",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 403)

        self.active_production_run.refresh_from_db()

        self.assertEqual(
            self.active_production_run.status,
            ProductionRun.Status.ACTIVE,
        )

    def test_supervisor_can_pause_active_production_run(self):
        started_at = timezone.now()

        self.active_production_run.started_at = started_at
        self.active_production_run.ended_at = None
        self.active_production_run.save(
            update_fields=[
                "started_at",
                "ended_at",
                "updated_at",
            ]
        )

        self.client.force_login(self.supervisor)

        response = self.client.post(
            reverse(
                "production-run-pause",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.active_production_run.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse(
                "production-run-detail",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            ),
        )
        self.assertEqual(
            self.active_production_run.status,
            ProductionRun.Status.PAUSED,
        )
        self.assertEqual(
            self.active_production_run.started_at,
            started_at,
        )
        self.assertIsNone(
            self.active_production_run.ended_at
        )

    def test_paused_production_run_cannot_be_paused_again(self):
        self.active_production_run.status = ProductionRun.Status.PAUSED
        self.active_production_run.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        self.client.force_login(self.supervisor)

        response = self.client.post(
            reverse(
                "production-run-pause",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 403)

        self.active_production_run.refresh_from_db()

        self.assertEqual(
            self.active_production_run.status,
            ProductionRun.Status.PAUSED,
        )

    def test_planned_production_run_cannot_be_paused(self):
        self.client.force_login(self.supervisor)

        response = self.client.post(
            reverse(
                "production-run-pause",
                kwargs={
                    "pk": self.planned_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 403)

        self.planned_production_run.refresh_from_db()

        self.assertEqual(
            self.planned_production_run.status,
            ProductionRun.Status.PLANNED,
        )

    def test_completed_production_run_cannot_be_paused(self):
        self.active_production_run.status = ProductionRun.Status.COMPLETED
        self.active_production_run.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        self.client.force_login(self.supervisor)

        response = self.client.post(
            reverse(
                "production-run-pause",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 403)

        self.active_production_run.refresh_from_db()

        self.assertEqual(
            self.active_production_run.status,
            ProductionRun.Status.COMPLETED,
        )

    def test_cancelled_production_run_cannot_be_paused(self):
        self.active_production_run.status = ProductionRun.Status.CANCELLED
        self.active_production_run.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        self.client.force_login(self.supervisor)

        response = self.client.post(
            reverse(
                "production-run-pause",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 403)

        self.active_production_run.refresh_from_db()

        self.assertEqual(
            self.active_production_run.status,
            ProductionRun.Status.CANCELLED,
        )

    def test_supervisor_sees_resume_button_for_paused_production_run(self):
        self.active_production_run.status = ProductionRun.Status.PAUSED
        self.active_production_run.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        self.client.force_login(self.supervisor)

        response = self.client.get(
            reverse(
                "production-run-detail",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Resume Production Run",
        )

    def test_resume_button_is_not_shown_for_active_production_run(self):
        self.client.force_login(self.supervisor)

        response = self.client.get(
            reverse(
                "production-run-detail",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            "Resume Production Run",
        )

    def test_resume_button_is_not_shown_for_planned_production_run(self):
        self.client.force_login(self.supervisor)

        response = self.client.get(
            reverse(
                "production-run-detail",
                kwargs={
                    "pk": self.planned_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            "Resume Production Run",
        )

    def test_operator_cannot_resume_production_run(self):
        self.active_production_run.status = ProductionRun.Status.PAUSED
        self.active_production_run.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        self.client.force_login(self.operator)

        response = self.client.post(
            reverse(
                "production-run-resume",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 403)

        self.active_production_run.refresh_from_db()

        self.assertEqual(
            self.active_production_run.status,
            ProductionRun.Status.PAUSED,
        )

    def test_production_run_resume_requires_post(self):
        self.active_production_run.status = ProductionRun.Status.PAUSED
        self.active_production_run.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        self.client.force_login(self.supervisor)

        response = self.client.get(
            reverse(
                "production-run-resume",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 403)

        self.active_production_run.refresh_from_db()

        self.assertEqual(
            self.active_production_run.status,
            ProductionRun.Status.PAUSED,
        )

    def test_supervisor_can_resume_paused_production_run(self):
        started_at = timezone.now()

        self.active_production_run.status = ProductionRun.Status.PAUSED
        self.active_production_run.started_at = started_at
        self.active_production_run.ended_at = None
        self.active_production_run.save(
            update_fields=[
                "status",
                "started_at",
                "ended_at",
                "updated_at",
            ]
        )

        self.client.force_login(self.supervisor)

        response = self.client.post(
            reverse(
                "production-run-resume",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.active_production_run.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse(
                "production-run-detail",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            ),
        )
        self.assertEqual(
            self.active_production_run.status,
            ProductionRun.Status.ACTIVE,
        )
        self.assertEqual(
            self.active_production_run.started_at,
            started_at,
        )
        self.assertIsNone(
            self.active_production_run.ended_at
        )

    def test_active_production_run_cannot_be_resumed(self):
        self.client.force_login(self.supervisor)

        response = self.client.post(
            reverse(
                "production-run-resume",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 403)

        self.active_production_run.refresh_from_db()

        self.assertEqual(
            self.active_production_run.status,
            ProductionRun.Status.ACTIVE,
        )

    def test_planned_production_run_cannot_be_resumed(self):
        self.client.force_login(self.supervisor)

        response = self.client.post(
            reverse(
                "production-run-resume",
                kwargs={
                    "pk": self.planned_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 403)

        self.planned_production_run.refresh_from_db()

        self.assertEqual(
            self.planned_production_run.status,
            ProductionRun.Status.PLANNED,
        )

    def test_completed_production_run_cannot_be_resumed(self):
        self.active_production_run.status = ProductionRun.Status.COMPLETED
        self.active_production_run.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        self.client.force_login(self.supervisor)

        response = self.client.post(
            reverse(
                "production-run-resume",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 403)

        self.active_production_run.refresh_from_db()

        self.assertEqual(
            self.active_production_run.status,
            ProductionRun.Status.COMPLETED,
        )

    def test_cancelled_production_run_cannot_be_resumed(self):
        self.active_production_run.status = ProductionRun.Status.CANCELLED
        self.active_production_run.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        self.client.force_login(self.supervisor)

        response = self.client.post(
            reverse(
                "production-run-resume",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 403)

        self.active_production_run.refresh_from_db()

        self.assertEqual(
            self.active_production_run.status,
            ProductionRun.Status.CANCELLED,
        )

    def test_resume_is_blocked_when_work_order_has_another_active_run(self):
        self.active_production_run.status = ProductionRun.Status.PAUSED
        self.active_production_run.started_at = timezone.now()
        self.active_production_run.save(
            update_fields=[
                "status",
                "started_at",
                "updated_at",
            ]
        )

        conflicting_active_run = ProductionRun.objects.create(
            work_order=self.work_order,
            production_line=self.second_production_line,
            shift=self.second_shift,
            status=ProductionRun.Status.ACTIVE,
            started_at=timezone.now(),
            notes="Synthetic FO-015 resume conflict test.",
        )

        self.client.force_login(self.supervisor)

        response = self.client.post(
            reverse(
                "production-run-resume",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 403)

        self.active_production_run.refresh_from_db()

        self.assertEqual(
            self.active_production_run.status,
            ProductionRun.Status.PAUSED,
        )

        conflicting_active_run.refresh_from_db()

        self.assertEqual(
            conflicting_active_run.status,
            ProductionRun.Status.ACTIVE,
        )

    def test_supervisor_sees_complete_button_for_active_production_run(self):
        self.client.force_login(self.supervisor)

        response = self.client.get(
            reverse(
                "production-run-detail",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Complete Production Run",
        )

    def test_complete_button_is_not_shown_for_planned_production_run(self):
        self.client.force_login(self.supervisor)

        response = self.client.get(
            reverse(
                "production-run-detail",
                kwargs={
                    "pk": self.planned_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            "Complete Production Run",
        )

    def test_complete_button_is_not_shown_for_paused_production_run(self):
        self.active_production_run.status = ProductionRun.Status.PAUSED
        self.active_production_run.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        self.client.force_login(self.supervisor)

        response = self.client.get(
            reverse(
                "production-run-detail",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            "Complete Production Run",
        )

    def test_operator_cannot_complete_production_run(self):
        self.client.force_login(self.operator)

        response = self.client.post(
            reverse(
                "production-run-complete",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 403)

        self.active_production_run.refresh_from_db()

        self.assertEqual(
            self.active_production_run.status,
            ProductionRun.Status.ACTIVE,
        )
        self.assertIsNone(
            self.active_production_run.ended_at
        )

    def test_production_run_complete_requires_post(self):
        self.client.force_login(self.supervisor)

        response = self.client.get(
            reverse(
                "production-run-complete",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 403)

        self.active_production_run.refresh_from_db()

        self.assertEqual(
            self.active_production_run.status,
            ProductionRun.Status.ACTIVE,
        )
        self.assertIsNone(
            self.active_production_run.ended_at
        )

    def test_supervisor_can_complete_active_production_run(self):
        started_at = timezone.now()

        self.active_production_run.started_at = started_at
        self.active_production_run.ended_at = None
        self.active_production_run.save(
            update_fields=[
                "started_at",
                "ended_at",
                "updated_at",
            ]
        )

        self.client.force_login(self.supervisor)

        response = self.client.post(
            reverse(
                "production-run-complete",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.active_production_run.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse(
                "production-run-detail",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            ),
        )
        self.assertEqual(
            self.active_production_run.status,
            ProductionRun.Status.COMPLETED,
        )
        self.assertEqual(
            self.active_production_run.started_at,
            started_at,
        )
        self.assertIsNotNone(
            self.active_production_run.ended_at
        )
        self.assertGreaterEqual(
            self.active_production_run.ended_at,
            started_at,
        )

    def test_planned_production_run_cannot_be_completed(self):
        self.client.force_login(self.supervisor)

        response = self.client.post(
            reverse(
                "production-run-complete",
                kwargs={
                    "pk": self.planned_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 403)

        self.planned_production_run.refresh_from_db()

        self.assertEqual(
            self.planned_production_run.status,
            ProductionRun.Status.PLANNED,
        )
        self.assertIsNone(
            self.planned_production_run.ended_at
        )

    def test_paused_production_run_cannot_be_completed(self):
        self.active_production_run.status = ProductionRun.Status.PAUSED
        self.active_production_run.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        self.client.force_login(self.supervisor)

        response = self.client.post(
            reverse(
                "production-run-complete",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 403)

        self.active_production_run.refresh_from_db()

        self.assertEqual(
            self.active_production_run.status,
            ProductionRun.Status.PAUSED,
        )
        self.assertIsNone(
            self.active_production_run.ended_at
        )

    def test_completed_production_run_cannot_be_completed_again(self):
        self.active_production_run.status = ProductionRun.Status.COMPLETED
        self.active_production_run.ended_at = timezone.now()
        self.active_production_run.save(
            update_fields=[
                "status",
                "ended_at",
                "updated_at",
            ]
        )

        original_ended_at = self.active_production_run.ended_at

        self.client.force_login(self.supervisor)

        response = self.client.post(
            reverse(
                "production-run-complete",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 403)

        self.active_production_run.refresh_from_db()

        self.assertEqual(
            self.active_production_run.status,
            ProductionRun.Status.COMPLETED,
        )
        self.assertEqual(
            self.active_production_run.ended_at,
            original_ended_at,
        )

    def test_cancelled_production_run_cannot_be_completed(self):
        self.active_production_run.status = ProductionRun.Status.CANCELLED
        self.active_production_run.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        self.client.force_login(self.supervisor)

        response = self.client.post(
            reverse(
                "production-run-complete",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 403)

        self.active_production_run.refresh_from_db()

        self.assertEqual(
            self.active_production_run.status,
            ProductionRun.Status.CANCELLED,
        )
        self.assertIsNone(
            self.active_production_run.ended_at
        )

    def test_supervisor_sees_cancel_button_for_planned_production_run(self):
        self.client.force_login(self.supervisor)

        response = self.client.get(
            reverse(
                "production-run-detail",
                kwargs={
                    "pk": self.planned_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Cancel Production Run",
        )

    def test_supervisor_sees_cancel_button_for_active_production_run(self):
        self.client.force_login(self.supervisor)

        response = self.client.get(
            reverse(
                "production-run-detail",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Cancel Production Run",
        )

    def test_supervisor_sees_cancel_button_for_paused_production_run(self):
        self.active_production_run.status = ProductionRun.Status.PAUSED
        self.active_production_run.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        self.client.force_login(self.supervisor)

        response = self.client.get(
            reverse(
                "production-run-detail",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Cancel Production Run",
        )

    def test_cancel_button_is_not_shown_for_completed_production_run(self):
        self.active_production_run.status = ProductionRun.Status.COMPLETED
        self.active_production_run.ended_at = timezone.now()
        self.active_production_run.save(
            update_fields=[
                "status",
                "ended_at",
                "updated_at",
            ]
        )

        self.client.force_login(self.supervisor)

        response = self.client.get(
            reverse(
                "production-run-detail",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            "Cancel Production Run",
        )

    def test_cancel_button_is_not_shown_for_cancelled_production_run(self):
        self.active_production_run.status = ProductionRun.Status.CANCELLED
        self.active_production_run.ended_at = timezone.now()
        self.active_production_run.save(
            update_fields=[
                "status",
                "ended_at",
                "updated_at",
            ]
        )

        self.client.force_login(self.supervisor)

        response = self.client.get(
            reverse(
                "production-run-detail",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            "Cancel Production Run",
        )

    def test_operator_cannot_cancel_production_run(self):
        self.client.force_login(self.operator)

        response = self.client.post(
            reverse(
                "production-run-cancel",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 403)

        self.active_production_run.refresh_from_db()

        self.assertEqual(
            self.active_production_run.status,
            ProductionRun.Status.ACTIVE,
        )
        self.assertIsNone(
            self.active_production_run.ended_at
        )

    def test_production_run_cancel_requires_post(self):
        self.client.force_login(self.supervisor)

        response = self.client.get(
            reverse(
                "production-run-cancel",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 403)

        self.active_production_run.refresh_from_db()

        self.assertEqual(
            self.active_production_run.status,
            ProductionRun.Status.ACTIVE,
        )
        self.assertIsNone(
            self.active_production_run.ended_at
        )

    def test_supervisor_can_cancel_planned_production_run(self):
        self.client.force_login(self.supervisor)

        response = self.client.post(
            reverse(
                "production-run-cancel",
                kwargs={
                    "pk": self.planned_production_run.pk,
                },
            )
        )

        self.planned_production_run.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse(
                "production-run-detail",
                kwargs={
                    "pk": self.planned_production_run.pk,
                },
            ),
        )
        self.assertEqual(
            self.planned_production_run.status,
            ProductionRun.Status.CANCELLED,
        )
        self.assertIsNone(
            self.planned_production_run.started_at
        )
        self.assertIsNone(
            self.planned_production_run.ended_at
        )

    def test_supervisor_can_cancel_active_production_run(self):
        started_at = timezone.now()

        self.active_production_run.started_at = started_at
        self.active_production_run.ended_at = None
        self.active_production_run.save(
            update_fields=[
                "started_at",
                "ended_at",
                "updated_at",
            ]
        )

        self.client.force_login(self.supervisor)

        response = self.client.post(
            reverse(
                "production-run-cancel",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.active_production_run.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse(
                "production-run-detail",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            ),
        )
        self.assertEqual(
            self.active_production_run.status,
            ProductionRun.Status.CANCELLED,
        )
        self.assertEqual(
            self.active_production_run.started_at,
            started_at,
        )
        self.assertIsNotNone(
            self.active_production_run.ended_at
        )
        self.assertGreaterEqual(
            self.active_production_run.ended_at,
            started_at,
        )

    def test_supervisor_can_cancel_paused_production_run(self):
        started_at = timezone.now()

        self.active_production_run.status = ProductionRun.Status.PAUSED
        self.active_production_run.started_at = started_at
        self.active_production_run.ended_at = None
        self.active_production_run.save(
            update_fields=[
                "status",
                "started_at",
                "ended_at",
                "updated_at",
            ]
        )

        self.client.force_login(self.supervisor)

        response = self.client.post(
            reverse(
                "production-run-cancel",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.active_production_run.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse(
                "production-run-detail",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            ),
        )
        self.assertEqual(
            self.active_production_run.status,
            ProductionRun.Status.CANCELLED,
        )
        self.assertEqual(
            self.active_production_run.started_at,
            started_at,
        )
        self.assertIsNotNone(
            self.active_production_run.ended_at
        )
        self.assertGreaterEqual(
            self.active_production_run.ended_at,
            started_at,
        )

    def test_completed_production_run_cannot_be_cancelled(self):
        started_at = timezone.now()
        ended_at = timezone.now()

        self.active_production_run.status = ProductionRun.Status.COMPLETED
        self.active_production_run.started_at = started_at
        self.active_production_run.ended_at = ended_at
        self.active_production_run.save(
            update_fields=[
                "status",
                "started_at",
                "ended_at",
                "updated_at",
            ]
        )

        self.client.force_login(self.supervisor)

        response = self.client.post(
            reverse(
                "production-run-cancel",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 403)

        self.active_production_run.refresh_from_db()

        self.assertEqual(
            self.active_production_run.status,
            ProductionRun.Status.COMPLETED,
        )
        self.assertEqual(
            self.active_production_run.started_at,
            started_at,
        )
        self.assertEqual(
            self.active_production_run.ended_at,
            ended_at,
        )

    def test_cancelled_production_run_cannot_be_cancelled_again(self):
        started_at = timezone.now()
        ended_at = timezone.now()

        self.active_production_run.status = ProductionRun.Status.CANCELLED
        self.active_production_run.started_at = started_at
        self.active_production_run.ended_at = ended_at
        self.active_production_run.save(
            update_fields=[
                "status",
                "started_at",
                "ended_at",
                "updated_at",
            ]
        )

        self.client.force_login(self.supervisor)

        response = self.client.post(
            reverse(
                "production-run-cancel",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 403)

        self.active_production_run.refresh_from_db()

        self.assertEqual(
            self.active_production_run.status,
            ProductionRun.Status.CANCELLED,
        )
        self.assertEqual(
            self.active_production_run.started_at,
            started_at,
        )
        self.assertEqual(
            self.active_production_run.ended_at,
            ended_at,
        )

class ProductionEntryInterfaceTests(TestCase):
    password = "ForgeOps-Test-Password-2026!"

    @classmethod
    def setUpTestData(cls):
        User = get_user_model()

        cls.operator_group = Group.objects.get(
            name="Operator"
        )
        cls.supervisor_group = Group.objects.get(
            name="Production Supervisor"
        )

        cls.operator = User.objects.create_user(
            username="fo018_operator",
            password=cls.password,
        )
        cls.operator.groups.add(cls.operator_group)

        cls.supervisor = User.objects.create_user(
            username="fo018_supervisor",
            password=cls.password,
        )
        cls.supervisor.groups.add(cls.supervisor_group)

        cls.site = Site.objects.create(
            code="FO018-SITE",
            name="Synthetic FO-018 Site",
            description=(
                "Synthetic site for FO-018 "
                "ProductionEntry interface tests."
            ),
        )

        cls.production_area = ProductionArea.objects.create(
            site=cls.site,
            code="FO018-AREA",
            name="Synthetic FO-018 Area",
            description=(
                "Synthetic production area for FO-018 tests."
            ),
        )

        cls.production_line = ProductionLine.objects.create(
            production_area=cls.production_area,
            code="FO018-LINE",
            name="Synthetic FO-018 Line",
            description=(
                "Synthetic Production Line for FO-018 tests."
            ),
        )

        cls.shift = Shift.objects.create(
            name="FO-018 Test Shift",
            start_time=time(7, 0),
            end_time=time(15, 0),
        )

        cls.product = Product.objects.create(
            code="PRD-FO018",
            name="Synthetic FO-018 Product",
            description=(
                "Synthetic Product for FO-018 interface tests."
            ),
        )

        cls.work_order = WorkOrder.objects.create(
            order_number="WO-FO018-0001",
            product=cls.product,
            planned_quantity=500,
            status=WorkOrder.Status.RELEASED,
            due_date=date(2026, 8, 31),
            notes="Synthetic Work Order for FO-018.",
        )

        cls.active_production_run = ProductionRun.objects.create(
            work_order=cls.work_order,
            production_line=cls.production_line,
            shift=cls.shift,
            status=ProductionRun.Status.ACTIVE,
            started_at=timezone.now(),
            notes=(
                "Synthetic ACTIVE Production Run "
                "for FO-018."
            ),
        )

        cls.planned_work_order = WorkOrder.objects.create(
            order_number="WO-FO018-0002",
            product=cls.product,
            planned_quantity=500,
            status=WorkOrder.Status.RELEASED,
            due_date=date(2026, 9, 1),
            notes=(
                "Synthetic Work Order for PLANNED "
                "FO-018 Production Run."
            ),
        )

        cls.planned_production_run = ProductionRun.objects.create(
            work_order=cls.planned_work_order,
            production_line=cls.production_line,
            shift=cls.shift,
            status=ProductionRun.Status.PLANNED,
            notes=(
                "Synthetic PLANNED Production Run "
                "for FO-018."
            ),
        )

    def test_production_entry_create_requires_login(self):
        response = self.client.get(
            reverse(
                "production-entry-create",
                kwargs={
                    "production_run_pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            "/accounts/login/",
            response.url,
        )

    def test_operator_can_access_production_entry_create_page(self):
        self.client.force_login(self.operator)

        response = self.client.get(
            reverse(
                "production-entry-create",
                kwargs={
                    "production_run_pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Record Production Entry",
        )
        self.assertContains(
            response,
            self.work_order.order_number,
        )

    def test_supervisor_can_access_production_entry_create_page(self):
        self.client.force_login(self.supervisor)

        response = self.client.get(
            reverse(
                "production-entry-create",
                kwargs={
                    "production_run_pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Record Production Entry",
        )

    def test_operator_sees_record_entry_button_for_active_run(self):
        self.client.force_login(self.operator)

        response = self.client.get(
            reverse(
                "production-run-detail",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Record Production Entry",
        )

    def test_record_entry_button_not_shown_for_planned_run(self):
        self.client.force_login(self.operator)

        response = self.client.get(
            reverse(
                "production-run-detail",
                kwargs={
                    "pk": self.planned_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            "Record Production Entry",
        )

    def test_record_entry_button_not_shown_for_paused_run(self):
        self.active_production_run.status = ProductionRun.Status.PAUSED
        self.active_production_run.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        self.client.force_login(self.operator)

        response = self.client.get(
            reverse(
                "production-run-detail",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            "Record Production Entry",
        )

    def test_record_entry_button_not_shown_for_completed_run(self):
        self.active_production_run.status = ProductionRun.Status.COMPLETED
        self.active_production_run.ended_at = timezone.now()
        self.active_production_run.save(
            update_fields=[
                "status",
                "ended_at",
                "updated_at",
            ]
        )

        self.client.force_login(self.operator)

        response = self.client.get(
            reverse(
                "production-run-detail",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            "Record Production Entry",
        )

    def test_record_entry_button_not_shown_for_cancelled_run(self):
        self.active_production_run.status = ProductionRun.Status.CANCELLED
        self.active_production_run.ended_at = timezone.now()
        self.active_production_run.save(
            update_fields=[
                "status",
                "ended_at",
                "updated_at",
            ]
        )

        self.client.force_login(self.operator)

        response = self.client.get(
            reverse(
                "production-run-detail",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(
            response,
            "Record Production Entry",
        )

    def test_operator_can_create_valid_production_entry(self):
        self.client.force_login(self.operator)

        response = self.client.post(
            reverse(
                "production-entry-create",
                kwargs={
                    "production_run_pk": self.active_production_run.pk,
                },
            ),
            {
                "good_quantity": 48,
                "rejected_quantity": 2,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse(
                "production-run-detail",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            ),
        )

        entry = ProductionEntry.objects.get(
            production_run=self.active_production_run
        )

        self.assertEqual(
            entry.good_quantity,
            48,
        )
        self.assertEqual(
            entry.rejected_quantity,
            2,
        )

    def test_created_entry_belongs_to_requested_production_run(self):
        self.client.force_login(self.operator)

        self.client.post(
            reverse(
                "production-entry-create",
                kwargs={
                    "production_run_pk": self.active_production_run.pk,
                },
            ),
            {
                "good_quantity": 25,
                "rejected_quantity": 5,
            },
        )

        entry = ProductionEntry.objects.get(
            production_run=self.active_production_run
        )

        self.assertEqual(
            entry.production_run,
            self.active_production_run,
        )

    def test_recorded_by_is_authenticated_user(self):
        self.client.force_login(self.operator)

        self.client.post(
            reverse(
                "production-entry-create",
                kwargs={
                    "production_run_pk": self.active_production_run.pk,
                },
            ),
            {
                "good_quantity": 20,
                "rejected_quantity": 1,
            },
        )

        entry = ProductionEntry.objects.get(
            production_run=self.active_production_run
        )

        self.assertEqual(
            entry.recorded_by,
            self.operator,
        )

    def test_zero_good_and_zero_rejected_is_rejected(self):
        self.client.force_login(self.operator)

        response = self.client.post(
            reverse(
                "production-entry-create",
                kwargs={
                    "production_run_pk": self.active_production_run.pk,
                },
            ),
            {
                "good_quantity": 0,
                "rejected_quantity": 0,
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertFalse(
            ProductionEntry.objects.filter(
                production_run=self.active_production_run
            ).exists()
        )

    def test_negative_good_quantity_is_rejected(self):
        self.client.force_login(self.operator)

        response = self.client.post(
            reverse(
                "production-entry-create",
                kwargs={
                    "production_run_pk": self.active_production_run.pk,
                },
            ),
            {
                "good_quantity": -1,
                "rejected_quantity": 1,
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertFalse(
            ProductionEntry.objects.filter(
                production_run=self.active_production_run
            ).exists()
        )

    def test_negative_rejected_quantity_is_rejected(self):
        self.client.force_login(self.operator)

        response = self.client.post(
            reverse(
                "production-entry-create",
                kwargs={
                    "production_run_pk": self.active_production_run.pk,
                },
            ),
            {
                "good_quantity": 1,
                "rejected_quantity": -1,
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertFalse(
            ProductionEntry.objects.filter(
                production_run=self.active_production_run
            ).exists()
        )

    def test_planned_run_cannot_accept_production_entry(self):
        self.client.force_login(self.operator)

        response = self.client.get(
            reverse(
                "production-entry-create",
                kwargs={
                    "production_run_pk": self.planned_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_paused_run_cannot_accept_production_entry(self):
        self.active_production_run.status = ProductionRun.Status.PAUSED
        self.active_production_run.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        self.client.force_login(self.operator)

        response = self.client.get(
            reverse(
                "production-entry-create",
                kwargs={
                    "production_run_pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_completed_run_cannot_accept_production_entry(self):
        self.active_production_run.status = ProductionRun.Status.COMPLETED
        self.active_production_run.ended_at = timezone.now()
        self.active_production_run.save(
            update_fields=[
                "status",
                "ended_at",
                "updated_at",
            ]
        )

        self.client.force_login(self.operator)

        response = self.client.get(
            reverse(
                "production-entry-create",
                kwargs={
                    "production_run_pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_cancelled_run_cannot_accept_production_entry(self):
        self.active_production_run.status = ProductionRun.Status.CANCELLED
        self.active_production_run.ended_at = timezone.now()
        self.active_production_run.save(
            update_fields=[
                "status",
                "ended_at",
                "updated_at",
            ]
        )

        self.client.force_login(self.operator)

        response = self.client.get(
            reverse(
                "production-entry-create",
                kwargs={
                    "production_run_pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 403)

    def test_multiple_entries_update_good_quantity_total(self):
        ProductionEntry.objects.create(
            production_run=self.active_production_run,
            good_quantity=48,
            rejected_quantity=2,
            recorded_by=self.operator,
        )

        ProductionEntry.objects.create(
            production_run=self.active_production_run,
            good_quantity=88,
            rejected_quantity=12,
            recorded_by=self.supervisor,
        )

        self.assertEqual(
            self.active_production_run.good_quantity,
            136,
        )

    def test_multiple_entries_update_rejected_quantity_total(self):
        ProductionEntry.objects.create(
            production_run=self.active_production_run,
            good_quantity=48,
            rejected_quantity=2,
            recorded_by=self.operator,
        )

        ProductionEntry.objects.create(
            production_run=self.active_production_run,
            good_quantity=88,
            rejected_quantity=12,
            recorded_by=self.supervisor,
        )

        self.assertEqual(
            self.active_production_run.rejected_quantity,
            14,
        )

    def test_multiple_entries_update_total_recorded_quantity(self):
        ProductionEntry.objects.create(
            production_run=self.active_production_run,
            good_quantity=48,
            rejected_quantity=2,
            recorded_by=self.operator,
        )

        ProductionEntry.objects.create(
            production_run=self.active_production_run,
            good_quantity=88,
            rejected_quantity=12,
            recorded_by=self.supervisor,
        )

        self.assertEqual(
            self.active_production_run.total_recorded_quantity,
            150,
        )

    def test_multiple_entries_update_completion_percentage(self):
        ProductionEntry.objects.create(
            production_run=self.active_production_run,
            good_quantity=48,
            rejected_quantity=2,
            recorded_by=self.operator,
        )

        ProductionEntry.objects.create(
            production_run=self.active_production_run,
            good_quantity=88,
            rejected_quantity=12,
            recorded_by=self.supervisor,
        )

        self.assertEqual(
            self.active_production_run.completion_percentage,
            30.0,
        )

    def test_production_run_detail_displays_production_entries(self):
        ProductionEntry.objects.create(
            production_run=self.active_production_run,
            good_quantity=48,
            rejected_quantity=2,
            recorded_by=self.operator,
        )

        self.client.force_login(self.operator)

        response = self.client.get(
            reverse(
                "production-run-detail",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "Production Entries",
        )
        self.assertContains(
            response,
            self.operator.username,
        )

    def test_production_run_detail_displays_empty_entry_state(self):
        self.client.force_login(self.operator)

        response = self.client.get(
            reverse(
                "production-run-detail",
                kwargs={
                    "pk": self.active_production_run.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "No production entries recorded.",
        )

    def test_production_entries_are_displayed_newest_first(self):
        first_entry = ProductionEntry.objects.create(
            production_run=self.active_production_run,
            good_quantity=10,
            rejected_quantity=1,
            recorded_by=self.operator,
        )

        second_entry = ProductionEntry.objects.create(
            production_run=self.active_production_run,
            good_quantity=20,
            rejected_quantity=2,
            recorded_by=self.supervisor,
        )

        entries = list(
            self.active_production_run.production_entries.all()
        )

        self.assertEqual(
            entries[0],
            second_entry,
        )
        self.assertEqual(
            entries[1],
            first_entry,
        )