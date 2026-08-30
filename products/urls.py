# products/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('cakes/', views.cake_list, name='cake_list'),
    path('cakes/<int:product_id>/', views.cake_detail, name='cake_detail'),
    path('review/<int:product_id>/', views.add_review, name='add_review'),
]
