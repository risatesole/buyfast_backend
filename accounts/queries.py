# accounts/queries.py
from django.db.models import Count, Q

EMPLOYEE_SORT_FIELDS = {
    "name": "last_name",
    "email": "email",
    "hired_at": "employee_profile__hired_at",
    "position": "employee_profile__position",
}

CUSTOMER_SORT_FIELDS = {
    "name": "last_name",
    "email": "email",
    "created_at": "created_at",
    "purchases": "purchase_count",
}


def annotate_customer_purchase_count(queryset):
    """
    Adds a computed `purchase_count` field to a customer User queryset: the
    number of distinct orders placed by that customer.

    Shared by the admin customers report view and any future admin customer
    list view so both count purchases the exact same way.
    """
    return queryset.annotate(purchase_count=Count("orders", distinct=True))


def apply_admin_employees_filters(queryset, request):
    """
    Applies search/position/profile/hired-date filters and sort order to an
    employee User queryset (expects the queryset to already be scoped to
    role="employee" with employee_profile selected).
    """
    search = request.query_params.get("search", "").strip()
    if search:
        queryset = queryset.filter(
            Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(email__icontains=search)
        )

    position = request.query_params.get("position", "").strip()
    if position:
        queryset = queryset.filter(employee_profile__position=position)

    profile_id = request.query_params.get("profile", "").strip()
    if profile_id:
        try:
            queryset = queryset.filter(employee_profile__profile_id=int(profile_id))
        except ValueError:
            pass

    date_from = request.query_params.get("date_from", "").strip()
    if date_from:
        queryset = queryset.filter(employee_profile__hired_at__date__gte=date_from)

    date_to = request.query_params.get("date_to", "").strip()
    if date_to:
        queryset = queryset.filter(employee_profile__hired_at__date__lte=date_to)

    sort_param = request.query_params.get("sort", "-hired_at").strip()
    descending = sort_param.startswith("-")
    sort_key = sort_param.lstrip("-")
    db_field = EMPLOYEE_SORT_FIELDS.get(sort_key)

    if db_field:
        queryset = queryset.order_by(f"-{db_field}" if descending else db_field)
    else:
        queryset = queryset.order_by("-employee_profile__hired_at")

    return queryset


def apply_admin_customers_filters(queryset, request):
    """
    Applies search/institution-member/signup-date/purchase-count filters and
    sort order to a customer User queryset (expects
    annotate_customer_purchase_count to have already been applied for the
    purchases filter/sort, and the queryset to already be scoped to
    role="customer").
    """
    search = request.query_params.get("search", "").strip()
    if search:
        queryset = queryset.filter(
            Q(first_name__icontains=search)
            | Q(last_name__icontains=search)
            | Q(email__icontains=search)
        )

    institution_member = request.query_params.get("institution_member", "").strip()
    if institution_member:
        queryset = queryset.filter(institution_member=institution_member.lower() == "true")

    date_from = request.query_params.get("date_from", "").strip()
    if date_from:
        queryset = queryset.filter(created_at__date__gte=date_from)

    date_to = request.query_params.get("date_to", "").strip()
    if date_to:
        queryset = queryset.filter(created_at__date__lte=date_to)

    min_purchases = request.query_params.get("min_purchases", "").strip()
    if min_purchases:
        try:
            queryset = queryset.filter(purchase_count__gte=int(min_purchases))
        except ValueError:
            pass

    max_purchases = request.query_params.get("max_purchases", "").strip()
    if max_purchases:
        try:
            queryset = queryset.filter(purchase_count__lte=int(max_purchases))
        except ValueError:
            pass

    sort_param = request.query_params.get("sort", "-created_at").strip()
    descending = sort_param.startswith("-")
    sort_key = sort_param.lstrip("-")
    db_field = CUSTOMER_SORT_FIELDS.get(sort_key)

    if db_field:
        queryset = queryset.order_by(f"-{db_field}" if descending else db_field)
    else:
        queryset = queryset.order_by("-created_at")

    return queryset
