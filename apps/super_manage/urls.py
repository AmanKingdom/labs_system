from django.urls import path

from apps.super_manage.views import school_manage, create_or_modify_school_ajax, remove_ajax, \
    save_ajax, classes_manage, teacher_manage, save_term_ajax, become_a_teacher, cancel_the_teacher, course_manage, \
    labs_attribute_manage, experiment_type_manage, lab_manage, system_settings, personal_info, application_manage, \
    application_check, get_schedule
from apps.browse.views import require_login

app_name = 'super_manage'

urlpatterns = [
    path('personal_info', require_login(personal_info), name='personal_info'),
    path('system_settings', require_login(system_settings), name='system_settings'),
    path('school_manage', require_login(school_manage), name='school_manage'),
    path('classes_manage', require_login(classes_manage), name='classes_manage'),
    path('teacher_manage', require_login(teacher_manage), name='teacher_manage'),
    path('course_manage', require_login(course_manage), name='course_manage'),
    path('experiment_type_manage', require_login(experiment_type_manage), name='experiment_type_manage'),
    path('labs_attribute_manage', require_login(labs_attribute_manage), name='labs_attribute_manage'),
    path('lab_manage', require_login(lab_manage), name='lab_manage'),
    path('application_manage', require_login(application_manage), name='application_manage'),

    path('create_or_modify_school_ajax', create_or_modify_school_ajax, name='create_or_modify_school_ajax'),
    path('remove_ajax', remove_ajax, name='remove_ajax'),
    path('save_ajax', save_ajax, name='save_ajax'),
    path('save_term_ajax', save_term_ajax, name='save_term_ajax'),
    path('become_a_teacher', become_a_teacher, name='become_a_teacher'),
    path('cancel_the_teacher', cancel_the_teacher, name='cancel_the_teacher'),

    path('application_check/<course_id>/<status>/', application_check, name='application_check'),

    path('get_schedule', get_schedule, name='get_schedule')
]