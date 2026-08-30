from django.urls import path
from . import views

urlpatterns = [

    path('price-predictor/', views.price_predictor, name='price_predictor'),
    path('quiz/', views.taste_profile, name='taste_profile'),
    path('recommendations/', views.recommendations, name='ai_recommendations'),
    path('generate/', views.generate_cake, name='ai_generate'),
    path('generate/save/', views.save_ai_design, name='save_ai_design'),
    path('generate/quote/<int:cake_id>/', views.submit_quote_request, name='submit_quote_request'),
    path('bakebot/api/', views.bakebot_api, name='bakebot_api'),
]
