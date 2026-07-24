# scripts/createrandomorders.py
#
# Usage (most robust, works identically on Windows and Unix):
#   python manage.py shell -c "exec(open('scripts/createrandomorders.py', encoding='utf-8').read())"
#
# Also works, but is more fragile on some Windows setups:
#   python manage.py shell < scripts/createrandomorders.py
#
# What it does:
#   1. Gets or creates a default PaymentProvider.
#   2. Creates ~100 random Orders, each belonging to a random existing User.
#   3. For every Order, creates 1-4 random OrderItems using existing
#      ProductVariants.
#   4. Creates one OrderPayment per Order (with a matching
#      PaymentProviderTransaction) whose amount equals the sum of that
#      order's item subtotals.
#
# Requirements:
#   - At least one User must already exist in the database.
#   - At least one ProductVariant must already exist in the database.
#   (The script will abort with a clear message if either is missing.)
#
# NOTE: All logic lives inside run() and has no blank lines in its body.
# This is deliberate: when this file is fed to `manage.py shell` via stdin
# redirection (`<`), Python's plain interactive console treats a blank line
# as "end of the current indented block" -- so a blank line inside a for/if
# body silently truncates it and everything after gets misread as
# top-level code, causing spurious IndentationErrors. Keeping the body
# blank-line-free avoids that failure mode. The `exec(open(...).read())`
# invocation above sidesteps the problem entirely by compiling the whole
# file as one unit, so it's the preferred way to run this.

import random
from datetime import timedelta
from django.utils import timezone


def run():
    from accounts.models import User
    from products.default.models import ProductVariant
    from payment.models import PaymentProvider, PaymentProviderTransaction
    from orders.models import Order, OrderItem, OrderPayment
    TOTAL_ORDERS = 100
    MAX_ITEMS_PER_ORDER = 4
    MIN_ITEMS_PER_ORDER = 1
    STATUS_CHOICES = [Order.Status.PENDING, Order.Status.FULFILLED, Order.Status.RETURNED]
    print("=" * 60)
    print("Generando ordenes aleatorias...")
    print("=" * 60)
    payment_provider, created = PaymentProvider.objects.get_or_create(
        name="Cash / Default Provider",
        defaults={
            "description": "Proveedor de pago por defecto generado por el script de seed.",
            "is_default": True,
        },
    )
    print("PaymentProvider %s: %s" % ("creado" if created else "ya existia", payment_provider.name))
    users = list(User.objects.all())
    if not users:
        raise SystemExit("No hay usuarios (User) en la base de datos. Crea al menos uno antes de correr este script.")
    variants = list(ProductVariant.objects.all())
    if not variants:
        raise SystemExit("No hay ProductVariant en la base de datos. Crea al menos una antes de correr este script.")
    print("Usuarios disponibles: %d" % len(users))
    print("Variantes de producto disponibles: %d" % len(variants))
    now = timezone.now()
    orders_created = 0
    items_created = 0
    payments_created = 0
    for i in range(TOTAL_ORDERS):
        customer = random.choice(users)
        status = random.choice(STATUS_CHOICES)
        created_at_offset = timedelta(days=random.randint(0, 30), hours=random.randint(0, 23), minutes=random.randint(0, 59))
        order_created_at = now - created_at_offset
        has_pickup = random.random() > 0.25
        pickup_time = (order_created_at + timedelta(days=random.randint(1, 7))) if has_pickup else None
        order = Order.objects.create(customer=customer, status=status, pickup_time=pickup_time)
        Order.objects.filter(pk=order.pk).update(created_at=order_created_at)
        order.refresh_from_db()
        orders_created += 1
        item_count = random.randint(MIN_ITEMS_PER_ORDER, MAX_ITEMS_PER_ORDER)
        chosen_variants = random.sample(variants, k=min(item_count, len(variants)))
        order_subtotal = 0.0
        for variant in chosen_variants:
            quantity = random.randint(1, 5)
            price_per_item = float(variant.selling_price)
            tax_amount = round(price_per_item * float(variant.tax_rate) / 100, 2)
            OrderItem.objects.create(order=order, product=variant, quantity=quantity, price_per_item=price_per_item, tax_amount=tax_amount)
            order_subtotal += (price_per_item + tax_amount) * quantity
            items_created += 1
        transaction = PaymentProviderTransaction.objects.create(payment_provider=payment_provider, reference_document="SEED-TXN-%s-%s" % (order.id, random.randint(1000, 9999)), amount=round(order_subtotal, 2), tax=0)
        OrderPayment.objects.create(order=order, payment_provider=payment_provider, payment_provider_transaction=transaction, amount=round(order_subtotal, 2), tax_amount=0)
        payments_created += 1
        if (i + 1) % 10 == 0:
            print("  ...%d/%d ordenes creadas" % (i + 1, TOTAL_ORDERS))
    print("=" * 60)
    print("Listo.")
    print("Ordenes creadas: %d" % orders_created)
    print("Items creados: %d" % items_created)
    print("Pagos creados: %d" % payments_created)
    print("=" * 60)


run()