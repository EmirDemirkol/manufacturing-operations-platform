from io import StringIO
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse


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

# Create your tests here.
