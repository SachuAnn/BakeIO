from users.models import User
from delivery.models import DeliveryAssignment


def assign_delivery(order):
    """
    Assigns the first available delivery user to the order.
    """

    # ❌ Do not assign twice
    if DeliveryAssignment.objects.filter(order=order).exists():
        return

    # ✅ Get first available delivery user
    delivery_user = User.objects.filter(
        role='delivery',
        is_active=True
    ).exclude(
        deliveryassignment__status__in=['assigned', 'picked']
    ).first()

    if not delivery_user:
        return  # No delivery person available

    # ✅ Create assignment
    DeliveryAssignment.objects.create(
        order=order,
        delivery_person=delivery_user,
        status='assigned'
    )
