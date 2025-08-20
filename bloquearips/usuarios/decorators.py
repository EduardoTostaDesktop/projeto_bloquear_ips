from django.shortcuts import redirect
from functools import wraps

def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.is_superuser or request.user.tipo == "admin"):
            return view_func(request, *args, **kwargs)
        return redirect("home")
    return wrapper

def engredes_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.tipo == "engredes":
            return view_func(request, *args, **kwargs)
        return redirect("home")
    return wrapper
