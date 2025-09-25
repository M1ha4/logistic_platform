from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order, DriverProfile, DriverLocation
from .forms import OrderForm, DocumentForm


@login_required
def manager_dashboard(request):
    orders = Order.objects.all()
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.manager = request.user
            order.status = "assigned"
            order.save()
            return redirect("manager_dashboard")
    else:
        form = OrderForm()
    return render(request, "manager_dashboard.html", {"orders": orders, "form": form})


@login_required
def driver_dashboard(request):
    driver = get_object_or_404(DriverProfile, user=request.user)
    orders = Order.objects.filter(driver=driver)
    if request.method == "POST":
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.order = orders.first()  # упрощенно: прикрепляем к первому заказу
            doc.save()
            return redirect("driver_dashboard")
    else:
        form = DocumentForm()
    return render(request, "driver_dashboard.html", {"orders": orders, "form": form})


@login_required
def admin_dashboard(request):
    orders = Order.objects.all()
    locations = DriverLocation.objects.all()
    return render(request, "admin_dashboard.html", {"orders": orders, "locations": locations})
