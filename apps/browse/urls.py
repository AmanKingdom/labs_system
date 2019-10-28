from django.urls import path

from .views import assistant_view, logout, require_login, LoginView, RegisterView

app_name = 'browse'

urlpatterns = [
    path('login', LoginView.as_view(), name='login'),
    path('register', RegisterView.as_view(), name='register'),

    path('assistant_view', require_login(assistant_view), name='assistant_view'),
    path('logout', logout, name='logout'),
]
