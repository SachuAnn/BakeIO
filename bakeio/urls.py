from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('core.urls')),
    path('auth/', include('users.urls')),

    

    path('bakeries/', include('bakeries.urls')),
    path('products/', include('products.urls')),

    path('cart/', include('cart.urls')),
    path('cart/', include('cart.urls')),
    path('', include('orders.urls')),

    path('wishlist/', include('wishlist.urls')),
    path('explore/', include('explore.urls')),
    path('chat/', include('chat.urls')),
    path('notifications/', include('notifications.urls')),
    path('delivery/', include('delivery.urls')),
    path('auth/delivery/', include('delivery.urls')),
    path('ai/', include('ai_features.urls')),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
