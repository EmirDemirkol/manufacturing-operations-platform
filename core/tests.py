from datetime import date
from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse

from .models import Product, WorkOrder


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