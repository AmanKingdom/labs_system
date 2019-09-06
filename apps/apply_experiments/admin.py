from django.contrib import admin

from apps.apply_experiments.models import ExperimentType, SpecialRequirements, Experiment


class ExperimentTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


admin.site.register(ExperimentType, ExperimentTypeAdmin)


class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('id', 'no', 'name', 'course', 'experiment_type', 'lecture_time', 'which_week', 'days_of_the_week',
                    'section', 'special_requirements', 'status', 'create_time', 'modify_time')
    search_fields = ('name', 'course__name')  # 设置可对校区名称或学校名称进行搜索
    list_filter = ('course__name', 'experiment_type')  # 对学校设置可筛选


admin.site.register(Experiment, ExperimentAdmin)


class SpecialRequirementsAdmin(admin.ModelAdmin):
    list_display = ('id', 'special_consume_requirements', 'special_system_requirements', 'special_soft_requirements')


admin.site.register(SpecialRequirements, SpecialRequirementsAdmin)
