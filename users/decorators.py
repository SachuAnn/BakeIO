from django.shortcuts import redirect
from django.contrib import messages

def bakery_required(view_func):
    def wrapper(request, *args, **kwargs):

        # Not logged in
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in first')
            return redirect('login')

        # Logged in but not bakery
        if request.user.role != 'bakery':
            messages.error(request, 'Bakery access only')
            return redirect('login')

        return view_func(request, *args, **kwargs)

    return wrapper
def delivery_required(view_func):
    def wrapper(request, *args, **kwargs):

        if not request.user.is_authenticated:
            messages.error(request, 'Please log in first')
            return redirect('login')

        if request.user.role != 'delivery':
            messages.error(request, 'Delivery access only')
            return redirect('login')

        return view_func(request, *args, **kwargs)

    return wrapper



def admin_required(view_func):
    def wrapper(request, *args, **kwargs):

        # 1️⃣ Not logged in
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in first')
            return redirect('login')

        # 2️⃣ Logged in but not admin
        if request.user.role != 'admin':
            messages.error(request, 'Admin access only')
            return redirect('login')

        return view_func(request, *args, **kwargs)

    return wrapper
