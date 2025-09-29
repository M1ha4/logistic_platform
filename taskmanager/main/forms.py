from django import forms
from .models import Order, OrderDocument, DriverProfile


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        # 👇 исключаем дату и менеджера (они ставятся автоматически)
        exclude = ["date", "manager"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # показываем список только водителей
        self.fields["driver"].queryset = DriverProfile.objects.all()


class DocumentForm(forms.ModelForm):
    class Meta:
        model = OrderDocument
        fields = ["file"]
