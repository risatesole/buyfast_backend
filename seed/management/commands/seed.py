from django.core.management.base import BaseCommand
from payment.models import PaymentProvider
from products.default.models import Category
from store.models import CarouselSlide

PROVIDERS = [
    {"name": "Los Santos Bank",               "description": "Los Santos Bank payment provider"},
    {"name": "Banco Popular Dominicana",       "description": "Banco Popular Dominicana payment provider"},
    {"name": "Banreservas",                    "description": "Banco de Reservas de la Republica Dominicana"},
]

CATEGORIES = [
    {
        "slug": "stationery",
        "name": "Papelería y Suministros",
        "description": "Cuadernos, bolígrafos, papel y material gastable.",
        "priority": 1,
        "image_banner": "https://images.unsplash.com/photo-1497366754035-f200968a6e72?w=1200&h=400&fit=crop",
        "image_cart": "https://images.unsplash.com/photo-1497366754035-f200968a6e72?w=100&h=100&fit=crop",
        "image_default": "https://images.unsplash.com/photo-1497366754035-f200968a6e72?w=400&h=400&fit=crop",
    },
    {
        "slug": "books_manuals",
        "name": "Libros y Manuales",
        "description": "Textos universitarios, manuales de laboratorio y guías.",
        "priority": 1,
        "image_banner": "https://images.unsplash.com/photo-150784272343-583f20270319?w=1200&h=400&fit=crop",
        "image_cart": "https://images.unsplash.com/photo-1507842872343-583f20270319?w=100&h=100&fit=crop",
        "image_default": "https://images.unsplash.com/photo-1507842872343-583f20270319?w=400&h=400&fit=crop",
    },
    {
        "slug": "medical_lab",
        "name": "Medicina y Laboratorio",
        "description": "Estetoscopios, batas médicas, kits de disección y bioseguridad.",
        "priority": 1,
        "image_banner": "https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=1200&h=400&fit=crop",
        "image_cart": "https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=100&h=100&fit=crop",
        "image_default": "https://images.unsplash.com/photo-1576091160550-2173dba999ef?w=400&h=400&fit=crop",
    },
    {
        "slug": "architecture_arts",
        "name": "Arquitectura y Artes",
        "description": "Reglas T, escalímetros, maquetas, pinturas y pinceles.",
        "priority": 2,
        "image_banner": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=1200&h=400&fit=crop",
        "image_cart": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=100&h=100&fit=crop",
        "image_default": "https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=400&h=400&fit=crop",
    },
    {
        "slug": "electronics",
        "name": "Electrónica y Calculadoras",
        "description": "Calculadoras científicas, memorias USB y accesorios periféricos.",
        "priority": 2,
        "image_banner": "https://images.unsplash.com/photo-1550355291-bbee04a92027?w=1200&h=400&fit=crop",
        "image_cart": "https://images.unsplash.com/photo-1550355291-bbee04a92027?w=100&h=100&fit=crop",
        "image_default": "https://images.unsplash.com/photo-1550355291-bbee04a92027?w=400&h=400&fit=crop",
    },
    {
        "slug": "uniforms",
        "name": "Uniformes e Institucional",
        "description": "T-shirts UASD, ropa deportiva y promocionales.",
        "priority": 3,
        "image_banner": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1200&h=400&fit=crop",
        "image_cart": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=100&h=100&fit=crop",
        "image_default": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=400&fit=crop",
    },
    {
        "slug": "snacks_beverages",
        "name": "Snacks y Bebidas",
        "description": "Comida rápida, café, agua y meriendas.",
        "priority": 3,
        "image_banner": "https://images.unsplash.com/photo-1495521821757-a1efb6729352?w=1200&h=400&fit=crop",
        "image_cart": "https://images.unsplash.com/photo-1495521821757-a1efb6729352?w=100&h=100&fit=crop",
        "image_default": "https://images.unsplash.com/photo-1495521821757-a1efb6729352?w=400&h=400&fit=crop",
    },
]


class Command(BaseCommand):
    help = "Seed payment providers and product categories"

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

        # Seed Product Categories
        self.stdout.write(self.style.WARNING("=== Seeding Product Categories ==="))

        for data in CATEGORIES:
            category, created = Category.objects.get_or_create(
                slug=data["slug"],
                defaults={
                    "name": data["name"],
                    "description": data["description"],
                    "priority": data["priority"],
                    "image_banner": data["image_banner"],
                    "image_cart": data["image_cart"],
                    "image_default": data["image_default"],
                },
            )

            status = "created" if created else "already exists"
            self.stdout.write(f"  {category.name} — {status}")

        self.stdout.write(
            self.style.SUCCESS("\n✓ Done seeding product categories.\n")
        )

        # Seed Carousel Slides
        self.stdout.write(self.style.WARNING("=== Seeding Carousel Slides ==="))

        slides_data = [
            {
                "id": "1",
                "image": "https://zdnhvnvrngxvxedrvuon.supabase.co/storage/v1/object/public/bucket1/carrousel/calculadoras.png",
                "title": "Calculadoras",
                "description": "Descubre la que va con tu estilo",
                "button_text": "Comprar Ahora",
                "button_link": "categories",
                "order": 1,
                "is_active": True,
            },
            {
                "id": "2",
                "image": "https://zdnhvnvrngxvxedrvuon.supabase.co/storage/v1/object/public/bucket1/carrousel/manualeslab.png",
                "title": "Ya Disponibles",
                "description": "No pierdas tiempo ahora es más rápido",
                "button_text": "Ver Todos",
                "button_link": "categories",
                "order": 2,
                "is_active": True,
            },
            {
                "id": "3",
                "image": "https://zdnhvnvrngxvxedrvuon.supabase.co/storage/v1/object/public/bucket1/carrousel/econodigital.jpeg",
                "title": "BuyFast",
                "description": "El mismo ecónomato, pero digital",
                "button_text": "Ver todas las categorias",
                "button_link": "categories",
                "order": 3,
                "is_active": True,
            },
        ]

        for slide_data in slides_data:
            slide, created = CarouselSlide.objects.update_or_create(
                id=slide_data["id"],
                defaults=slide_data,
            )
            status = "created" if created else "updated"
            self.stdout.write(f"  {slide.title} — {status}")

        self.stdout.write(
            self.style.SUCCESS("\n✓ Done seeding carousel slides.\n")
        )
