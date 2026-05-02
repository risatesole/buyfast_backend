def is_employee_challenge(user):
    return user.is_authenticated and user.role == "employee"
