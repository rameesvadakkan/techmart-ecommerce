from django.urls import path
from . import views

app_name = "adminpanel"

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Orders
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('orders/<int:order_id>/update/', views.update_order_status, name='update_order_status'),

    # Products
    path('products/add/', views.product_add, name='product_add'),
    path('products/<int:product_id>/delete/', views.product_delete, name='product_delete'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:product_id>/edit/', views.product_edit, name='product_edit'),

    # Users
    path('users/', views.user_list, name='user_list'),
    path("returns/", views.return_requests, name="admin_return_requests"),
    path("returns/<int:request_id>/", views.manage_return, name="admin_manage_return"),
    path("returns/", views.return_requests, name="admin_return_requests"),
    path("returns/<int:request_id>/", views.manage_return, name="manage_return"),
    path('returns/', views.return_requests, name='return_requests'),

    
    
    
]
