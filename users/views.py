from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .decorators import admin_required, bakery_required

from bakeries.models import Bakery
from products.models import Product, Offer, Review
from delivery.models import DeliveryAssignment
from orders.models import Order, Payment
from notifications.models import Notification
from notifications.utils import notify
from orders.services import assign_delivery

User = get_user_model()

# =====================================================
# DELIVERY DASHBOARD (SINGLE SOURCE OF TRUTH ✅)
# =====================================================
@login_required
def delivery_dashboard(request):
    if request.user.role != 'delivery':
        return redirect('login')

    # 🔒 NEVER filter on status or availability
    assignments = DeliveryAssignment.objects.filter(
        delivery_person_id=request.user.id
    ).select_related(
        'order', 'order__bakery', 'order__delivery_address'
    ).order_by('-assigned_at')

    notifications = Notification.objects.filter(
        user=request.user
    ).order_by('-created_at')[:30]

    unread_count = Notification.objects.filter(
        user=request.user,
        is_read=False
    ).count()

    return render(request, 'users/delivery_dashboard.html', {
        'assignments': assignments,
        'notifications': notifications,
        'unread_count': unread_count,
    })



# =====================================================
# BAKERY → UPDATE ORDER STATUS
# =====================================================
@login_required
def update_order_status(request, order_id):
    if request.method != 'POST':
        return redirect('bakery_orders')

    order = get_object_or_404(
        Order,
        id=order_id,
        bakery__owner=request.user
    )

    new_status = request.POST.get('status')
    order.status = new_status
    order.save()

    # 🔔 Notify customer based on status
    if new_status == 'preparing':
        notify(order.customer, f"Your order #{order.id} is now being prepared 🧁")

    elif new_status == 'ready':
        notify(order.customer, f"Your order #{order.id} is ready for pickup 🚴")

        # 🚴 Try assigning delivery automatically
        assign_delivery(order)

    return redirect('bakery_orders')


# =====================================================
# ADMIN
# =====================================================
@admin_required
def admin_payments(request):
    payments = Payment.objects.all().order_by('-created_at')
    return render(request, 'users/admin_payments.html', {'payments': payments})


@admin_required
def admin_orders(request):
    orders = Order.objects.select_related('customer', 'bakery').order_by('-created_at')
    return render(request, 'users/admin_orders.html', {'orders': orders})


@admin_required
def toggle_delivery(request, user_id):
    user = get_object_or_404(User, id=user_id, role='delivery')
    user.is_active = not user.is_active
    user.save()
    return redirect('manage_delivery')


@admin_required
def delete_delivery(request, user_id):
    user = get_object_or_404(User, id=user_id, role='delivery')
    user.delete()
    return redirect('manage_delivery')


@admin_required
def toggle_user_status(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if user != request.user:
        user.is_active = not user.is_active
        user.save()

    return redirect('admin_view_users')


@admin_required
def add_delivery(request):
    if request.method == 'POST':
        User.objects.create_user(
            username=request.POST['username'],
            password=request.POST['password'],
            email=request.POST.get('email', ''),
            role='delivery'
        )
        return redirect('manage_delivery')

    return render(request, 'users/add_delivery.html')


@admin_required
def manage_delivery(request):
    deliveries = User.objects.filter(role='delivery')
    return render(request, 'users/manage_delivery.html', {'deliveries': deliveries})


@admin_required
def admin_view_users(request):
    users = User.objects.all()
    return render(request, 'users/admin_view_users.html', {'users': users})


@admin_required
def manage_bakeries(request):
    bakeries = Bakery.objects.select_related('owner')
    return render(request, 'users/manage_bakeries.html', {'bakeries': bakeries})


@admin_required
def toggle_bakery_status(request, bakery_id):
    bakery = get_object_or_404(Bakery, id=bakery_id)
    bakery.is_active = not bakery.is_active
    bakery.save()
    
    status_text = "activated" if bakery.is_active else "deactivated"
    messages.success(request, f"{bakery.name} has been {status_text}")
    
    return redirect('manage_bakeries')



# =====================================================
# AUTH
# =====================================================
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        role = request.POST.get('role')

        user = authenticate(request, username=username, password=password)

        if not user:
            messages.error(request, "Invalid username or password")
            return redirect('login')

        if not user.is_active:
            messages.error(request, "Account is blocked")
            return redirect('login')

        if user.role != role:
            messages.error(request, "Role does not match this account")
            return redirect('login')

        login(request, user)
        return redirect(role_redirect(user))

    return render(request, 'users/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


def register(request):
    if request.method == 'POST':
        if User.objects.filter(username=request.POST['username']).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        User.objects.create_user(
            username=request.POST['username'],
            email=request.POST['email'],
            password=request.POST['password'],
            role=request.POST['role'],
            is_active=True
        )

        messages.success(request, "Account created successfully")
        return redirect('login')

    return render(request, 'users/register.html')


def role_redirect(user):
    return {
        'admin': '/auth/dashboard/admin/',
        'bakery': '/auth/dashboard/bakery/',
        'delivery': '/auth/dashboard/delivery/',
        'customer': '/auth/dashboard/customer/',
    }.get(user.role, '/')


# =====================================================
# DASHBOARDS
# =====================================================
@login_required
def bakery_dashboard(request):
    if request.user.role != 'bakery':
        return redirect('login')
    
    bakery = get_object_or_404(Bakery, owner=request.user)

    # Check for quote requests
    from ai_features.models import QuoteRequest
    try:
        quote_requests = QuoteRequest.objects.filter(bakery=bakery).order_by('-created_at')
    except:
        quote_requests = []
        
    # Fetch recent reviews for this bakery's products
    reviews = Review.objects.filter(product__bakery=bakery).order_by('-created_at')[:10]

    # Active delivery assignments to track riders
    from delivery.models import DeliveryAssignment
    active_assignments = DeliveryAssignment.objects.filter(
        order__bakery=bakery,
        status__in=['assigned', 'out_for_delivery']
    ).select_related('order', 'delivery_person')
        
    return render(request, 'users/bakery_dashboard.html', {
        'bakery': bakery,
        'quote_requests': quote_requests,
        'recent_reviews': reviews,
        'active_assignments': active_assignments
    })


@login_required
def customer_dashboard(request):
    if request.user.role != 'customer':
        return redirect('login')
    
    # 📈 TRENDING DELIGHTS: Calculate most frequently bought cakes
    # We aggregate based on OrderItem across all delivered/completed orders
    from django.db.models import Count
    from orders.models import OrderItem
    from products.models import Product
    
    trending_products = Product.objects.filter(
        orderitem__order__status__in=['delivered', 'completed']
    ).annotate(
        sales_count=Count('orderitem')
    ).order_by('-sales_count')[:4]

    all_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    unread_count = all_notifications.filter(is_read=False).count()
    notifications = all_notifications[:10]

    wishlisted_product_ids = []
    if request.user.is_authenticated:
        from wishlist.models import Wishlist
        wishlisted_product_ids = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)

    return render(request, 'users/customer_dashboard.html', {
        'trending_products': trending_products,
        'notifications': notifications,
        'unread_count': unread_count,
        'wishlisted_product_ids': wishlisted_product_ids
    })


@login_required
@admin_required
def admin_dashboard(request):
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    # Get real counts from database
    total_users = User.objects.count()
    total_bakeries = Bakery.objects.count()
    total_orders = Order.objects.count()
    
    # Get recent reviews for admin
    all_reviews = Review.objects.select_related('user', 'product').order_by('-created_at')[:20]
    
    context = {
        'total_users': total_users,
        'bakeries': Bakery.objects.all(),
        'orders': Order.objects.all(),
        'recent_reviews': all_reviews,
    }
    
    return render(request, 'users/admin_dashboard.html', context)


# =====================================================
# BAKERY PROFILE
# =====================================================
@login_required
def bakery_profile(request):
    if request.user.role != 'bakery':
        return redirect('login')

    bakery, _ = Bakery.objects.get_or_create(
        owner=request.user,
        defaults={'name': request.user.username}
    )

    if request.method == 'POST':
        bakery.name = request.POST.get('name')
        bakery.address = request.POST.get('address')
        if 'logo' in request.FILES:
            bakery.logo = request.FILES['logo']
        bakery.save()
        messages.success(request, "Profile updated")

    return render(request, 'bakery/bakery_profile.html', {'bakery': bakery})


# =====================================================
# PRODUCTS
# =====================================================
@login_required
def manage_products(request):
    if request.user.role != 'bakery':
        return redirect('login')

    bakery = get_object_or_404(Bakery, owner=request.user)
    products = Product.objects.filter(bakery=bakery)

    return render(request, 'bakery/manage_products.html', {'products': products})


@bakery_required
def add_product(request):
    bakery = get_object_or_404(Bakery, owner=request.user)

    if request.method == 'POST':
        offer_id = request.POST.get('offer')
        offer = Offer.objects.filter(id=offer_id, bakery=bakery).first() if offer_id else None
        
        Product.objects.create(
            bakery=bakery,
            name=request.POST['name'],
            price=request.POST['price'],
            description=request.POST.get('description', ''),
            image=request.FILES.get('image'),
            offer=offer
        )
        messages.success(request, "Product added")
        return redirect('manage_products')

    offers = Offer.objects.filter(bakery=bakery, is_active=True)
    return render(request, 'bakery/add_product.html', {'offers': offers})


@bakery_required
def edit_product(request, id):
    product = get_object_or_404(Product, id=id, bakery__owner=request.user)
    bakery = product.bakery

    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.price = request.POST.get('price')
        product.description = request.POST.get('description')
        
        offer_id = request.POST.get('offer')
        product.offer = Offer.objects.filter(id=offer_id, bakery=bakery).first() if offer_id else None

        if request.FILES.get('image'):
            product.image = request.FILES['image']

        product.save()
        messages.success(request, "Product updated")
        return redirect('manage_products')

    offers = Offer.objects.filter(bakery=bakery, is_active=True)
    return render(request, 'bakery/edit_product.html', {
        'product': product,
        'offers': offers
    })


@bakery_required
def delete_product(request, id):
    product = get_object_or_404(Product, id=id, bakery__owner=request.user)
    product.delete()
    return redirect('manage_products')


# =====================================================
# OFFERS
# =====================================================
@bakery_required
def manage_offers(request):
    bakery = get_object_or_404(Bakery, owner=request.user)
    offers = Offer.objects.filter(bakery=bakery)
    return render(request, 'bakery/manage_offers.html', {'offers': offers})


@bakery_required
def add_offer(request):
    bakery = get_object_or_404(Bakery, owner=request.user)

    if request.method == 'POST':
        Offer.objects.create(
            bakery=bakery,
            title=request.POST['title'],
            discount_percent=request.POST['discount_percent'],
            is_active=True
        )
        messages.success(request, "Offer added")
        return redirect('manage_offers')

    return render(request, 'bakery/add_offer.html')


@login_required
def toggle_offer(request, offer_id):
    if request.user.role != 'bakery':
        return redirect('login')

    offer = get_object_or_404(Offer, id=offer_id)
    offer.is_active = not offer.is_active
    offer.save()

    return redirect('manage_offers')


# =====================================================
# BAKERY ORDERS
# =====================================================
@login_required
def bakery_orders(request):
    if request.user.role != 'bakery':
        return redirect('login')

    bakery = get_object_or_404(Bakery, owner=request.user)

    orders = Order.objects.filter(
        bakery=bakery
    ).order_by('-created_at')

    return render(request, 'bakery/orders.html', {
        'bakery': bakery,
        'orders': orders
    })


@login_required
def bakery_analytics(request):
    if request.user.role != 'bakery':
        return redirect('login')

    from django.db.models import Sum, Count, Q
    from django.utils import timezone
    from datetime import timedelta
    
    bakery = get_object_or_404(Bakery, owner=request.user)
    
    # Get all orders for this bakery
    all_orders = Order.objects.filter(bakery=bakery)
    
    # Total metrics
    total_orders = all_orders.count()
    
    # Calculate revenue from ALL payments for this bakery's orders
    total_revenue = Payment.objects.filter(
        order__bakery=bakery
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Time-based metrics
    today = timezone.now().date()
    today_orders = all_orders.filter(created_at__date=today).count()
    week_ago = today - timedelta(days=7)
    week_orders = all_orders.filter(created_at__date__gte=week_ago).count()
    month_ago = today - timedelta(days=30)
    month_orders = all_orders.filter(created_at__date__gte=month_ago).count()
    
    # Status breakdown
    status_counts = {
        'pending': all_orders.filter(status='pending').count(),
        'placed': all_orders.filter(status='placed').count(),
        'accepted': all_orders.filter(status='accepted').count(),
        'preparing': all_orders.filter(status='preparing').count(),
        'ready': all_orders.filter(status='ready').count(),
        'rejected': all_orders.filter(status='rejected').count(),
        'delivered': all_orders.filter(status='delivered').count(),
    }
    
    context = {
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'today_orders': today_orders,
        'week_orders': week_orders,
        'month_orders': month_orders,
        'status_counts': status_counts,
    }

    return render(request, 'bakery/analytics.html', context)


# =====================================================
# LOCATION API
# =====================================================
@login_required
def update_location(request):
    if request.method == 'POST':
        import json
        try:
            data = json.loads(request.body)
            lat = float(data.get('latitude'))
            lng = float(data.get('longitude'))

            if request.user.role == 'bakery':
                bakery = request.user.owned_bakery
                bakery.latitude = lat
                bakery.longitude = lng
                bakery.save()
                return JsonResponse({'status': 'success', 'role': 'bakery'})

            elif request.user.role == 'delivery':
                # Update all active assignments for this delivery person
                from delivery.models import DeliveryAssignment
                active_assignments = DeliveryAssignment.objects.filter(
                    delivery_person=request.user
                ).exclude(status__in=['delivered', 'cancelled'])
                
                count = 0
                for assignment in active_assignments:
                    assignment.current_latitude = lat
                    assignment.current_longitude = lng
                    assignment.save()
                    count += 1
                return JsonResponse({
                    'status': 'success', 
                    'role': 'delivery', 
                    'updated_assignments': count,
                    'message': 'Rider position synced' if count > 0 else 'No active orders to track'
                })

            elif request.user.role == 'customer':
                # Update the user's default address (or create one if none exists for demo purposes)
                from users.models import Address
                address = Address.objects.filter(user=request.user, is_default=True).first()
                if not address:
                    # Fallback to any address if no default
                    address = Address.objects.filter(user=request.user).first()
                
                if address:
                    address.latitude = lat
                    address.longitude = lng
                    address.save()
                    return JsonResponse({'status': 'success', 'role': 'customer', 'address_id': address.id})
                else:
                    return JsonResponse({'status': 'error', 'message': 'No address found to update'}, status=404)

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)
