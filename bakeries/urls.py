from django.urls import path
from . import views

urlpatterns = [
    path('', views.bakery_list, name='bakery_list'),
    path('<int:id>/', views.bakery_detail, name='bakery_detail'),
]
