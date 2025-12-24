from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.models import Address
from orders.models import Order, ReturnRequest
from wishlist.models import Wishlist
from accounts.models import Profile
from django.contrib import messages

@login_required
def dashboard(request):
    return render(request, "userpanel/dashboard.html")


@login_required
def profile(request):
    return render(request, "userpanel/profile.html")


@login_required
def address_list(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, "userpanel/addresses.html", {"addresses": addresses})


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "userpanel/orders.html", {"orders": orders})


@login_required
def wishlist(request):
    items = Wishlist.objects.filter(user=request.user)
    return render(request, "userpanel/wishlist.html", {"items": items})


@login_required
def returns(request):
    requests = ReturnRequest.objects.filter(user=request.user)
    return render(request, "userpanel/returns.html", {"requests": requests})

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.forms import ProfileForm, UserForm

@login_required
def edit_profile(request):
    user = request.user

    # FIX: Create profile if missing
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == "POST":
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name") or " "
        user.email = request.POST.get("email")
        user.save()

        profile.phone = request.POST.get("phone")

        if "profile_image" in request.FILES:
            profile.profile_image = request.FILES["profile_image"]

        profile.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("userpanel:edit_profile")

    return render(request, "userpanel/edit_profile.html", {
        "user": user,
        "profile": profile
    })

