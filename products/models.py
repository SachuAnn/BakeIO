from django.db import models
from django.conf import settings


class Offer(models.Model):
    bakery = models.ForeignKey(
        'bakeries.Bakery',
        on_delete=models.CASCADE,
        related_name='offers'
    )
    title = models.CharField(max_length=100)
    discount_percent = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} ({self.discount_percent}%)"


class Product(models.Model):
    bakery = models.ForeignKey(
        'bakeries.Bakery',
        on_delete=models.CASCADE,
        related_name='products'
    )
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='cakes/', blank=True, null=True)

    offer = models.ForeignKey(
        'products.Offer',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
    )

    is_available = models.BooleanField(default=True)
    model_3d = models.FileField(upload_to='cake_models/', blank=True, null=True)

    @property
    def discounted_price(self):
        if self.offer and self.offer.is_active:
            discount = (self.offer.discount_percent / 100) * float(self.price)
            return round(float(self.price) - discount, 2)
        return self.price

    def __str__(self):
        return self.name


class Review(models.Model):
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    rating = models.IntegerField(
        choices=[(i, i) for i in range(1, 6)]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.rating}"
