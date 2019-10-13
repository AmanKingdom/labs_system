from django.urls import path

from .views import assistant_view, login, logout, require_login, register, set_school, LoginView

app_name = 'browse'

urlpatterns = [
    path('assistant_view', require_login(assistant_view), name='assistant_view'),
    path('register', register, name='register'),
    path('set_school', set_school, name='set_school'),
    path('login', LoginView.as_view(), name='login'),
    path('logout', logout, name='logout'),
]
