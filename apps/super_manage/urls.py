from django.urls import path

from apps.super_manage.views import school_manage, create_or_modify_school_ajax, remove_ajax, \
    save_ajax, classes_manage, teacher_manage, save_term_ajax, become_a_teacher, cancel_the_teacher
from apps.browse.views import require_login

app_name = 'super_manage'

urlpatterns = [
    path('school_manage', require_login(school_manage), name='school_manage'),
    path('classes_manage', require_login(classes_manage), name='classes_manage'),
    path('teacher_manage', require_login(teacher_manage), name='teacher_manage'),
    path('create_or_modify_school_ajax', create_or_modify_school_ajax, name='create_or_modify_school_ajax'),
    path('remove_ajax', remove_ajax, name='remove_ajax'),
    path('save_ajax', save_ajax, name='save_ajax'),
    path('save_term_ajax', save_term_ajax, name='save_term_ajax'),
    path('become_a_teacher', become_a_teacher, name='become_a_teacher'),
    path('cancel_the_teacher', cancel_the_teacher, name='cancel_the_teacher'),
]