from django.contrib import admin

from apps.super_manage.models import School, Institute, SchoolArea, Labs, Department, Grade, Classes, Teacher, \
    TotalRequirements, Course, LabsAttribute


class SchoolAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')   # 设置展示的列
    search_fields = ('name', )  # 设置可对学校名称进行搜索


admin.site.register(School, SchoolAdmin)


class SchoolAreaAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'school')  # 设置展示的列
    search_fields = ('name', 'school__name')  # 设置可对校区名称或学校名称进行搜索
    list_filter = ('school__name', )  # 对学校设置可筛选
    fields = ('school', 'name') # 设置详情信息页面所能显示的字段及其顺序


admin.site.register(SchoolArea, SchoolAreaAdmin)


class InstituteAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'school_area')  # 设置展示的列
    search_fields = ('name', 'school_area__name')  # 设置可对学院名称或学校校区名称进行搜索
    list_filter = ('school_area',)  # 对学校及其校区设置可筛选
    fields = ('school_area', 'name')  # 设置详情信息页面所能显示的字段及其顺序


admin.site.register(Institute, InstituteAdmin)


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'institute')  # 设置展示的列
    search_fields = ('name', 'institute__name')  # 设置可对校区名称或学校名称进行搜索
    list_filter = ('institute',)  # 对学院设置可筛选
    fields = ('institute', 'name')  # 设置详情信息页面所能显示的字段及其顺序


admin.site.register(Department, DepartmentAdmin)


class LabsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'institute', 'number_of_people', 'dispark')  # 设置展示的列
    search_fields = ('name', 'institute__name')  # 设置可对校区名称或学校名称进行搜索
    list_filter = ('institute', 'dispark')  # 对学院和开放情况设置可筛选
    fields = ('institute', 'name', 'number_of_people', 'dispark', 'attributes')  # 设置详情信息页面所能显示的字段及其顺序
    filter_horizontal = ('attributes',)  # 多对多选项的更好界面，也可垂直排列：filter_vertical


admin.site.register(Labs, LabsAdmin)

admin.site.register(LabsAttribute)


class GradeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'department')  # 设置展示的列
    search_fields = ('name', 'department')  # 设置可对年级名称或系名称进行搜索
    list_filter = ('department', )  # 对系名称设置可筛选
    fields = ('department', 'name')  # 设置详情信息页面所能显示的字段及其顺序


admin.site.register(Grade, GradeAdmin)


class ClassesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'grade')  # 设置展示的列
    search_fields = ('name', 'grade')  # 设置可对年级名称或系名称进行搜索
    list_filter = ('grade', )  # 对系名称设置可筛选
    fields = ('grade', 'name')  # 设置详情信息页面所能显示的字段及其顺序


admin.site.register(Classes, ClassesAdmin)


class TeacherAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'department', 'account', 'phone')  # 设置展示的列
    search_fields = ('name', 'department', 'account')  # 设置可对教师名称、系名称、教师账号进行搜索
    list_filter = ('department', )  # 对系名称设置可筛选
    fields = ('department', 'name', 'account', 'password', 'phone')  # 设置详情信息页面所能显示的字段及其顺序


admin.site.register(Teacher, TeacherAdmin)


class TotalRequirementsAdmin(admin.ModelAdmin):
    list_display = ('id', 'teaching_materials', 'total_consume_requirements', 'total_system_requirements',
                    'total_soft_requirements')  # 设置展示的列


admin.site.register(TotalRequirements, TotalRequirementsAdmin)


class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'institute', 'modify_time')  # 设置展示的列
    search_fields = ('name', 'institute')  # 设置可对教师名称、系名称、教师账号进行搜索
    list_filter = ('institute', )  # 对系名称设置可筛选


admin.site.register(Course, CourseAdmin)

