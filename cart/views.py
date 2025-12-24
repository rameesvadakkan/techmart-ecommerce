from django.shortcuts import render, redirect, get_object_or_404
from products.models import Product
from .cart import Cart
from django.contrib import messages

def cart_detail(request):
    cart = Cart(request)

    coupon_id = request.session.get("coupon_id")
    coupon = None
    discount = 0

    if coupon_id:
        try:
            coupon = Coupon.objects.get(id=coupon_id)
            discount = (coupon.discount / 100) * float(cart.get_total_price())
        except Coupon.DoesNotExist:
            coupon = None
            discount = 0

    final_total = cart.get_total_price() - discount

    return render(request, "cart/cart_detail.html", {
        "cart": cart,
        "coupon": coupon,
        "discount": discount,
        "final_total": final_total,
    })


def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.add(product)
    return redirect('cart_detail')

def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart_detail')

def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        action = request.POST.get('action')
        current_qty = int(request.POST.get('current_quantity'))

        if action == "increase":
            new_qty = current_qty + 1
        elif action == "decrease":
            new_qty = current_qty - 1
            if new_qty < 1:
                new_qty = 1
        else:
            new_qty = current_qty

        cart.cart[str(product_id)]['quantity'] = new_qty
        cart.save()

    return redirect('cart_detail')
from coupon.models import Coupon
from django.utils import timezone

def apply_coupon(request):
    code = request.POST.get("coupon_code")

    if not code:
        messages.error(request, "Please enter a coupon code.")
        return redirect("cart_detail")

    try:
        coupon = Coupon.objects.get(code__iexact=code, active=True)
    except Coupon.DoesNotExist:
        messages.error(request, "Invalid coupon code.")
        return redirect("cart_detail")

    # Check expiry
    if coupon.expiry_date and coupon.expiry_date < timezone.now().date():
        messages.error(request, "Coupon has expired.")
        return redirect("cart_detail")

    # Save coupon to session
    request.session["coupon_id"] = coupon.id
    messages.success(request, f"Coupon '{coupon.code}' applied successfully!")

    return redirect("cart_detail")
def remove_coupon(request):
    if "coupon_id" in request.session:
        del request.session["coupon_id"]
    messages.info(request, "Coupon removed.")
    return redirect("cart_detail")

