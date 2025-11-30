from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('success/<int:order_id>/', views.order_success, name='order_success'),
    path('my-orders/', views.order_list, name='order_list'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('place-order/', views.place_order, name='place_order'),
    path('order-summary/<int:address_id>/<str:payment_method>/', views.order_summary, name='order_summary'),
    path('track/<int:order_id>/', views.track_order, name='track_order'),
    path("invoice/<int:order_id>/", views.download_invoice, name="download_invoice"),
    path("create_razorpay_order/", views.create_razorpay_order, name="create_razorpay_order"),
    path('return/<int:item_id>/', views.request_return, name='request_return'),


    
]
