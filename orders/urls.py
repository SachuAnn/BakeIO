from django.urls import path
from . import views
from .views import checkout

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/address/', views.checkout_address, name='checkout_address'),
    path('checkout/address/add/', views.add_address, name='add_address'),
    path('checkout/address/delete/<int:address_id>/', views.delete_address, name='delete_address'),
    path('checkout/payment/', views.checkout_payment, name='checkout_payment'),
    path('orders/', views.my_orders, name='my_orders'),
    path('orders/cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('orders/track/<int:order_id>/', views.track_order, name='track_order'),
    path('payments/', views.payment_history, name='payment_history'),
    path('invoice/<int:order_id>/', views.view_invoice, name='view_invoice'),
]
