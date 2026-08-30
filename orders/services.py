from django.utils import timezone
from django.contrib.auth import get_user_model

from delivery.models import DeliveryAssignment
from notifications.utils import notify

User = get_user_model()


def assign_delivery(order):
    delivery_person = User.objects.filter(
        role='delivery',
        is_available=True
    ).order_by('available_since').first()

    if not delivery_person:
        # ❌ No delivery person available
        notify(order.customer, "No delivery person available at the moment. Please wait... ⏳")
        return False

    DeliveryAssignment.objects.create(
        order=order,
        delivery_person=delivery_person,
        status='assigned'
    )

    order.status = 'assigned'
    order.save()

    # 🔒 Lock the delivery person
    delivery_person.is_available = False
    delivery_person.save()

    # 🔔 Notifications
    notify(delivery_person, f"New delivery assigned: Order #{order.id} 📦")
    notify(order.customer, f"Delivery partner {delivery_person.username} assigned 🚴")
    notify(order.bakery.owner, f"Delivery partner assigned for Order #{order.id}")

    return True


def process_ready_orders():
    """
    Finds all 'ready' orders that are not yet assigned,
    and tries to assign them to available delivery partners.
    """
    from .models import Order  # avoid circular import

    ready_orders = Order.objects.filter(status='ready').order_by('created_at')

    for order in ready_orders:
        # Stop if no drivers are left (optimization)
        if not User.objects.filter(role='delivery', is_available=True).exists():
            break
        
        assign_delivery(order)
