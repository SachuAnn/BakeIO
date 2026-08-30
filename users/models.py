from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    role = models.CharField(max_length=20)
    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('bakery', 'Bakery'),
        ('delivery', 'Delivery'),
        ('admin', 'Admin'),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.username} ({self.role})"
    is_available = models.BooleanField(default=False)
    available_since = models.DateTimeField(null=True, blank=True)

class Address(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='addresses')
    full_name = models.CharField(max_length=100)
    street_address = models.TextField()
    city = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=20)
    is_default = models.BooleanField(default=False)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.full_name} - {self.city}"