from django.urls import path

from apps.super_manage.views import school_manage, create_or_modify_school_ajax, remove_school_areas_ajax, \
    save_school_areas_ajax
from apps.browse.views import require_login

app_name = 'super_manage'

urlpatterns = [
    path('school_manage', require_login(school_manage), name='school_manage'),
    path('create_or_modify_school_ajax', create_or_modify_school_ajax, name='create_or_modify_school_ajax'),
    path('remove_school_areas_ajax', remove_school_areas_ajax, name='remove_school_areas_ajax'),
    path('save_school_areas_ajax', save_school_areas_ajax, name='save_school_areas_ajax'),
]