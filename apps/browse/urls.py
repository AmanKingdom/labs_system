from django.urls import path

from .views import assistant_view, login, logout

app_name = 'browse'

urlpatterns = [
    path('assistant_view', assistant_view, name='assistant_view'),
    path('login', login, name='login'),
    path('logout', logout, name='logout'),
]
