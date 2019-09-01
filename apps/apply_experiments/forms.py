from django import forms

from apps.super_manage.models import Course

#
# class CourseForm(forms.ModelForm):
#     class Meta:
#         model = Course
#         fields = ['teachers.department', 'name', 'course']
#         widgets = {
#             'name': forms.TextInput(attrs={})
#         }
