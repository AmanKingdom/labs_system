from django.test import TestCase


class ModelsTest(TestCase):

    def test_get_all_func_in_model_school(self):
        from apps.manage.models import School
        s = School.objects.all()
        if s:
            s = s[0]

        print(s.get_all_institutes())
        print(s.get_all_departments())
        print(s.get_all_grades())
        print(s.get_all_classes())
        print(s.get_all_teachers())
        print(s.get_all_labs())
        print(s.get_all_courses())

