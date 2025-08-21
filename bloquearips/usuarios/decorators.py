from django.shortcuts import redirect
from functools import wraps

# Decorator genérico para permitir apenas certos tipos
def allowed_roles(roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.tipo in roles:
                return view_func(request, *args, **kwargs)
            return redirect("home")
        return wrapper
    return decorator

# Decorators específicos
def admin_required(view_func):
    return allowed_roles(['admin'])(view_func)

def engredes_required(view_func):
    return allowed_roles(['admin', 'engredes'])(view_func)

def noc_required(view_func):
    return allowed_roles(['admin', 'engredes', 'noc'])(view_func)
