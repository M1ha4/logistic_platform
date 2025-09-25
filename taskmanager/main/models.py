from django.contrib.auth.models import User
from django.db import models

class DriverProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    car_number = models.CharField(max_length=20, blank=True)

    @property
    def is_busy(self):
        return self.order_set.filter(status="in_progress").exists()

    def __str__(self):
        return self.user.username



class Order(models.Model):
    STATUS_CHOICES = [
        ("new", "Новая"),
        ("assigned", "Назначена"),
        ("in_progress", "В пути"),
        ("completed", "Завершена"),
    ]

    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="created_orders")
    driver = models.ForeignKey(DriverProfile, on_delete=models.SET_NULL, null=True, blank=True)
    from_address = models.CharField(max_length=255)
    to_address = models.CharField(max_length=255)
    cargo = models.TextField()
    date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")

    from_lat = models.FloatField(null=True, blank=True)
    from_lng = models.FloatField(null=True, blank=True)
    to_lat = models.FloatField(null=True, blank=True)
    to_lng = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"Заказ {self.id} ({self.status})"


class DriverLocation(models.Model):
    driver = models.ForeignKey(DriverProfile, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)


class OrderDocument(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="documents")
    file = models.FileField(upload_to="documents/")
    uploaded_at = models.DateTimeField(auto_now_add=True)