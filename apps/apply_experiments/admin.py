from django.contrib import admin

from apps.apply_experiments.models import ExperimentType, SpecialRequirements, Experiment

admin.site.register(ExperimentType)
admin.site.register(SpecialRequirements)
admin.site.register(Experiment)
