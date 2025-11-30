from django.shortcuts import redirect
from django.contrib import messages

def admin_only(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, "You must login as admin!")
            return redirect('login')

        if not request.user.is_staff:  # Only staff users allowed
            messages.error(request, "Access denied! Admins only.")
            return redirect('home')

        return view_func(request, *args, **kwargs)
    return wrapper
