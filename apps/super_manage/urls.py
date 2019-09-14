from django.urls import path

from apps.super_manage.views import school_manage
from apps.browse.views import require_login

app_name = 'super_manage'

urlpatterns = [
    path('school_manage', require_login(school_manage), name='school_manage'),
]