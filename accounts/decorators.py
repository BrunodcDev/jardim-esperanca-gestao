from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def coordenadora_required(view_func):
    """Permite o acesso apenas a coordenadoras (ou superusuários)."""

    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_coordenadora:
            messages.error(request, "Acesso restrito à coordenação.")
            return redirect("dashboard")
        return view_func(request, *args, **kwargs)

    return _wrapped_view
