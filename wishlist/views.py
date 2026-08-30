from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from products.models import Product
from .models import Wishlist

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item = Wishlist.objects.filter(user=request.user, product=product)

    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'
    
    if wishlist_item.exists():
        wishlist_item.delete()
        if is_ajax:
            return JsonResponse({'status': 'removed', 'message': f'Removed {product.name} from wishlist'})
        messages.info(request, f"Removed {product.name} from your wishlist.")
    else:
        Wishlist.objects.create(user=request.user, product=product)
        if is_ajax:
            return JsonResponse({'status': 'added', 'message': f'Added {product.name} to wishlist'})
        messages.success(request, f"Added {product.name} to your wishlist!")
        
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def remove_from_wishlist(request, product_id):
    Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
    return redirect('view_wishlist')

@login_required
def view_wishlist(request):
    items = Wishlist.objects.filter(user=request.user)
    return render(request, 'wishlist/wishlist.html', {'items': items})


