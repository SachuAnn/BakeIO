from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem
from products.models import Product

@login_required
def cart_view(request):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    items = CartItem.objects.filter(cart=cart)

    total = sum(item.item_total() for item in items)

    return render(request, 'cart/cart.html', {
        'items': items,
        'total': total
    })


@login_required
def add_to_cart(request, product_id):
    cart, _ = Cart.objects.get_or_create(user=request.user)
    product = get_object_or_404(Product, id=product_id)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product
    )

    if not created:
        item.quantity += 1
    item.save()

    return redirect('cart_view')


@login_required
def update_quantity(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)

    if request.method == 'POST':
        qty = int(request.POST['quantity'])
        if qty > 0:
            item.quantity = qty
            item.save()

    return redirect('cart_view')


@login_required
def remove_item(request, item_id):
    item = get_object_or_404(CartItem, id=item_id)
    item.delete()
    return redirect('cart_view')
