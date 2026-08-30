from django.db import models
from django.conf import settings

class GeneratedCake(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='generated_cakes'
    )
    prompt = models.TextField()
    image_url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cake Design: {self.prompt[:30]}..."


class TasteProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='taste_profile'
    )
    
    SWEETNESS_CHOICES = [(i, str(i)) for i in range(1, 11)]
    
    FLAVOR_CHOICES = [
        ('chocolate', '🍫 Chocolate'),
        ('vanilla', '🍦 Vanilla'),
        ('fruit', '🍓 Fruit / Berry'),
        ('nuts', '🥜 Nutty'),
        ('spicy', '🌶️ Spiced'),
    ]
    
    TEXTURE_CHOICES = [
        ('soft', '☁️ Soft & Spongey'),
        ('crunchy', '🍪 Crunchy & Crispy'),
        ('creamy', '🥛 Creamy & Rich'),
    ]

    sweet_tooth_level = models.IntegerField(choices=SWEETNESS_CHOICES, default=5)
    favorite_flavor = models.CharField(max_length=20, choices=FLAVOR_CHOICES)
    texture_preference = models.CharField(max_length=20, choices=TEXTURE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile: {self.user.username}"


class QuoteRequest(models.Model):
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quote_requests')
    bakery = models.ForeignKey('bakeries.Bakery', on_delete=models.CASCADE, related_name='quote_requests')
    generated_cake = models.ForeignKey('ai_features.GeneratedCake', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, default='pending') # pending, replied
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Quote from {self.customer.username} to {self.bakery.name}"
