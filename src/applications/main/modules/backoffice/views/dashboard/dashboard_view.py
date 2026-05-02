from ..contexts.backoffice_context_handler import backoffice_view_context_handler
from django.contrib.auth.decorators import login_required, user_passes_test
from ....auth.is_employee_challenge import is_employee_challenge
from django.shortcuts import render

@login_required
@user_passes_test(is_employee_challenge)
def backoffice_dashboard_view(request):
    """HANDLE POST ACTIONS"""
    return render(request, "backoffice/page.html", backoffice_view_context_handler())
