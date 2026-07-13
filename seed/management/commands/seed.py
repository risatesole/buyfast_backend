from django.core.management.base import BaseCommand
from payment.models import PaymentProvider

PROVIDERS = [
    {"name": "Los Santos Bank",               "description": "Los Santos Bank payment provider"},
    {"name": "Banco Popular Dominicana",       "description": "Banco Popular Dominicana payment provider"},
    {"name": "Banreservas",                    "description": "Banco de Reservas de la Republica Dominicana"},
]


class Command(BaseCommand):
    help = "Seed payment providers"

    def add_arguments(self, parser):
        parser.add_argument(
            "--default",
            type=str,
            choices=["los_santos_bank", "banco_popular", "banreservas"],
            default="banreservas",
            help="Which provider to mark as default",
        )

    def handle(self, *args, **options):
        # Seed Payment Providers
        self.stdout.write(self.style.WARNING("\n=== Seeding Payment Providers ==="))
        
        default_map = {
            "los_santos_bank": "Los Santos Bank",
            "banco_popular":   "Banco Popular Dominicana",
            "banreservas":     "Banreservas",
        }

        default_name = default_map[options["default"]]

        for data in PROVIDERS:
            provider, created = PaymentProvider.objects.get_or_create(
                name=data["name"],
                defaults={"description": data["description"]},
            )

            is_default = provider.name == default_name

            if provider.is_default != is_default:
                provider.is_default = is_default
                provider.save()

            status = "created" if created else "already exists"
            flag = " ✔ DEFAULT" if is_default else ""

            self.stdout.write(f"  {provider.name} — {status}{flag}")

        self.stdout.write(
            self.style.SUCCESS("\n✓ Done seeding payment providers.\n")
        )
