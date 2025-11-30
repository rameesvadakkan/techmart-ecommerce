from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login 
from .models import Address
from .forms import AddressForm
from django.contrib import messages 
from .models import Profile

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)   # Auto login after register
            return redirect('home')
    else:
        form = UserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})

@login_required
def address_list(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'accounts/address_list.html', {'addresses': addresses})

@login_required
def add_address(request):
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user

            # Set first address as default
            if not Address.objects.filter(user=request.user).exists():
                address.is_default = True

            address.save()
            return redirect('address_list')
    else:
        form = AddressForm()

    return render(request, 'accounts/address_form.html', {'form': form})


@login_required
def edit_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)

    if request.method == "POST":
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect('address_list')
    else:
        form = AddressForm(instance=address)

    return render(request, 'accounts/address_form.html', {'form': form})


@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    return redirect('address_list')


@login_required
def set_default_address(request, address_id):
    Address.objects.filter(user=request.user).update(is_default=False)
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.is_default = True
    address.save()
    return redirect('address_list')


from accounts.forms import ProfileForm, UserForm

@login_required
def edit_profile(request):
    user = request.user

    # FIX: Create profile if missing
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == "POST":
        user.first_name = request.POST.get("first_name")
        user.last_name = request.POST.get("last_name")
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
