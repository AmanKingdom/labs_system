from django.contrib import admin

from apps.super_manage.models import School, Institute, SchoolArea, Labs, Department, Grade, Classes, Teacher, \
    TotalRequirements, Course, LabsAttribute

admin.site.register(School)
admin.site.register(SchoolArea)
admin.site.register(Institute)
admin.site.register(Labs)
admin.site.register(Department)
admin.site.register(Grade)
admin.site.register(Classes)
admin.site.register(Teacher)
admin.site.register(TotalRequirements)
admin.site.register(Course)
admin.site.register(LabsAttribute)
