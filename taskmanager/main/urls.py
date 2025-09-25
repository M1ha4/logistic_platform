from django.urls import path
from . import views

urlpatterns = [
    path("manager/", views.manager_dashboard, name="manager_dashboard"),
    path("driver/", views.driver_dashboard, name="driver_dashboard"),
    path("admin-panel/", views.admin_dashboard, name="admin_dashboard"),
    path("api/update-location/", views.update_location, name="update_location"),
    path("admin-panel/order/<int:order_id>/map/", views.order_map, name="order_map")
]
