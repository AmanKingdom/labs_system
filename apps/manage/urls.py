from django.urls import path

from apps.manage.views import become_a_teacher, cancel_the_teacher, personal_info, \
    application_check, ScheduleView, ArrangeView, CourseBlockView, SetSchoolView, SystemSettingsView, SchoolAreasView, \
    InstitutesView, DepartmentsView, GradesView, SchoolManageView, ClassesView, \
    ClassesManageView, TeachersView, TeacherManageView, CoursesView, CourseManageView, LabAttributesView, \
    LabAttributeManageView, LabManageView, LabsView, ExperimentTypesView, ExperimentTypeManageView, \
    ApplicationManageView
from apps.browse.views import require_login

app_name = 'manage'

urlpatterns = [
    path('schools/<school_id>/school_areas', SchoolAreasView.as_view(), name='school_areas'),
    path('schools/<school_id>/institutes', InstitutesView.as_view(), name='institutes'),
    path('schools/<school_id>/departments', DepartmentsView.as_view(), name='departments'),
    path('schools/<school_id>/grades', GradesView.as_view(), name='grades'),
    path('schools/<school_id>/classes', ClassesView.as_view(), name='classes'),
    path('schools/<school_id>/teachers', TeachersView.as_view(), name='teachers'),
    path('schools/<school_id>/courses', CoursesView.as_view(), name='courses'),
    path('schools/<school_id>/labs', LabsView.as_view(), name='labs'),
    path('schools/<school_id>/lab_attributes', LabAttributesView.as_view(), name='lab_attributes'),
    path('schools/<school_id>/experiment_types', ExperimentTypesView.as_view(), name='experiment_types'),

    path('set_school', SetSchoolView.as_view(), name='set_school'),

    path('personal_info', require_login(personal_info), name='personal_info'),
    path('become_a_teacher', become_a_teacher, name='become_a_teacher'),
    path('cancel_the_teacher', cancel_the_teacher, name='cancel_the_teacher'),

    path('system_settings', SystemSettingsView.as_view(), name='system_settings'),

    path('school_manage', SchoolManageView.as_view(), name='school_manage'),
    path('classes_manage', ClassesManageView.as_view(), name='classes_manage'),
    path('teacher_manage', TeacherManageView.as_view(), name='teacher_manage'),
    path('course_manage', CourseManageView.as_view(), name='course_manage'),
    path('lab_manage', LabManageView.as_view(), name='lab_manage'),
    path('lab_attribute_manage', LabAttributeManageView.as_view(), name='lab_attribute_manage'),
    path('experiment_type_manage', ExperimentTypeManageView.as_view(), name='experiment_type_manage'),

    path('application_manage', ApplicationManageView.as_view(), name='application_manage'),

    path('application_check/<course_id>/<status>/', application_check, name='application_check'),

    path('arrange', require_login(ArrangeView.as_view()), name='arrange'),
    path('schedule', ScheduleView.as_view(), name='schedule'),
    path('need_adjust_course_block/<course_block_id>/', CourseBlockView.as_view(), name='need_adjust_course_block'),
]
