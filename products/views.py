from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from .models import Product, Review


# ✅ Cake list (Search by item)
def cake_list(request):
    query = request.GET.get('q', '')
    cakes = Product.objects.all()

    if query:
        cakes = cakes.filter(name__icontains=query)

    wishlisted_product_ids = []
    if request.user.is_authenticated:
        from wishlist.models import Wishlist
        wishlisted_product_ids = Wishlist.objects.filter(user=request.user).values_list('product_id', flat=True)

    return render(request, 'explore/cakes.html', {
        'cakes': cakes,
        'query': query,
        'wishlisted_product_ids': wishlisted_product_ids
    })


# ✅ Cake detail (Reviews live here)
def cake_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    is_wishlisted = False
    if request.user.is_authenticated:
        from wishlist.models import Wishlist
        is_wishlisted = Wishlist.objects.filter(user=request.user, product=product).exists()

    return render(request, 'products/cake_detail.html', {
        'product': product,
        'is_wishlisted': is_wishlisted
    })


# ✅ Add review
@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        Review.objects.create(
            product=product,
            user=request.user,
            rating=request.POST.get('rating'),
            comment=request.POST.get('comment')
        )

    return redirect('cake_detail', product_id=product.id)
