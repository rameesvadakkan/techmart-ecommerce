from django.shortcuts import render, redirect
from .models import Coupon
from .forms import ApplyCouponForm
from django.contrib import messages
from datetime import date

def apply_coupon(request):
    from cart.cart import Cart  # import here to avoid circular error
    cart = Cart(request)

    if request.method == "POST":
        form = ApplyCouponForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["code"].upper()
            
            try:
                coupon = Coupon.objects.get(code=code)
            except Coupon.DoesNotExist:
                messages.error(request, "Invalid Coupon Code")
                return redirect("cart_detail")

            if not coupon.is_valid():
                messages.error(request, "Coupon expired or inactive")
                return redirect("cart_detail")

            if cart.get_total_price() < coupon.min_amount:
                messages.error(request, f"Minimum amount ₹{coupon.min_amount} required")
                return redirect("cart_detail")

            # Save coupon in session
            request.session['coupon_id'] = coupon.id
            messages.success(request, f"Coupon '{code}' applied successfully!")
            return redirect("cart_detail")

    return redirect("cart_detail")
from django.shortcuts import render

# Create your views here.
