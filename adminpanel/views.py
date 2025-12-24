from django.shortcuts import render, get_object_or_404, redirect
from orders.models import Order, OrderItem
from products.models import Product, Category
from django.contrib.auth.models import User
from django.contrib import messages
from .decorators import admin_only

from django.db.models import Sum
from orders.models import Order
from django.utils.timezone import now
import calendar

def dashboard(request):
    total_users = User.objects.count()
    total_products = Product.objects.count()
    total_orders = Order.objects.count()
    total_returns = ReturnRequest.objects.count()

    total_revenue = Order.objects.aggregate(total=Sum('total_amount'))['total'] or 0

    # Create monthly graph data
    months = []
    sales_data = []
    orders_data = []

    for i in range(1, 13):
        month_name = calendar.month_abbr[i]
        months.append(month_name)

        monthly_orders = Order.objects.filter(created_at__month=i)
        orders_data.append(monthly_orders.count())
        sales_data.append(
            monthly_orders.aggregate(total=Sum('total_amount'))['total'] or 0
        )

    recent_orders = Order.objects.order_by('-id')[:5]

    return render(request, "adminpanel/dashboard.html", {
        "total_users": total_users,
        "total_products": total_products,
        "total_orders": total_orders,
        "total_returns": total_returns,
        "total_revenue": total_revenue,
        "months": months,
        "sales_data": sales_data,
        "orders_data": orders_data,
        "recent_orders": recent_orders,
    })


# ========== ORDERS ==========
@admin_only
def order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    return render(request, 'adminpanel/order_list.html', {'orders': orders})

@admin_only
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'adminpanel/order_detail.html', {'order': order})

@admin_only
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        new_status = request.POST.get("status")

        # Debug print
        print("Received status:", new_status)

        if new_status in ["pending", "processing", "shipped", "delivered", "cancelled"]:
            order.status = new_status
            order.save()

        return redirect("adminpanel:order_detail", order_id=order.id)

    return render(request, "adminpanel/update_order_status.html", {"order": order})



# ========== PRODUCTS ==========
@admin_only
def product_list(request):
    products = Product.objects.all()
    return render(request, 'adminpanel/product_list.html', {'products': products})

@admin_only
def product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        product.name = request.POST.get("name")
        product.price = request.POST.get("price")
        product.stock = request.POST.get("stock")
        product.available = 'available' in request.POST

        if 'image' in request.FILES:
            product.image = request.FILES['image']

        product.save()
        return redirect('adminpanel:product_list')

    return render(request, 'adminpanel/product_edit.html', {"product": product})


# ========== USERS ==========
@admin_only
def user_list(request):
    users = User.objects.all()
    return render(request, 'adminpanel/user_list.html', {'users': users})
@admin_only
def product_add(request):
    categories = Category.objects.all()

    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        stock = request.POST.get("stock")
        category_id = request.POST.get("category")
        image = request.FILES.get("image")

        category = Category.objects.get(id=category_id)

        Product.objects.create(
            name=name,
            price=price,
            stock=stock,
            category=category,
            image=image,
            available=True
        )

        messages.success(request, "Product added successfully!")
        return redirect("adminpanel:product_list")

    return render(request, "adminpanel/product_add.html", {"categories": categories})
@admin_only
def product_delete(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product.delete()
    messages.success(request, "Product deleted successfully!")
    return redirect("adminpanel:product_list")
from orders.models import ReturnRequest

@admin_only
def return_requests(request):
    requests = ReturnRequest.objects.all().order_by("-created_at")
    return render(request, "adminpanel/return_requests.html", {"requests": requests})


@admin_only
def manage_return(request, request_id):
    req = get_object_or_404(ReturnRequest, id=request_id)

    if request.method == "POST":
        status = request.POST.get("status")

        if not status:
            messages.error(request, "Status cannot be empty.")
            return redirect('adminpanel:manage_return', request_id=req.id)

        req.status = status
        req.admin_response = request.POST.get("response", "")
        req.save()

        # RESTORE STOCK IF REFUNDED
        if status == "refunded":
            product = req.item.product
            product.stock += req.item.quantity
            product.save()

        messages.success(request, f"Return updated to: {req.get_status_display()}")
        return redirect('adminpanel:return_requests')

    return render(request, "adminpanel/manage_return.html", {"req": req})
