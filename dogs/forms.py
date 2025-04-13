# forms.py
from django import forms
from .models import Dog

class DogForm(forms.ModelForm):
    class Meta:
        model = Dog
        fields = ['name', 'breed', 'age', 'description', 'image', 'birth_date']  # Укажите поля, которые нужно отображать в форме
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),  # Для удобного выбора даты
        }

