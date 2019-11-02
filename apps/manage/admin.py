from django.contrib import admin

from apps.manage.models import School, Institute, SchoolArea, Lab, Department, Grade, Classes, Teacher, \
    TotalRequirements, Course, LabAttribute, SchoolYear, Term, SuperUser, CourseBlock, ArrangeSettings, ExperimentType, \
    Experiment, SpecialRequirements

admin.site.site_header = '实验室数据后台管理系统'
admin.site.site_title = '实验室数据管理'


class SchoolAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'create_time', 'modify_time', 'visible')   # 设置展示的列
    search_fields = ('name', )  # 设置可对学校名称进行搜索
    list_editable = ['name', 'visible']


admin.site.register(School, SchoolAdmin)


class SchoolAreaAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'school', 'create_time', 'modify_time', 'visible')  # 设置展示的列
    search_fields = ('name', 'school__name')  # 设置可对校区名称或学校名称进行搜索
    list_filter = ('school__name', )  # 对学校设置可筛选
    fields = ('school', 'name') # 设置详情信息页面所能显示的字段及其顺序


admin.site.register(SchoolArea, SchoolAreaAdmin)


class InstituteAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'school_area', 'create_time', 'modify_time', 'visible')  # 设置展示的列
    search_fields = ('name', 'school_area__name')  # 设置可对学院名称或学校校区名称进行搜索
    list_filter = ('school_area',)  # 对学校及其校区设置可筛选
    fields = ('school_area', 'name')  # 设置详情信息页面所能显示的字段及其顺序


admin.site.register(Institute, InstituteAdmin)


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'institute', 'create_time', 'modify_time', 'visible')  # 设置展示的列
    search_fields = ('name', 'institute__name')  # 设置可对校区名称或学校名称进行搜索
    list_filter = ('institute',)  # 对学院设置可筛选
    fields = ('institute', 'name')  # 设置详情信息页面所能显示的字段及其顺序


admin.site.register(Department, DepartmentAdmin)


class LabsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'institute', 'number_of_people', 'dispark', 'attribute1', 'attribute2', 'attribute3', 'create_time', 'modify_time', 'visible')  # 设置展示的列
    search_fields = ('name', 'institute__name')  # 设置可对校区名称或学校名称进行搜索
    list_filter = ('institute', 'dispark')  # 对学院和开放情况设置可筛选


admin.site.register(Lab, LabsAdmin)


class LabsAttributeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'school', 'create_time', 'modify_time', 'visible')  # 设置展示的列
    list_editable = ['name', 'school']  # 设置可行内编辑


admin.site.register(LabAttribute, LabsAttributeAdmin)


class GradeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'department', 'create_time', 'modify_time', 'visible')  # 设置展示的列
    search_fields = ('name', 'department')  # 设置可对年级名称或系名称进行搜索
    list_filter = ('department', )  # 对系名称设置可筛选
    fields = ('department', 'name')  # 设置详情信息页面所能显示的字段及其顺序


admin.site.register(Grade, GradeAdmin)


class ClassesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'grade', 'create_time', 'modify_time', 'visible')  # 设置展示的列
    search_fields = ('name', 'grade')  # 设置可对年级名称或系名称进行搜索
    list_filter = ('grade', )  # 对系名称设置可筛选
    fields = ('grade', 'name')  # 设置详情信息页面所能显示的字段及其顺序


admin.site.register(Classes, ClassesAdmin)


class TeacherAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'department', 'account', 'phone', 'create_time', 'modify_time', 'visible')  # 设置展示的列
    search_fields = ('name', 'department', 'account')  # 设置可对教师名称、系名称、教师账号进行搜索
    list_filter = ('department', )  # 对系名称设置可筛选
    fields = ('department', 'name', 'account', 'password', 'phone')  # 设置详情信息页面所能显示的字段及其顺序


admin.site.register(Teacher, TeacherAdmin)


class TotalRequirementsAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'teaching_materials', 'total_consume_requirements', 'total_system_requirements',
                    'total_soft_requirements', 'create_time', 'modify_time', 'visible')  # 设置展示的列


admin.site.register(TotalRequirements, TotalRequirementsAdmin)


class CourseAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'institute', 'term', 'create_time', 'modify_time', 'visible')  # 设置展示的列
    list_editable = ['name', 'institute', 'term']  # 设置可行内编辑
    search_fields = ('name', 'institute')  # 设置可对教师名称、系名称、教师账号进行搜索
    list_filter = ('institute', )  # 对系名称设置可筛选


admin.site.register(Course, CourseAdmin)


class SchoolYearAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__', 'since', 'to', 'create_time', 'modify_time', 'visible')  # 设置展示的列
    list_editable = ['since', 'to'] # 设置可行内编辑


admin.site.register(SchoolYear, SchoolYearAdmin)


class TermAdmin(admin.ModelAdmin):
    list_display = ('id', '__str__', 'name', 'school_year', 'school', 'begin_date', 'create_time', 'modify_time', 'visible')  # 设置展示的列
    list_editable = ['name', 'school_year', 'school']  # 设置可行内编辑


admin.site.register(Term, TermAdmin)


class SuperUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'account', 'school', 'is_teacher', 'create_time', 'modify_time', 'visible')  # 设置展示的列
    search_fields = ('name', 'account')  # 设置可对教师名称、系名称、教师账号进行搜索


admin.site.register(SuperUser, SuperUserAdmin)


class CourseBlockAdmin(admin.ModelAdmin):
    list_display = ('id', 'course', 'days_of_the_week', 'same_new_old', 'need_adjust', 'create_time', 'modify_time', 'visible')  # 设置展示的列


admin.site.register(CourseBlock, CourseBlockAdmin)

admin.site.register(ArrangeSettings)


class ExperimentTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'school', 'create_time', 'modify_time', 'visible')
    list_editable = ['name', 'school', 'visible']  # 设置可行内编辑


admin.site.register(ExperimentType, ExperimentTypeAdmin)


class ExperimentAdmin(admin.ModelAdmin):
    list_display = ('id', 'no', 'name', 'course', 'experiment_type', 'lecture_time', 'which_week', 'days_of_the_week',
                    'section', 'status', 'create_time', 'modify_time', 'visible')
    search_fields = ('name', 'course__name')  # 设置可对校区名称或学校名称进行搜索
    list_filter = ('course__name', 'experiment_type')  # 对学校设置可筛选
    list_editable = ['no', 'name', 'course', 'experiment_type', 'lecture_time', 'which_week', 'days_of_the_week',
                     'section', 'status', 'visible']  # 设置可行内编辑


admin.site.register(Experiment, ExperimentAdmin)


class SpecialRequirementsAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'experiment', 'special_consume_requirements', 'special_system_requirements', 'special_soft_requirements', 'create_time',
        'modify_time', 'visible')
    list_editable = ['special_consume_requirements', 'special_system_requirements',
                     'special_soft_requirements']  # 设置可行内编辑


admin.site.register(SpecialRequirements, SpecialRequirementsAdmin)
