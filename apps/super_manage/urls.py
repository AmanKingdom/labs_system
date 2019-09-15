from django.urls import path

from apps.super_manage.views import school_manage, create_or_modify_school_ajax, remove_ajax, \
    save_ajax, classes_manage
from apps.browse.views import require_login

app_name = 'super_manage'

urlpatterns = [
    path('school_manage', require_login(school_manage), name='school_manage'),
    path('classes_manage', require_login(classes_manage), name='classes_manage'),
    path('create_or_modify_school_ajax', create_or_modify_school_ajax, name='create_or_modify_school_ajax'),
    path('remove_ajax', remove_ajax, name='remove_ajax'),
    path('save_ajax', save_ajax, name='save_ajax'),
]