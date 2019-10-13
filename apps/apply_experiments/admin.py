from django.contrib import admin

from apps.manage.models import ExperimentType, Experiment, SpecialRequirements


class ExperimentTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'school', 'create_time', 'modify_time', 'visible')
    list_editable = ['name', 'school', 'visible']  # 设置可行内编辑


admin.site.register(ExperimentType, ExperimentTypeAdmin)


class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('id', 'no', 'name', 'course', 'experiment_type', 'lecture_time', 'which_week', 'days_of_the_week',
                    'section', 'special_requirements', 'status', 'create_time', 'modify_time', 'visible')
    search_fields = ('name', 'course__name')  # 设置可对校区名称或学校名称进行搜索
    list_filter = ('course__name', 'experiment_type')  # 对学校设置可筛选
    list_editable = ['no', 'name', 'course', 'experiment_type', 'lecture_time', 'which_week', 'days_of_the_week',
                     'section', 'special_requirements', 'status', 'visible']  # 设置可行内编辑


admin.site.register(Experiment, ExperimentAdmin)


class SpecialRequirementsAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'special_consume_requirements', 'special_system_requirements', 'special_soft_requirements', 'create_time',
        'modify_time', 'visible')
    list_editable = ['special_consume_requirements', 'special_system_requirements',
                     'special_soft_requirements']  # 设置可行内编辑


admin.site.register(SpecialRequirements, SpecialRequirementsAdmin)
