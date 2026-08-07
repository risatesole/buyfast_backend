def serialize_profile(user):
    employee = getattr(user, "employee_profile", None)
    if not employee or not employee.profile:
        return None
    return {
        "id": employee.profile.id,
        "name": employee.profile.name,
        "permissions": employee.profile.permissions,
    }
