from django import forms
from .models import Order, Document


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["from_address", "to_address", "cargo", "date", "driver"]


class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ["image"]
