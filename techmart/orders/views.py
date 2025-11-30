from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from cart.cart import Cart
from .models import Order, OrderItem
from accounts.models import Address
from products.models import Product
from coupon.models import Coupon   # <-- if you have coupon app
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from django.http import JsonResponse

# --------------------------------------------------------------------
# CHECKOUT PAGE – Select Address + Payment Method
# --------------------------------------------------------------------
@login_required
def checkout(request):
    cart = Cart(request)
    saved_addresses = Address.objects.filter(user=request.user).order_by('-is_default')

    if request.method == "POST":

        # 🔥 STOCK CHECK
        for item in cart:
            if item['quantity'] > item['product'].stock:
                messages.error(request, f"{item['product'].name} does not have enough stock!")
                return redirect('cart_detail')

        # 🔥 ADDRESS SELECTION CHECK
        selected_address_id = request.POST.get("selected_address")
        if not selected_address_id:
            messages.error(request, "Please select a delivery address.")
            return redirect("checkout")

        payment_method = request.POST.get("payment_method")
        if not payment_method:
            messages.error(request, "Please select a payment method.")
            return redirect("checkout")

        # Redirect to order summary
        return redirect(
            "order_summary",
            address_id=selected_address_id,
            payment_method=payment_method
        )

    return render(request, "orders/checkout.html", {
        "cart": cart,
        "addresses": saved_addresses
    })


# --------------------------------------------------------------------
# ORDER SUMMARY BEFORE CONFIRMING
# --------------------------------------------------------------------
@login_required
def order_summary(request, address_id, payment_method):
    cart = Cart(request)
    address = get_object_or_404(Address, id=address_id, user=request.user)

    # 🔥 COUPON LOGIC
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

    return render(request, "orders/order_summary.html", {
        "cart": cart,
        "address": address,
        "payment_method": payment_method,
        "subtotal": cart.get_total_price(),
        "discount": discount,
        "final_total": final_total,
        "coupon": coupon,
    })


# --------------------------------------------------------------------
# PLACE ORDER – Final Submit
# --------------------------------------------------------------------
@login_required
def place_order(request):
    cart = Cart(request)

    if request.method != "POST":
        return redirect("checkout")

    address_id = request.POST.get("address_id")
    payment_method = request.POST.get("payment_method")

    # Fetch address
    address = get_object_or_404(Address, id=address_id, user=request.user)

    # 🔥 COUPON LOGIC AGAIN
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

    final_amount = cart.get_total_price() - discount

    # 🚀 CREATE ORDER
    order = Order.objects.create(
        user=request.user,
        full_name=address.full_name,
        phone=address.phone,
        address=address.address,
        city=address.city,
        pincode=address.pincode,
        payment_method=payment_method,
        coupon=coupon.code if coupon else "",
        discount_amount=discount,
        total_amount=final_amount,
        estimated_delivery=timezone.now().date() + timedelta(days=4)
    )

    # SAVE ITEMS + REDUCE STOCK
    for item in cart:
        OrderItem.objects.create(
            order=order,
            product=item["product"],
            price=item["price"],
            quantity=item["quantity"]
        )
        item["product"].stock -= item["quantity"]
        item["product"].save()

    cart.clear()

    # Remove coupon from session
    if "coupon_id" in request.session:
        del request.session["coupon_id"]

    return redirect("order_success", order_id=order.id)


# --------------------------------------------------------------------
# SUCCESS PAGE
# --------------------------------------------------------------------
@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_success.html', {'order': order})


# --------------------------------------------------------------------
# USER ORDER LIST
# --------------------------------------------------------------------
@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})


# --------------------------------------------------------------------
# ORDER DETAIL
# --------------------------------------------------------------------
@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = OrderItem.objects.filter(order=order)

    return render(request, 'orders/order_detail.html', {
        "order": order,
        "items": items,
    })
@login_required
def track_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    return render(request, "orders/track_order.html", {
        "order": order
    })
@login_required
def download_invoice(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = OrderItem.objects.filter(order=order)

    # Response for PDF file
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Invoice_{order.id}.pdf"'

    # Create PDF
    pdf = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    y = height - 40  # Starting height

    # -----------------------------
    # HEADER
    # -----------------------------
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(40, y, "TechMart - Invoice")
    y -= 30

    pdf.setFont("Helvetica", 12)
    pdf.drawString(40, y, f"Invoice ID: INV-{order.id}")
    y -= 20
    pdf.drawString(40, y, f"Date: {order.created_at.strftime('%d-%m-%Y')}")
    y -= 30

    # -----------------------------
    # CUSTOMER DETAILS
    # -----------------------------
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, y, "Billing Details")
    y -= 25

    pdf.setFont("Helvetica", 12)
    pdf.drawString(40, y, f"Name: {order.full_name}")
    y -= 20
    pdf.drawString(40, y, f"Phone: {order.phone}")
    y -= 20
    pdf.drawString(40, y, f"Address: {order.address}, {order.city} - {order.pincode}")
    y -= 30

    # -----------------------------
    # ORDER ITEMS
    # -----------------------------
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, y, "Order Items")
    y -= 25

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(40, y, "Product")
    pdf.drawString(260, y, "Qty")
    pdf.drawString(320, y, "Price")
    pdf.drawString(400, y, "Total")
    y -= 20

    pdf.setFont("Helvetica", 12)

    for item in items:
        if y < 100:  # new page if space ends
            pdf.showPage()
            y = height - 40

        pdf.drawString(40, y, item.product.name)
        pdf.drawString(260, y, str(item.quantity))
        pdf.drawString(320, y, f"₹{item.price}")
        pdf.drawString(400, y, f"₹{item.price * item.quantity}")
        y -= 20

    # -----------------------------
    # TOTAL AMOUNT
    # -----------------------------
    y -= 20
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(40, y, f"Grand Total: ₹{order.total_amount}")

    y -= 40
    pdf.setFont("Helvetica", 10)
    pdf.drawString(40, y, "Thank you for shopping with TechMart!")

    pdf.save()
    return response

import razorpay
from django.conf import settings

@login_required
def create_razorpay_order(request):
    if request.method == "POST":
        amount = int(float(request.POST.get("amount")) * 100)  # Convert to paise

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        # Create Razorpay Order
        razorpay_order = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": "1"
        })

        return JsonResponse({
            "order_id": razorpay_order["id"],
            "key": settings.RAZORPAY_KEY_ID,
            "amount": amount,
        })

    return JsonResponse({"error": "Invalid request"}, status=400)
from .models import ReturnRequest, OrderItem
from django.contrib.auth.decorators import login_required

@login_required
def request_return(request, item_id):
    item = get_object_or_404(OrderItem, id=item_id)
    # Check for existing return request
    existing = ReturnRequest.objects.filter(item=item).first()
    if existing and existing.status in ["approved", "refunded"]:
        messages.warning(request, "You have already submitted a return request for this item.")
        return redirect("order_detail", order_id=item.order.id)
    # Must be user's own order
    if item.order.user != request.user:
        messages.error(request, "Unauthorized access.")
        return redirect("order_list")

    # Allow only delivered orders
    if item.order.status != "delivered":
        messages.error(request, "You can request return only after delivery.")
        return redirect("order_detail", order_id=item.order.id)

    if request.method == "POST":
        reason = request.POST.get("reason")
        ReturnRequest.objects.create(
            order=item.order,
            item=item,
            user=request.user,
            reason=reason,
        )
        messages.success(request, "Return request submitted!")
        return redirect("order_detail", order_id=item.order.id)

    return render(request, "orders/request_return.html", {"item": item})
