from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
import uuid

from cart.models import Cart, CartItem
from .models import Order, OrderItem, Payment, Invoice
from notifications.models import Notification
from orders.services import assign_delivery


# 🔔 small helper (optional but clean)
def notify(user, message):
    Notification.objects.create(user=user, message=message)


from users.models import Address

@login_required
def checkout(request):
    """Redirect to the first step of checkout."""
    return redirect('checkout_address')

@login_required
def checkout_address(request):
    """Step 1: Select Delivery Address"""
    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        if address_id:
            # Store address in session
            request.session['checkout_address_id'] = address_id
            return redirect('checkout_payment')
    
    addresses = Address.objects.filter(user=request.user)
    return render(request, 'orders/checkout_address.html', {'addresses': addresses})

@login_required
def add_address(request):
    """Helper to add address inline"""
    if request.method == 'POST':
        # Get coordinates from form (sent by JavaScript geolocation)
        latitude = request.POST.get('latitude', '').strip()
        longitude = request.POST.get('longitude', '').strip()
        
        # Parse coordinates if provided
        lat = None
        lon = None
        if latitude and longitude:
            try:
                lat = float(latitude)
                lon = float(longitude)
            except ValueError:
                pass
        
        Address.objects.create(
            user=request.user,
            full_name=request.POST.get('full_name'),
            phone_number=request.POST.get('phone_number'),
            street_address=request.POST.get('street_address'),
            city=request.POST.get('city'),
            latitude=lat,
            longitude=lon,
            is_default=request.POST.get('is_default') == 'on'
        )
        
        if lat and lon:
            messages.success(request, "✅ Address saved with location data!")
        else:
            messages.warning(request, "⚠️ Address saved but location not detected. Distance check may not work accurately.")
            
    return redirect('checkout_address')

@login_required
def delete_address(request, address_id):
    """Delete a saved address"""
    if request.method == 'POST':
        address = get_object_or_404(Address, id=address_id, user=request.user)
        address.delete()
        
        # Clear session if deleted address was selected
        if str(address_id) == str(request.session.get('checkout_address_id')):
             if 'checkout_address_id' in request.session:
                del request.session['checkout_address_id']
                
    return redirect('checkout_address')

@login_required
def checkout_payment(request):
    """Step 2: Payment & Place Order"""
    cart = get_object_or_404(Cart, user=request.user)
    items = CartItem.objects.filter(cart=cart)
    
    if not items.exists():
        return redirect('cart_view')
        
    total = sum(item.item_total() for item in items)
    
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method', 'cod')
        address_id = request.session.get('checkout_address_id')
        
        if not address_id:
            return redirect('checkout_address')
            
        address = get_object_or_404(Address, id=address_id)
        bakery = items.first().product.bakery # Assuming single bakery order for now

        # 🚀 RADIUS ENFORCEMENT (Zomato Style)
        from utils.location_utils import calculate_distance, estimate_eta
        
        # Check if address has valid coordinates
        if not address.latitude or not address.longitude:
            messages.error(request, "⚠️ This address doesn't have location data. Please add a new address with location detection enabled.")
            return redirect('checkout_address')
        
        # Check if bakery has valid coordinates
        if not bakery.latitude or not bakery.longitude:
            messages.error(request, "⚠️ This bakery hasn't set up their location yet. Please contact them or choose another bakery.")
            return redirect('cart_view')
        
        # Calculate distance between bakery and delivery address
        distance = calculate_distance(
            bakery.latitude, bakery.longitude,
            address.latitude, address.longitude
        )

        # Enforce 10km delivery radius
        if distance > 10.0:
            messages.error(request, f"Sorry, this bakery is too far (Distance: {distance:.1f} km). We only deliver within 10km.")
            return redirect('checkout_address')

        # Calculate estimated time based on distance
        status_eta = estimate_eta(distance)

        # 1️⃣ Create Order
        order = Order.objects.create(
            customer=request.user,
            bakery=bakery,
            delivery_address=address,
            status='placed',
            estimated_delivery_time=timezone.now() + timezone.timedelta(minutes=int(status_eta.split('-')[1])),
            created_at=timezone.now()
        )

        # 2️⃣ Create Order Items
        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_at_purchase=item.product.discounted_price,
                original_price=item.product.price
            )

        # 3️⃣ Create Payment
        Payment.objects.create(
            order=order,
            amount=total,
            method=payment_method,
            status='paid' if payment_method != 'cod' else 'pending'
        )

        # 4️⃣ Create Invoice
        Invoice.objects.create(
            order=order,
            invoice_number=f"INV-{uuid.uuid4().hex[:8].upper()}"
        )

        # 5️⃣ Clear cart
        items.delete()
        if 'checkout_address_id' in request.session:
            del request.session['checkout_address_id']

        # 6️⃣ Notify
        notify(bakery.owner, f"New order #{order.id} received 📦")
        notify(request.user, f"Order #{order.id} placed successfully! 🚀")

        return redirect('my_orders')
        
    original_total = sum(item.quantity * float(item.product.price) for item in items)
    savings = original_total - float(total)
    
    return render(request, 'orders/checkout_payment.html', {
        'total': total,
        'original_total': original_total,
        'savings': savings
    })


@login_required
def my_orders(request):
    orders = Order.objects.filter(
        customer=request.user
    ).order_by('-created_at')

    return render(request, 'orders/my_orders.html', {
        'orders': orders
    })


@login_required
def cancel_order(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        customer=request.user
    )

    # Cancel constraint: User can only cancel before "Ready"
    if order.can_cancel:
        order.status = 'cancelled'
        order.save()

        notify(
            request.user,
            f"Order #{order.id} cancelled ❌"
        )

        notify(
            order.bakery.owner,
            f"Order #{order.id} was cancelled by customer"
        )

    return redirect('my_orders')


@login_required
def payment_history(request):
    payments = Payment.objects.filter(
        order__customer=request.user
    ).order_by('-created_at')

    return render(request, 'orders/payment_history.html', {
        'payments': payments
    })


@login_required
def view_invoice(request, order_id):
    order = get_object_or_404(
        Order,
        id=order_id,
        customer=request.user
    )
    invoice = get_object_or_404(Invoice, order=order)

    return render(request, 'orders/invoice_fixed.html', {
        'order': order,
        'invoice': invoice
    })

@login_required
def track_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # ✅ Security: only customer, bakery owner, or assigned delivery person
    allowed = False

    if order.customer == request.user:
        allowed = True

    elif order.bakery.owner == request.user:
        allowed = True

    elif hasattr(order, "delivery_assignment") and order.delivery_assignment:
        if order.delivery_assignment.delivery_person == request.user:
            allowed = True

    if not allowed:
        return redirect("my_orders")

    # =====================================================
    # ✅ Safe Map Coordinates (No Template Default Filters)
    # =====================================================

    # Bakery coordinates (fallback to Bangalore)
    bakery_lat = getattr(order.bakery, "latitude", None) or 12.9716
    bakery_lng = getattr(order.bakery, "longitude", None) or 77.5946

    # Customer coordinates (fallback)
    customer_lat = getattr(order.delivery_address, "latitude", None) or 12.9279
    customer_lng = getattr(order.delivery_address, "longitude", None) or 77.6271

    # Rider coordinates (only if assigned)
    rider_lat = None
    rider_lng = None

    if hasattr(order, "delivery_assignment") and order.delivery_assignment:
        rider_lat = getattr(order.delivery_assignment, "current_latitude", None)
        rider_lng = getattr(order.delivery_assignment, "current_longitude", None)

    # =====================================================
    # ✅ Render Clean Template Context
    # =====================================================
    from utils.location_utils import calculate_distance, estimate_eta
    
    distance = calculate_distance(bakery_lat, bakery_lng, customer_lat, customer_lng)
    eta_range = estimate_eta(distance)

    return render(request, "orders/order_tracking.html", {
        "order": order,
        "bakery_lat": bakery_lat,
        "bakery_lng": bakery_lng,
        "customer_lat": customer_lat,
        "customer_lng": customer_lng,
        "rider_lat": rider_lat,
        "rider_lng": rider_lng,
        "distance_km": round(distance, 1),
        "eta_range": eta_range,
    })

