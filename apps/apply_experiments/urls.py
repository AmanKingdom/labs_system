from django.urls import path

from apps.apply_experiments.views import apply, load_classes_of_course, load_labs_of_institute

app_name = 'apply_experiments'

urlpatterns = [
    path('apply', apply, name='apply'),
    path('ajax/load-classes-of-course/', load_classes_of_course, name='ajax_load_classes_of_course'),
    path('ajax/load-labs-of-institute/', load_labs_of_institute, name='ajax_load_labs_of_institute'),
]
