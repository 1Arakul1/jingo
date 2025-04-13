from django import forms
from .models import Dog
from datetime import date
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class DogForm(forms.ModelForm):
    class Meta:
        model = Dog
        fields = ['name', 'breed', 'age', 'description', 'image', 'birth_date']  # Укажите поля, которые нужно отображать в форме
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),  # Для удобного выбора даты
        }
