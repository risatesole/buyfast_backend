Repository: UASD Económato — Backend

Source of truth
- The canonical, authoritative repository guidance is in [CLAUDE.md](CLAUDE.md).
- Do NOT modify `CLAUDE.md`. Keep these Copilot instructions synchronized with it.

High-level intent
- This repository provides the Django/DRF backend API for the UASD Económato storefront. The frontend talks to this API under `/api/v1/`.
- All code (models, views, variables, comments) is in English. User-facing strings should be Spanish for end users.

What to follow (key rules)
- Tech stack: Django 6, Django REST Framework, `drf-spectacular`, Python ≥3.12, managed with `uv`.
- Auth: session-cookie based, not JWT. Use the existing `api/utils.py::CsrfExemptSessionAuthentication` for CSRF-free session endpoints called cross-origin.
- Use `api/permissions.py::require_employee(request)` for employee-only endpoints; do not duplicate role checks inline.

Project structure and conventions
- `config/settings/` uses one small file per concern; change those files rather than adding new blobs to a catch-all settings file.
- `api/urls.py` is the single source of truth for URL routing; add new endpoints by adding views in the domain app and wiring them in `api/urls.py`.
- `products/default` follows a DDD-ish layout; other apps use a simpler `usecases/` function style — follow the app's existing style.

Domain model notes
- Inventory is ledger-based (use `inventory/queries.py::annotate_variant_stock(queryset)` to get `total_quantity`).
- Use `orders/queries.py::annotate_order_totals(queryset)` for order annotations.
- Payments are not wired up — do not assume `OrderPayment` rows indicate real payment processing; check `Order.status` instead.

Restrictions and safety
- Do not refactor heavily or rename fields/functions without explicit permission — response shapes may be consumed by the frontend.
- Generate migrations with `manage.py makemigrations` for model changes and provide sensible `default=` values when adding required fields to avoid breaking existing rows.
- Be conservative: most apps have no tests — verify manually where needed.

Reuse and helpers
- Prefer existing shared helpers (permissions, query annotations, serializers). If a new shared helper is required, extract it into one shared module and update callers.

Developer notes for Copilot
- Consult [CLAUDE.md](CLAUDE.md) for authoritative guidance; reflect any CLAUDE.md constraints in suggested code.
- When suggesting changes that impact cross-repo contracts (frontend types or route shapes), clearly state the impact and mention where to update frontend route handler types.

If you need clarification
- Ask the user before adding new packages, renaming fields, or making breaking API changes.

Maintainers: keep these instructions in sync with [CLAUDE.md](CLAUDE.md).
