# users/urls.py
from django.urls import path
from . import views
from .views import (
    UserProfileView,
    EditProfileView,
    LogoutView,
    RegisterView,
    UserLoginView,
    WelcomeView,
    LogoutSuccessView,
    PasswordResetRequestView,
    ChangePasswordView
)

app_name = 'users'

urlpatterns = [
    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('edit_profile/', EditProfileView.as_view(), name='edit_profile'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='user_login'),  # This line is crucial
    path('welcome/', WelcomeView.as_view(), name='welcome'),
    path('logout_success/', LogoutSuccessView.as_view(), name='logout_success'),
    path('password_reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('profile/change_password/', ChangePasswordView.as_view(), name='change_password'),
]