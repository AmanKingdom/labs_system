from django.contrib import admin

from apps.browse.models import Schedule, Assistant

admin.site.register(Schedule)


class AssistantAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'teacher', 'account')  # 设置展示的列
    search_fields = ('name', 'teacher', 'account')  # 设置可对助理名称、教师名称、助理账号进行搜索
    list_filter = ('teacher', )  # 对教师名称设置可筛选


admin.site.register(Assistant, AssistantAdmin)
