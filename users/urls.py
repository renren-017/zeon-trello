from django.urls import path, include

from .views import (SignUpView, ActivateView, CheckEmailView, SuccessView)

urlpatterns = [
    path('register/', SignUpView.as_view(), name='register'),
    path('activate/<uidb64>/<token>/', ActivateView.as_view(), name='activate'),
    path('check-email/', CheckEmailView.as_view(), name='check_email'),
    path('success/', SuccessView.as_view(), name='success')
]