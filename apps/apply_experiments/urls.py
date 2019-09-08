from django.urls import path

from apps.apply_experiments.views import apply, load_classes_of_course,  submit_experiments, \
    manage_application, change_experiments
from browse.views import require_login

app_name = 'apply_experiments'

urlpatterns = [
    path('apply', require_login(apply), name='apply'),
    path('ajax/load-classes-of-course/', load_classes_of_course, name='ajax_load_classes_of_course'),
    path('submit-experiments', require_login(submit_experiments), name='submit_experiments'),
    path('manage-application', require_login(manage_application), name='manage_application'),
    path('change-experiments/<term>/<course_name>/', require_login(change_experiments), name='change_experiments'),
]
