from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.exceptions import ValidationError
from datetime import date
from django.utils.html import format_html  # Для отображения HTML в админке

User = get_user_model()

class Breed(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название породы', unique=True)
    description = models.TextField(blank=True, null=True, verbose_name='Описание породы')
    image = models.ImageField(upload_to='breed_images/', blank=True, null=True, verbose_name='Изображение породы')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Порода'
        verbose_name_plural = 'Породы'

class Dog(models.Model):
    name = models.CharField(max_length=100, verbose_name='Кличка')
    breed = models.ForeignKey(Breed, on_delete=models.CASCADE, related_name='dogs', verbose_name='Порода')
    age = models.PositiveIntegerField(verbose_name='Возраст')
    description = models.TextField(blank=True, verbose_name='Описание')
    image = models.ImageField(upload_to='dog_images/', blank=True, null=True, verbose_name='Фотография')
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='dogs', verbose_name='Владелец')
    birth_date = models.DateField(verbose_name='Дата рождения', null=True, blank=True)

    def __str__(self):
        return self.name

    def clean(self):
        if self.birth_date and self.birth_date > date.today():
            raise ValidationError('Дата рождения не может быть в будущем.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Собака'
        verbose_name_plural = 'Собаки'
        indexes = [
            models.Index(fields=['breed'], name='dog_breed_idx'),  # Добавляем индекс
        ]

