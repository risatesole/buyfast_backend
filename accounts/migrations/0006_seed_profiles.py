from django.db import migrations


SEED_PROFILES = [
    {
        "name": "Human Resources",
        "permissions": ["employees.view", "employees.manage"],
    },
    {
        "name": "Almacen",
        "permissions": ["products.view", "inventory.view", "inventory.manage"],
    },
    {
        "name": "Ventas",
        "permissions": ["customers.view", "customers.manage", "orders.view", "orders.manage"],
    },
    {
        "name": "Superuser",
        "permissions": [
            "employees.view",
            "employees.manage",
            "customers.view",
            "customers.manage",
            "products.view",
            "products.create",
            "products.edit",
            "inventory.view",
            "inventory.manage",
            "orders.view",
            "orders.manage",
        ],
        "is_protected": True,
    },
]


def seed_profiles(apps, schema_editor):
    Profile = apps.get_model("accounts", "Profile")
    for entry in SEED_PROFILES:
        Profile.objects.get_or_create(
            name=entry["name"],
            defaults={
                "permissions": entry["permissions"],
                "is_protected": entry.get("is_protected", False),
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_profile_and_employee_profile'),
    ]

    operations = [
        migrations.RunPython(seed_profiles, reverse_code=migrations.RunPython.noop),
    ]
