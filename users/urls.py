from django.urls import path
from . import views
from .views import update_order_status
from delivery.views import update_delivery_status   # 👈 ADD THIS


urlpatterns = [

    # =====================================================
    # AUTH
    # =====================================================
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),

    # =====================================================
    # DASHBOARDS
    # =====================================================
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),
    path('dashboard/delivery/', views.delivery_dashboard, name='delivery_dashboard'),
    path('api/update_location/', views.update_location, name='update_location'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/bakery/', views.bakery_dashboard, name='bakery_dashboard'),

    # =====================================================
    # ADMIN
    # =====================================================
    path('admin/users/', views.admin_view_users, name='admin_view_users'),
    path('admin/users/toggle/<int:user_id>/', views.toggle_user_status, name='toggle_user_status'),

    path('admin/delivery/', views.manage_delivery, name='manage_delivery'),
    path('admin/delivery/add/', views.add_delivery, name='add_delivery'),
    path('admin/delivery/toggle/<int:user_id>/', views.toggle_delivery, name='toggle_delivery'),
    path('admin/delivery/delete/<int:user_id>/', views.delete_delivery, name='delete_delivery'),

    path('admin/bakeries/', views.manage_bakeries, name='manage_bakeries'),
    path('admin/bakeries/toggle/<int:bakery_id>/', views.toggle_bakery_status, name='toggle_bakery_status'),
    path('admin/orders/', views.admin_orders, name='admin_orders'),
    path('admin/payments/', views.admin_payments, name='admin_payments'),

    # =====================================================
    # BAKERY PROFILE
    # =====================================================
    path('bakery/profile/', views.bakery_profile, name='bakery_profile'),

    # =====================================================
    # BAKERY PRODUCTS
    # =====================================================
    path('bakery/products/', views.manage_products, name='manage_products'),
    path('bakery/products/add/', views.add_product, name='add_product'),
    path('bakery/products/edit/<int:id>/', views.edit_product, name='edit_product'),
    path('bakery/products/delete/<int:id>/', views.delete_product, name='delete_product'),

    # =====================================================
    # BAKERY OFFERS
    # =====================================================
    path('bakery/offers/', views.manage_offers, name='manage_offers'),
    path('bakery/offers/add/', views.add_offer, name='add_offer'),
    path('bakery/offers/toggle/<int:offer_id>/', views.toggle_offer, name='toggle_offer'),

    # =====================================================
    # BAKERY ORDERS
    # =====================================================
    path('bakery/orders/', views.bakery_orders, name='bakery_orders'),
    path(
        'bakery/orders/update/<int:order_id>/',
        update_order_status,
        name='update_order_status'
    ),

    path('bakery/analytics/', views.bakery_analytics, name='bakery_analytics'),

    # =====================================================
    # DELIVERY (🔥 FIXED)
    # =====================================================
    path(
        'delivery/update-status/<int:order_id>/',
        update_delivery_status,
        name='delivery_update_status'
    ),
]
