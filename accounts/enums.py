from enum import Enum

class AccountRole(Enum):
    """Abstraction to avialable roles"""
    CUSTOMER = "customer"
    EMPLOYEE = "employee"

class AccountStatus(Enum):
    """Abstraction to avialable roles"""
    ACTIVE = "active"
    DEACTIVATED = "deactivated"
    DELETED = "deleted"
