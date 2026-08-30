from django.shortcuts import render, get_object_or_404
from .models import Bakery
from products.models import Product


def bakery_list(request):
    query = request.GET.get('q', '')
    bakeries = Bakery.objects.filter(
        is_active=True,
        name__icontains=query
    )
    return render(request, 'bakeries/bakery_list.html', {
        'bakeries': bakeries,
        'query': query
    })


def bakery_detail(request, id):
    bakery = get_object_or_404(Bakery, id=id, is_active=True)
    products = Product.objects.filter(bakery=bakery, is_available=True)
    
    wishlisted_product_ids = []
    if request.user.is_authenticated:
        from wishlist.models import Wishlist
        wishlisted_product_ids = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)

    return render(request, 'bakeries/bakery_detail.html', {
        'bakery': bakery,
        'products': products,
        'wishlisted_product_ids': wishlisted_product_ids
    })
