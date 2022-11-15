from django.urls import path

from holistic_auth.views import (
    LoginView,
    LogoutView,
    LogoutAllView,
    AccountView
)

urlpatterns = [
    path(
        'auth/login/',
        LoginView.as_view(),
        name='login'
    ),
    path(
        'auth/logout/',
        LogoutView.as_view(),
        name='logout'
    ),
    path(
        'auth/logout-all/',
        LogoutAllView.as_view(),
        name='logout-all'
    ),
    path(
        'accounts/',
        AccountView.as_view(),
        name='create-account'
    )
]
