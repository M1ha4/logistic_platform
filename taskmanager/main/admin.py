from django.contrib import admin
from .models import DriverProfile, Order, DriverLocation, OrderDocument

admin.site.register(DriverProfile)
admin.site.register(Order)
admin.site.register(DriverLocation)
admin.site.register(OrderDocument)


