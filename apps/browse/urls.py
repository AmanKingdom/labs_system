from django.urls import path

from .views import assistant_view, login, logout, require_login, register, set_school

app_name = 'browse'

urlpatterns = [
    path('assistant_view', require_login(assistant_view), name='assistant_view'),
    path('register', register, name='register'),
    path('set_school', set_school, name='set_school'),
    path('login', login, name='login'),
    path('logout', logout, name='logout'),
]
