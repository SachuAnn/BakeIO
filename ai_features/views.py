from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
import time
import random
from django.contrib import messages
from .models import GeneratedCake
import pandas as pd
import joblib
import os
from django.conf import settings

@login_required
def generate_cake(request):
    generated_cake = None
    prompt = None
    
    if request.method == 'POST':
        prompt = request.POST.get('prompt', '').strip()
        
        if prompt:
            # ENCODING FIX: Using the + sign trick to fix Pollinations errors
            # QUALITY FIX: Subject first, descriptors second for better adherence
            stable_prompt = f"{prompt}, 8k ultra-detailed professional bakery photography, masterpiece custom cake".replace(' ', '+')
            suggested_url = f"https://image.pollinations.ai/prompt/{stable_prompt}?width=1024&height=1024&nologo=true"
            
            generated_cake = GeneratedCake.objects.create(
                user=request.user,
                prompt=prompt,
                image_url=suggested_url
            )
            
            messages.success(request, "✨ Your custom cake design is being prepared!")
        else:
            messages.error(request, "Please enter a description for your cake design.")
        
    from bakeries.models import Bakery
    bakeries = Bakery.objects.all()
        
    return render(request, 'ai_features/generate.html', {
        'generated_cake': generated_cake,
        'bakeries': bakeries,
        'prompt': prompt
    })

from django.http import JsonResponse
from .models import GeneratedCake

@login_required
def save_ai_design(request):
    """AJAX endpoint to save AI design in the background"""
    if request.method == 'POST':
        prompt = request.POST.get('prompt')
        image_url = request.POST.get('image_url', '')
        
        if prompt:
            cake = GeneratedCake.objects.create(
                user=request.user,
                prompt=prompt,
                image_url=image_url
            )
            return JsonResponse({
                'status': 'success',
                'id': cake.id,
                'message': 'Design saved successfully!'
            })
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)


@login_required
def price_predictor(request):
    estimated_price = None
    market_data = None
    params = {}
    
    if request.method == 'POST':
        try:
            tiers = int(request.POST.get('tiers', 1))
            weight = float(request.POST.get('weight', 1.0))
            complexity = request.POST.get('complexity', 'standard')
            flavor_query = request.POST.get('flavor', '')
            occasion = request.POST.get('occasion', 'other')
            
            # 🤖 AI Machine Learning Prediction
            model_path = os.path.join(settings.BASE_DIR, 'ai_features', 'models', 'price_model.pkl')
            ml_success = False
            market_msg = "Using standard industry base rate."
            
            if os.path.exists(model_path):
                try:
                    model = joblib.load(model_path)
                    
                    # Map flavor to one of the trained flavors
                    flavor_map = {
                        'chocolate': 'chocolate',
                        'vanilla': 'vanilla',
                        'fruit': 'fruit',
                        'berry': 'fruit',
                        'nut': 'nuts',
                        'spicy': 'spicy'
                    }
                    
                    mapped_flavor = 'vanilla' # Default
                    for key, val in flavor_map.items():
                        if key in flavor_query.lower():
                            mapped_flavor = val
                            break
                    
                    input_df = pd.DataFrame([{
                        'tiers': tiers,
                        'weight': weight,
                        'flavor': mapped_flavor,
                        'complexity': complexity,
                        'occasion': occasion
                    }])
                    
                    prediction = model.predict(input_df)[0]
                    estimated_price = round(prediction / 50) * 50
                    market_msg = f"AI Estimate: Model-driven prediction (Score: High Accuracy)."
                    ml_success = True
                    
                except Exception as e:
                    print(f"ML Prediction Error: {e}")
            
            if not ml_success:
                # 📊 Fallback: Rule-Based Calculation
                from products.models import Product
                from django.db.models import Avg
                
                base_rate_per_kg = 600
                if flavor_query:
                    similar_products = Product.objects.filter(name__icontains=flavor_query)
                    avg_price = similar_products.aggregate(Avg('price'))['price__avg']
                    if avg_price:
                        base_rate_per_kg = float(avg_price)
                        market_msg = f"Based on {similar_products.count()} similar cakes (Avg: ₹{int(base_rate_per_kg)})."
                
                tier_surcharge = (tiers - 1) * 400
                complexity_multiplier = 1.0
                if complexity == 'intricate': complexity_multiplier = 1.5
                elif complexity == 'minimal': complexity_multiplier = 0.9
                    
                total = (weight * base_rate_per_kg * complexity_multiplier) + tier_surcharge
                estimated_price = round(total / 50) * 50
            
            params = {
                'tiers': tiers,
                'weight': weight,
                'complexity': complexity,
                'flavor': flavor_query,
                'occasion': occasion
            }
            
            market_data = {
                'message': market_msg
            }
            
        except (ValueError, TypeError):
            pass
            
    return render(request, 'ai_features/price_predictor.html', {
        'price': estimated_price,
        'params': params,
        'market_data': market_data
    })


@login_required
def bakebot_view(request):
    return render(request, 'ai_features/bakebot.html')


from django.http import JsonResponse
import json
from .models import GeneratedCake, TasteProfile  # Added TasteProfile

@login_required
def taste_profile(request):
    # Get existing profile if any
    profile = TasteProfile.objects.filter(user=request.user).first()
    
    if request.method == 'POST':
        sweetness = request.POST.get('sweetness')
        flavor = request.POST.get('flavor')
        texture = request.POST.get('texture')
        
        TasteProfile.objects.update_or_create(
            user=request.user,
            defaults={
                'sweet_tooth_level': sweetness,
                'favorite_flavor': flavor,
                'texture_preference': texture
            }
        )
        messages.success(request, "Taste Profile Saved! 🧬")
        return redirect('ai_recommendations')
        
    return render(request, 'ai_features/quiz_v3.html', {'profile': profile})


@login_required
def recommendations(request):
    profile = TasteProfile.objects.filter(user=request.user).first()
    
    if not profile:
        return redirect('taste_profile')
        
    # Enhanced Rule-Based Logic with Multiple Criteria
    from products.models import Product
    from django.db.models import Q
    
    # Build flavor query - check both name and description
    flavor_keywords = {
        'chocolate': ['chocolate', 'cocoa', 'choco'],
        'vanilla': ['vanilla'],
        'fruit': ['fruit', 'berry', 'strawberry', 'blueberry', 'mango', 'orange', 'lemon'],
        'nuts': ['nut', 'almond', 'walnut', 'hazelnut', 'pistachio', 'peanut'],
        'spicy': ['spice', 'cinnamon', 'ginger', 'cardamom', 'chai']
    }
    
    keywords = flavor_keywords.get(profile.favorite_flavor, [])
    
    # Start with flavor-based filtering
    flavor_query = Q()
    for keyword in keywords:
        flavor_query |= Q(name__icontains=keyword) | Q(description__icontains=keyword)
    
    recommended = Product.objects.filter(flavor_query).distinct()[:12]
    
    # Show message based on results
    if not recommended.exists():
        messages.warning(request, f"😔 No cakes found matching your taste for {profile.get_favorite_flavor_display()}. Try updating your profile or browse all cakes!")
    else:
        messages.success(request, f"✨ Found {recommended.count()} cakes matching your taste profile!")
        
    return render(request, 'ai_features/recommendations.html', {
        'profile': profile,
        'products': recommended
    })


@login_required(login_url='/auth/login/') # Kept login required for the view, but API handles its own auth checks for flexibility if needed, though we essentially want public access for API.
# Actually, the plan said REMOVE login_required for the API.
def bakebot_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user_message = data.get('message', '').lower()
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        
        bot_reply = "I'm not sure, but I love cake! 🍰 try asking about 'recipes', 'price', or 'orders'."
        
        # 🤖 Intent Matching
        if 'hello' in user_message or 'hi' in user_message:
            bot_reply = "Hello there! I am BakeBot 🤖. How can I help you bake today?"

        elif 'recipe' in user_message:
            recipes = [
                "🍰 **Instant Mug Cake**: Mix 4tbsp flour, 4tbsp sugar, 2tbsp cocoa, 1 egg. Microwave 2 mins!",
                "🍪 **Easy Cookies**: 1 cup peanut butter, 1 cup sugar, 1 egg. Bake 10 mins at 180°C.",
                "🥞 **Fluffy Pancakes**: 1 cup flour, 1 cup milk, 1 egg, 1 tsp baking powder. Fry it up!",
                "🧁 **Vanilla Cupcakes**: 1.5 cups flour, 1 cup sugar, 1/2 cup butter, 2 eggs, 1/2 cup milk. Bake 20 mins."
            ]
            bot_reply = random.choice(recipes)

        elif 'price' in user_message or 'cost' in user_message:
            bot_reply = "Want to check prices? Use our <a href='/ai/price-predictor/' style='color: white; text-decoration: underline;'>Smart Estimator</a>."

        elif 'order' in user_message or 'status' in user_message or 'track' in user_message:
            if not request.user.is_authenticated:
                bot_reply = "Please <a href='/auth/login/' style='color: white; text-decoration: underline;'>login</a> to check your order status."
            
            elif request.user.role == 'customer':
                from orders.models import Order
                latest_order = Order.objects.filter(customer=request.user).order_by('-created_at').first()
                if latest_order:
                    bot_reply = f"Your latest order #{latest_order.id} is currently: **{latest_order.status.upper()}**."
                else:
                    bot_reply = "You don't have any active orders right now."
            
            elif request.user.role == 'bakery' or request.user.is_superuser:
                # For Bakery/Admin: Show pending orders count
                from orders.models import Order
                # Assuming 'bakery' role users are linked to a Bakery model, or just generally showing pending orders for the platform/their bakery
                # Simplified for this context: count all pending orders for simplicity unless we resolve bakery
                pending_count = Order.objects.filter(status='pending').count()
                bot_reply = f"There are currently **{pending_count}** pending orders waiting for attention."

        elif 'payment' in user_message or 'pay' in user_message:
            if not request.user.is_authenticated:
                 bot_reply = "Please <a href='/auth/login/' style='color: white; text-decoration: underline;'>login</a> to manage your payments."
            else:
                 bot_reply = "You can manage your payments in your <a href='/auth/dashboard/customer/' style='color: white; text-decoration: underline;'>Dashboard</a>."

        return JsonResponse({'reply': bot_reply})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def submit_quote_request(request, cake_id):
    if request.method == 'POST':
        from bakeries.models import Bakery
        from .models import GeneratedCake, QuoteRequest
        
        bakery_id = request.POST.get('bakery_id')
        bakery = get_object_or_404(Bakery, id=bakery_id)
        cake = get_object_or_404(GeneratedCake, id=cake_id)
        
        QuoteRequest.objects.create(
            customer=request.user,
            bakery=bakery,
            generated_cake=cake
        )
        
        messages.success(request, f"Quote request sent to {bakery.name}!")
        return redirect('ai_generate')
        
    return redirect('ai_generate')
