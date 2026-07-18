from django.urls import path
from .views import (
    LoginView, LogoutView, ChangePasswordView, ForgotPasswordView,
    AdminResetDriverPasswordView, DriverListView, DriverDetailView, current_user
)

urlpatterns = [
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    path('auth/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('auth/forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('auth/reset-driver-password/', AdminResetDriverPasswordView.as_view(), name='reset-driver-password'),
    path('auth/me/', current_user, name='current-user'),
    path('drivers/', DriverListView.as_view(), name='driver-list'),
    path('drivers/<int:pk>/', DriverDetailView.as_view(), name='driver-detail'),
]
