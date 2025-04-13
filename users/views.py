from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout as django_logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from .forms import LoginForm, RegisterForm, EditProfileForm, PasswordResetRequestForm
from dogs.models import Dog
import secrets
from users.models import User
from django.views.generic import TemplateView, UpdateView, FormView, RedirectView
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect


class UserProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/user_profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Профиль пользователя'
        context['user'] = self.request.user
        context['dogs'] = Dog.objects.filter(owner=self.request.user)
        return context


class EditProfileView(LoginRequiredMixin, UpdateView):
    form_class = EditProfileForm
    template_name = 'users/edit_profile.html'
    success_url = reverse_lazy('users:user_profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Профиль успешно обновлен!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)


class ChangePasswordView(LoginRequiredMixin, FormView):
    form_class = PasswordChangeForm
    template_name = 'users/change_password.html'
    success_url = reverse_lazy('users:user_profile')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        user = form.save()
        update_session_auth_hash(self.request, user)
        messages.success(self.request, 'Пароль успешно изменен!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return super().form_invalid(form)


class UserLoginView(FormView):
    form_class = LoginForm
    template_name = 'users/login.html'

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, username=username, password=password)
        if user is not None:
            login(self.request, user)
            return HttpResponseRedirect(reverse_lazy('users:welcome'))  # Используем HttpResponseRedirect для перенаправления
        else:
            messages.error(self.request, 'Неверное имя пользователя или пароль')
            return self.form_invalid(form)  # Вызываем form_invalid для отображения ошибок
        #return redirect('users:welcome') # Не нужен redirect

    def form_invalid(self, form):
        messages.error(self.request, 'Пожалуйста, исправьте ошибки в форме.')
        return self.render_to_response(self.get_context_data(form=form))  # Render the template with the form


class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'users/register.html'

    def form_valid(self, form):
        try:
            user = form.save()
            # Генерация и отправка письма с подтверждением регистрации
            subject = 'Добро пожаловать в наш питомник!'
            message = f'Здравствуйте, {user.username}!\n\nСпасибо за регистрацию в нашем питомнике.'
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [user.email]

            email = EmailMessage(subject, message, from_email, recipient_list)
            email.fail_silently = False
            email.send()

            messages.success(self.request, "Вы успешно зарегистрировались и вошли в систему!")
            login(self.request, user)
            return HttpResponseRedirect(reverse_lazy('users:welcome'))  # Redirect using HttpResponseRedirect
        except Exception as e:
            error_message = f"Ошибка при отправке письма: {type(e).__name__} - {str(e)}"
            messages.error(self.request, f"Ошибка при регистрации: {error_message}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))

class LogoutView(RedirectView):
    url = reverse_lazy('users:logout_success')  # Use reverse_lazy

    def get(self, request, *args, **kwargs):
        django_logout(request)
        return super().get(request, *args, **kwargs)


class PasswordResetRequestView(FormView):
    form_class = PasswordResetRequestForm
    template_name = 'users/password_reset_request.html'

    def form_valid(self, form):
        email = form.cleaned_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(self.request, "Пользователь с таким email не найден.")
            return self.form_invalid(form)  # Render the form with errors

        new_password = secrets.token_urlsafe(16)
        user.set_password(new_password)
        user.save()

        subject = 'Сброс пароля для вашего аккаунта'
        message = render_to_string(
            'users/password_reset_email.html',
            {'user': user, 'new_password': new_password}
        )
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [user.email]
        email = EmailMessage(subject, message, from_email, recipient_list)
        email.fail_silently = False
        email.send()

        messages.success(self.request, "На ваш email отправлено письмо с новым паролем.")
        return HttpResponseRedirect(reverse_lazy('dogs:index'))  # Перенаправление после успешного сброса

    def form_invalid(self, form):
        messages.error(self.request, "Пожалуйста, исправьте ошибки в форме.")
        return self.render_to_response(self.get_context_data(form=form))


class WelcomeView(LoginRequiredMixin, TemplateView):
    template_name = 'users/welcome.html'


class LogoutSuccessView(TemplateView):
    template_name = 'users/logout_success.html'





