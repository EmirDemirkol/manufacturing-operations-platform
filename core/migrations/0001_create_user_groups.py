from django.db import migrations


GROUP_NAMES = [
    "Operator",
    "Production Supervisor",
    "Quality Specialist",
    "Manufacturing Engineer",
    "Operations Manager",
    "System Administrator",
]


def create_user_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    database = schema_editor.connection.alias

    for group_name in GROUP_NAMES:
        Group.objects.using(database).get_or_create(name=group_name)


def delete_user_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    database = schema_editor.connection.alias

    Group.objects.using(database).filter(name__in=GROUP_NAMES).delete()


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(
            create_user_groups,
            delete_user_groups,
        ),
    ]