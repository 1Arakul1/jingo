# dogs/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Breed, Dog
from .forms import DogForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse, reverse_lazy  # Add reverse_lazy here, at the top
from django.http import JsonResponse
from django.views import View
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib import messages


class AddDogToProfileView(LoginRequiredMixin, View):
    def post(self, request, dog_id):
        dog = get_object_or_404(Dog, pk=dog_id)

        if dog.owner:
            messages.error(request, f"Собака '{dog.name}' уже принадлежит пользователю {dog.owner.username}.")
        else:
            dog.owner = request.user
            dog.save()
            messages.success(request, f"Собака '{dog.name}' успешно добавлена в ваш профиль.")

        return redirect(request.META.get('HTTP_REFERER', reverse('dogs:dogs_list')))


class RemoveDogFromProfileView(LoginRequiredMixin, View):
    def post(self, request, dog_id):  # Изменено на POST, т.к. DELETE напрямую из HTML не поддерживается
        dog = get_object_or_404(Dog, pk=dog_id, owner=request.user)
        dog.owner = None
        dog.save()
        return JsonResponse({'message': 'Собака успешно удалена из профиля.'})


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'dogs/index.html'
    extra_context = {'title': 'Главная страница'}


class BreedsView(LoginRequiredMixin, TemplateView):
    template_name = 'dogs/breeds.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        title = 'Породы собак'
        breeds = Breed.objects.prefetch_related('dogs').all()
        breeds_data = []
        for breed in breeds:
            dogs = breed.dogs.order_by('?')[:3]
            breeds_data.append({'breed': breed, 'dogs': dogs})
        context['title'] = title
        context['breeds_data'] = breeds_data
        return context


class DogsListView(LoginRequiredMixin, ListView):
    model = Dog
    template_name = 'dogs/dogs_list.html'
    context_object_name = 'dogs'  # Имя переменной в шаблоне
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Список всех собак'
        return context


class DogCreateView(LoginRequiredMixin, CreateView):
    model = Dog
    form_class = DogForm
    template_name = 'dogs/dog_create.html'
    success_url = reverse_lazy('dogs:dogs_list')  # Добавлено для перенаправления

    def form_valid(self, form):
        messages.success(self.request, f"Собака '{form.instance.name}' успешно добавлена!")
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{form[field].label}: {error}")
        return super().form_invalid(form)

from django.urls import reverse_lazy

class DogUpdateView(LoginRequiredMixin, UpdateView):
    model = Dog
    form_class = DogForm
    template_name = 'dogs/dog_update.html'
    success_url = reverse_lazy('dogs:dogs_list')  # Добавлено для перенаправления

    def get_object(self, queryset=None):
        dog = super().get_object(queryset=queryset)
        if dog.owner != self.request.user:
            raise Http404("У вас нет прав на редактирование этой собаки.")
        return dog

    def form_valid(self, form):
        messages.success(self.request, f"Информация о собаке '{form.instance.name}' успешно обновлена!")
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{form[field].label}: {error}")
        return super().form_invalid(form)

from django.http import Http404

class DogDeleteView(LoginRequiredMixin, DeleteView):
    model = Dog
    template_name = 'dogs/dog_confirm_delete.html'
    success_url = reverse_lazy('dogs:dogs_list')

    def get_object(self, queryset=None):
        dog = super().get_object(queryset=queryset)
        if dog.owner != self.request.user:
            raise Http404("У вас нет прав на удаление этой собаки.")
        return dog

    def delete(self, request, *args, **kwargs):
        dog = self.get_object()
        messages.success(request, f"Собака '{dog.name}' успешно удалена.")
        return super().delete(request, *args, **kwargs)


class DogReadView(LoginRequiredMixin, DetailView):
    model = Dog
    template_name = 'dogs/dog_read.html'
    context_object_name = 'dog'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Информация о собаке'
        context['is_owner'] = self.object.owner == self.request.user
        return context


class AllDogsView(LoginRequiredMixin, ListView):
    model = Dog
    template_name = 'dogs/all_dogs.html'
    context_object_name = 'dogs'
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Все собаки'
        return context

