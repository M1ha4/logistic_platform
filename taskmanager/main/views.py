from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order, DriverProfile, DriverLocation
from .forms import OrderForm, DocumentForm

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
import json

from .models import DriverProfile, DriverLocation

from django.utils import timezone
from django.contrib.auth.decorators import login_required

from django.contrib.auth.views import LoginView
from django.urls import reverse

class RoleBasedLoginView(LoginView):
    template_name = "login.html"

    def get_success_url(self):
        user = self.request.user

        # Админ → админская панель
        if user.is_superuser or user.is_staff:
            return reverse("admin_dashboard")

        # Водитель → проверим есть ли DriverProfile
        if hasattr(user, "driverprofile"):
            return reverse("driver_dashboard")

        # Менеджер → для примера дадим отдельную страницу
        return reverse("manager_dashboard")



@login_required
def manager_dashboard(request):
    orders = Order.objects.all().order_by("-date")
    drivers = DriverProfile.objects.all()

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.manager = request.user  # <-- менеджер назначается автоматически
            order.save()
            return redirect("manager_dashboard")
    else:
        form = OrderForm()

    return render(request, "manager_dashboard.html", {
        "orders": orders,
        "drivers": drivers,
        "form": form,
    })


@login_required
def driver_dashboard(request):
    driver_profile = getattr(request.user, "driverprofile", None)
    if not driver_profile:
        return render(request, "driver_dashboard.html", {"no_driver": True})

    active_order = Order.objects.filter(driver=driver_profile, status="in_progress").first()

    # обработка кнопок
    if request.method == "POST" and active_order:
        if "share_location" in request.POST:
            lat = request.POST.get("lat")
            lng = request.POST.get("lng")
            if lat and lng:
                DriverLocation.objects.create(driver=driver_profile, latitude=lat, longitude=lng)
        elif "upload_doc" in request.POST and request.FILES.get("document"):
            doc = request.FILES["document"]
            active_order.documents.create(file=doc, uploaded_at=timezone.now())
        elif "finish_order" in request.POST:
            active_order.status = "done"
            active_order.save()
            return redirect("driver_dashboard")

    return render(request, "driver_dashboard.html", {
        "active_order": active_order,
    })

#@login_required
def admin_dashboard(request):
    drivers = DriverProfile.objects.all()
    orders = Order.objects.all()
    return render(request, "admin_dashboard.html", {"drivers": drivers, "orders": orders})


def order_map(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    # берем последнюю точку водителя (если есть)
    driver_location = None
    if order.driver:
        driver_location = DriverLocation.objects.filter(driver=order.driver).order_by('-timestamp').first()

    points = []
    # start
    if order.from_lat is not None and order.from_lng is not None:
        points.append({
            "type": "start",
            "lat": float(order.from_lat),
            "lng": float(order.from_lng),
            "label": f"Старт: {order.from_address}"
        })
    # driver
    if driver_location:
        points.append({
            "type": "driver",
            "lat": float(driver_location.latitude),
            "lng": float(driver_location.longitude),
            "label": f"Водитель: {order.driver.user.username}"
        })
    # end
    if order.to_lat is not None and order.to_lng is not None:
        points.append({
            "type": "end",
            "lat": float(order.to_lat),
            "lng": float(order.to_lng),
            "label": f"Финиш: {order.to_address}"
        })

    context = {
        "order": order,
        # безопасно сериализуем
        "points_json": json.dumps(points, cls=DjangoJSONEncoder)
    }
    return render(request, "order_map.html", context)


@csrf_exempt
def update_location(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            lat = data.get("lat")
            lng = data.get("lng")

            driver = DriverProfile.objects.get(user=request.user)

            DriverLocation.objects.create(
                driver=driver,
                latitude=lat,
                longitude=lng
            )

            return JsonResponse({"status": "ok"}, status=201)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=405)