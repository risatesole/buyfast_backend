from ..models import User
from ..enums import AccountRole

def create_account(first_name, last_name, email, password, role, status):
    valid_roles = [r.value for r in AccountRole]

    if role not in valid_roles:
        raise ValueError(
            f"Invalid role '{role}'. Allowed roles: {', '.join(valid_roles)}"
        )

    user = User.objects.create_user(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password,
        role=role,
        status="active"
    )

    return user