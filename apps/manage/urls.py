from django.urls import path

from apps.manage.views import create_or_modify_school_ajax, remove_ajax, \
    save_ajax, become_a_teacher, cancel_the_teacher, course_manage, \
    labs_attribute_manage, experiment_type_manage, lab_manage, personal_info, application_manage, \
    application_check, ScheduleView, ArrangeView, CourseBlockView, SetSchoolView, SystemSettingsView, SchoolAreasView, \
    InstitutesView, DepartmentsView, GradesView, SchoolManageView, test_school_areas_view, ClassesView, \
    ClassesManageView, TeachersView, TeacherManageView
from apps.browse.views import require_login

app_name = 'manage'

urlpatterns = [
    path('test_school_areas', test_school_areas_view, name='test_school_areas'),

    path('schools/<school_id>/school_areas', SchoolAreasView.as_view(), name='school_areas'),
    path('schools/<school_id>/institutes', InstitutesView.as_view(), name='institutes'),
    path('schools/<school_id>/departments', DepartmentsView.as_view(), name='departments'),
    path('schools/<school_id>/grades', GradesView.as_view(), name='grades'),
    path('schools/<school_id>/classes', ClassesView.as_view(), name='classes'),
    path('schools/<school_id>/teachers', TeachersView.as_view(), name='teachers'),

    # path('schools/<school_id>/courses', CoursesView, name='courses'),
    # path('schools/<school_id>/labs', LabsView, name='labs'),
    # path('schools/<school_id>/lab_attributes', LabAttributesView, name='lab_attributes'),
    # path('schools/<school_id>/experiment_types', ExperimentTypesView, name='experiment_types'),


    path('set_school', SetSchoolView.as_view(), name='set_school'),

    path('personal_info', require_login(personal_info), name='personal_info'),
    path('system_settings', SystemSettingsView.as_view(), name='system_settings'),

    path('school_manage', SchoolManageView.as_view(), name='school_manage'),
    path('classes_manage', ClassesManageView.as_view(), name='classes_manage'),
    path('teacher_manage', TeacherManageView.as_view(), name='teacher_manage'),

    path('course_manage', require_login(course_manage), name='course_manage'),
    path('experiment_type_manage', require_login(experiment_type_manage), name='experiment_type_manage'),
    path('labs_attribute_manage', require_login(labs_attribute_manage), name='labs_attribute_manage'),
    path('lab_manage', require_login(lab_manage), name='lab_manage'),
    path('application_manage', require_login(application_manage), name='application_manage'),

    path('create_or_modify_school_ajax', create_or_modify_school_ajax, name='create_or_modify_school_ajax'),
    path('remove_ajax', remove_ajax, name='remove_ajax'),
    path('save_ajax', save_ajax, name='save_ajax'),
    path('become_a_teacher', become_a_teacher, name='become_a_teacher'),
    path('cancel_the_teacher', cancel_the_teacher, name='cancel_the_teacher'),

    path('application_check/<course_id>/<status>/', application_check, name='application_check'),

    path('arrange', require_login(ArrangeView.as_view()), name='arrange'),
    path('schedule', ScheduleView.as_view(), name='schedule'),
    path('need_adjust_course_block/<course_block_id>/', CourseBlockView.as_view(), name='need_adjust_course_block'),
]
