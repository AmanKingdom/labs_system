from django.contrib import admin

from apps.apply_experiments.models import ExperimentType, SpecialRequirements, Experiment


class ExperimentTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


admin.site.register(ExperimentType, ExperimentTypeAdmin)
admin.site.register(SpecialRequirements)
admin.site.register(Experiment)
