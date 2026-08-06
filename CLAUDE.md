# Project: UASD Económato Online Store — Backend

Django/DRF backend for **UASD's Económato** (a Dominican Republic university
co-op store): students browse products, pay online, and pick the order up in
person. The frontend is a separate Next.js app (see the `frontend` project's
own `CLAUDE.md`) that talks to this API exclusively under `/api/v1/`.

**All code (models, views, variables, comments) is in English.** User-facing
strings that leak to the frontend (email bodies, error messages the UI shows
verbatim) should be written with the Spanish-speaking end user in mind, but
the codebase itself stays in English.

## Tech stack

- Django 6, Django REST Framework, `drf-spectacular` (OpenAPI schema at
  `/api/schema/`), `django-taggit`, `django-cors-headers`, `whitenoise`,
  `psycopg2-binary`, Python ≥3.12, managed with `uv` (`pyproject.toml` +
  `uv.lock`, mirrored into `requirements.txt` for Docker/Vercel).
- `djangorestframework-simplejwt` and `rest_framework.authtoken` are installed
  but **not actually used** — auth is session-based (see below). Don't assume
  JWT is live just because the package is present.
- Product images go through a local `mediaupload` package (`packages/mediaupload`)
  wrapping the Supabase Storage SDK.
- No Celery, no Channels — nothing async-specific despite `asgi.py` existing.

## Project structure

- `config/settings/` — one small file per concern (`auth/`, `database/`,
  `cors_session_and_csfr/`, `installed_apps/`, etc.), all re-exported via
  `config/settings/__init__.py`. If you need to change a setting, find its
  dedicated file rather than adding a new blob to a catch-all settings file.
- Django apps: `accounts`, `products/default`, `cart`, `checkout`, `inventory`,
  `orders`, `payment`, `store`, `seed`, plus `api` as the routing hub.
- **`api/urls.py` is the single source of truth for URL routing.** Every
  endpoint across every app is wired up in this one file, importing views from
  their owning app. When adding an endpoint, add the view in its domain app
  and wire it here — don't create a per-app `urls.py`.
- `products/default` is the most architected app (DDD-ish: `entities/`,
  `value_objects/`, `repositories/`, `services/`) — everything else uses a
  simpler `usecases/`-function style. Don't force the DDD pattern onto other
  apps; match the surrounding app's existing style instead.

## Auth model

- Custom user model `accounts.User` (`AUTH_USER_MODEL = "accounts.User"`),
  email as the username field, `role` is `"customer"` or `"employee"`
  (no Django groups/permissions-based RBAC in normal use).
- `matricula` = student ID/registration number — unique, nullable, optional at
  signup. Admin user endpoints (`/users/<id>/`) look users up by numeric PK,
  not by `matricula`.
- Session auth, not JWT. Endpoints that need CSRF-free session auth (because
  they're called cross-origin from the Next.js frontend) use
  `api/utils.py::CsrfExemptSessionAuthentication`.
- Employee-only endpoints use the shared `api/permissions.py::require_employee(request)`
  helper (401 if unauthenticated, 403 if `role != "employee"`). **Use this
  helper for any new employee-gated view — don't write a new inline
  `if request.user.role != "employee"` check.** (The inventory app's admin
  views use DRF's `permissions.IsAdminUser` instead, which is an older,
  inconsistent pattern from before this helper existed — don't copy that one
  for new code.)

## Domain model highlights

- **Products**: `Product` → `ProductVariant` → `ProductImage`. Categories are
  Económato-specific (stationery, books/manuals, medical/lab,
  architecture/arts, electronics, uniforms, snacks/beverages).
- **Inventory is ledger-based, not a mutable counter.** `StockMovement_model`
  records every change (`initial_inventory`, `purchase_entry`,
  `customer_sell`) with a running `balance`; current stock for a variant =
  its latest movement's balance. `quantity` on a movement is **always
  positive** — direction is implied by `movement_type`, not the sign. Use the
  shared `inventory/queries.py::annotate_variant_stock(queryset)` to get a
  `total_quantity` annotation on a `ProductVariant` queryset — don't re-write
  the `Coalesce(Sum('stock_movements__balance'), ...)` pattern inline.
- **Orders**: `Order` (status: `pending` / `fulfilled` / `returned` — **no
  "paid" or "cancelled" state exists yet**) → `OrderItem` → `OrderPayment`.
  Use the shared `orders/queries.py::annotate_order_totals(queryset)` to get
  `total_amount`/`total_tax`/`item_count` on an `Order` queryset instead of
  re-deriving the `Sum(F(...) * F(...))` annotation.
- **Payments are not actually wired up.** `payment/usecases/process_payment.py`
  exists (Luhn validation + would-be transaction record) but checkout never
  calls it — only card validation runs. `OrderPayment` rows are never created
  today. `PaymentProvider` models a **bank** (Banreservas, Banco Popular, a
  test bank), not a gateway SDK — there's no live Stripe/Azul/CardNet
  integration. Don't assume payment succeeded/failed based on `OrderPayment`
  existing; check `Order.status` instead, and flag to the user if a task
  depends on payment actually being processed.
- **Pickup timeslots are currently hardcoded** stub data in the checkout
  timeslots endpoint, not backed by a real scheduling model.
- Money fields are **inconsistently typed**: `ProductVariant.selling_price`/
  `tax_rate` correctly use `DecimalField`, but `OrderItem`/`OrderPayment`/
  `PaymentProviderTransaction` use `FloatField`. Match whatever the field
  you're touching already uses — don't silently "fix" this inconsistency as
  part of an unrelated task.

## Known gaps (don't be surprised by these; don't fix unless asked)

- `.env.example`'s Postgres variable names (`DB_*`) don't match what
  `config/settings/database/database.py` actually reads
  (`POSTGRESQL_DATABASE_*`).
- `SECRET_KEY` is hardcoded in `config/settings/system/secret_key.py`, not
  read from an env var.
- `README.md`/`REQUERIMIENTOS.md`/`documentation/database.dbml` describe an
  earlier, simpler design (catalog-only, a `Supplier`/price-history model)
  that was never fully implemented and has since been superseded by the
  actual code — don't treat them as ground truth for the current schema;
  the models in `accounts/`, `products/default/models/`, `inventory/models.py`,
  `orders/models.py`, `payment/models.py` are.

## Restrictions (apply to every change, not just one task)

- **Do not refactor heavily.** A feature request is not an invitation to clean
  up unrelated code or restructure files beyond what's needed.
- **Do not rename existing fields/functions/variables without explicit
  permission** — several apps (orders, inventory) have public API response
  shapes that the frontend depends on; a rename is a breaking change even if
  it looks like a typo fix (e.g. don't "fix" `employee_model`/`Customer_model`'s
  lowercase-class-name style).
- **Do not make changes that could break existing functionality.** There's no
  test suite in most apps (only `cart/tests/` has real tests) — be
  conservative, and verify manually (run the dev server, hit the actual
  endpoint) before calling a change done.
- **Migrations**: always generate one via `manage.py makemigrations` for any
  model change, and think about existing rows — e.g. a new required-looking
  field needs a sensible `default=` so existing rows don't break.
- **Reuse before duplicating.** If a new endpoint needs logic that already
  exists elsewhere (a permission check, a queryset annotation, a serializer),
  **extract it into one new shared file** that both the original view and the
  new code import from — don't copy-paste it a third time. Precedent from
  this session: `api/permissions.py::require_employee`,
  `orders/queries.py::annotate_order_totals`, and
  `inventory/queries.py::annotate_variant_stock` were all extracted out of
  views that had the logic inline, and those original views were updated to
  call the shared helper instead of keeping their own copy.
- Several thresholds are still hardcoded in places that arguably should be
  configurable (e.g. `inventory/views/admin/inventory_products_admin_view.py`
  has ~11 separate `10`/`50` low/medium-stock literals, and
  `api/views_dashboard.py` has its own `LOW_STOCK_THRESHOLD = 5`). If a task
  asks you to make one of these configurable, expect to touch every one of
  these call sites — don't assume changing one constant covers it.

## Frontend contract

The Next.js frontend calls this API through Route Handlers under
`frontend/app/api/v1/**/route.ts`, which proxy to whatever you build here
using the session cookie. When you add or change a response shape, check
whether a frontend Route Handler/type already assumes the old shape before
considering the change done.
