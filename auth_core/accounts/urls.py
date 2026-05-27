from django.urls import path
from .views import UserRegisterView, UserLoginView, UserLogoutView, ProfileView, ProfileUpdateView, UserPasswordChangeView, AccountStatusView
from . import views
from django.views.generic import TemplateView

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name = 'register'),
    path('login/', UserLoginView.as_view(), name = 'login'),
    path('terminating/', views.logout_sequence_view, name = 'logout_sequence'),
    path('logout', UserLogoutView.as_view(next_page = 'login'), name = 'logout'),
    path('profile/', ProfileView.as_view(), name = 'profile'),
    path('profile/edit/', ProfileUpdateView.as_view(), name = 'edit_profile'),
    path('profile/password/', UserPasswordChangeView.as_view(), name = 'password_change'),
    path('profile/status/', AccountStatusView.as_view(), name='account_status'),
    path('request-verification/', views.request_verification_link, name='request_verification'),
    path('verify-email/<uuid:token>/', views.verify_email, name = 'verify_email'),
]