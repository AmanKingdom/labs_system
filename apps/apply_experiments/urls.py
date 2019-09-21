from django.urls import path

from apps.apply_experiments.views import apply, load_classes_of_course, submit_experiments, \
    manage_application, change_experiments, remove_all_experiments, weeks_analyze, rooms_analyze
from apps.browse.views import require_login

app_name = 'apply_experiments'

urlpatterns = [
    path('apply', require_login(apply), name='apply'),
    path('ajax/load_classes_of_course/', load_classes_of_course, name='ajax_load_classes_of_course'),
    path('submit_experiments', require_login(submit_experiments), name='submit_experiments'),
    path('manage_application', require_login(manage_application), name='manage_application'),
    path('remove_all_experiments', require_login(remove_all_experiments), name='remove_all_experiments'),
    path('change_experiments/<course_id>/', require_login(change_experiments), name='change_experiments'),

    path('weeks_analyze', require_login(weeks_analyze), name='weeks_analyze'),
    path('rooms_analyze', require_login(rooms_analyze), name='rooms_analyze'),
]
