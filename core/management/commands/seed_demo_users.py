from getpass import getpass

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


DEMO_USERS = {
    "operator_demo": "Operator",
    "supervisor_demo": "Production Supervisor",
    "quality_demo": "Quality Specialist",
    "engineer_demo": "Manufacturing Engineer",
    "manager_demo": "Operations Manager",
    "sysadmin_demo": "System Administrator",
}


class Command(BaseCommand):
    help = "Create or update the ForgeOps demonstration users."

    def handle(self, *args, **options):
        password = getpass("Demo-user password: ")
        confirmation = getpass("Confirm password: ")

        if password != confirmation:
            raise CommandError("Passwords do not match.")

        try:
            validate_password(password)
        except ValidationError as error:
            raise CommandError(" ".join(error.messages)) from error

        groups = {
            group.name: group
            for group in Group.objects.filter(name__in=DEMO_USERS.values())
        }

        missing_groups = set(DEMO_USERS.values()) - set(groups)

        if missing_groups:
            missing = ", ".join(sorted(missing_groups))
            raise CommandError(f"Missing required groups: {missing}")

        User = get_user_model()

        with transaction.atomic():
            for username, group_name in DEMO_USERS.items():
                user, created = User.objects.get_or_create(
                    username=username,
                )

                user.is_active = True
                user.is_staff = group_name == "System Administrator"
                user.is_superuser = False
                user.set_password(password)
                user.save()

                user.groups.set([groups[group_name]])

                action = "Created" if created else "Updated"
                self.stdout.write(
                    self.style.SUCCESS(
                        f"{action} {username} as {group_name}"
                    )
                )