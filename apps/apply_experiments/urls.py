from django.urls import path

from apps.apply_experiments.views import apply, load_classes_of_course, load_labs_of_institute, submit_experiments, \
    manage_application, change_experiments

app_name = 'apply_experiments'

urlpatterns = [
    path('apply', apply, name='apply'),
    path('ajax/load-classes-of-course/', load_classes_of_course, name='ajax_load_classes_of_course'),
    path('ajax/load-labs-of-institute/', load_labs_of_institute, name='ajax_load_labs_of_institute'),
    path('submit-experiments', submit_experiments, name='submit_experiments'),
    path('manage-application', manage_application, name='manage_application'),
    path('change-experiments/<school_year>/<term>/<course>/', change_experiments, name='change_experiments'),
]
