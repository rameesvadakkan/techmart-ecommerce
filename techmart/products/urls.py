from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),

    # SEARCH FIRST
    path('search/', views.search, name='search'),

    # CATEGORY FILTER
    path('category/<slug:category_slug>/', views.product_list, name='product_list_by_category'),

    # ADD RATING
    path('<slug:slug>/rate/', views.add_rating, name='add_rating'),

    # PRODUCT DETAIL — ALWAYS LAST
    path('<slug:slug>/', views.product_detail, name='product_detail'),
]
