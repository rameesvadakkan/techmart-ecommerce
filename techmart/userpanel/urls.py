from django.urls import path
from . import views

app_name = "userpanel"

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('addresses/', views.address_list, name='addresses'),
    path('orders/', views.order_list, name='orders'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('returns/', views.returns, name='returns'),
    path('edit-profile/', views.edit_profile, name="edit_profile"),
]
