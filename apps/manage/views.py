import json
from functools import wraps

from django.http import JsonResponse, HttpResponseRedirect, QueryDict, Http404, HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from apps.manage.models import *

from logging_setting import ThisLogger
from apps.manage.tools.list_tool import get_model_field_ids
from apps.manage.tools.setting_tool import *
from apps.manage.tools.string_tool import *

this_logger = ThisLogger().logger

MANAGER = 'managers'
TEACHER = 'teachers'
STUDENT = 'students'

GROUP_LIST = [MANAGER, TEACHER, STUDENT]

STATUS = {
    '1': '已提交待审核',
    '2': '审核不通过',
    '3': '审核通过'
}

# 设计13个可用的课程块背景颜色
COLOR_DIVS = ['color1_div', 'color2_div', 'color3_div', 'color4_div', 'color5_div', 'color6_div',
              'color7_div', 'color8_div', 'color9_div', 'color10_div', 'color11_div', 'color12_div', 'color13_div']

MENUS = [
    {'name': '个人信息', 'url_name': 'personal_info', 'parent': None, 'icon': '<i class="fa fa-user-circle-o"></i>', 'app_name': 'manage', 'roles': GROUP_LIST},
    {'name': '系统设置', 'url_name': 'system_settings', 'parent': None, 'icon': '<i class="fa fa-cog"></i>', 'app_name': 'manage', 'roles': [GROUP_LIST[0],]},
    {'name': '教学信息管理', 'url_name': None, 'parent': None, 'icon': '<i class="fa fa-bank"></i>', 'app_name': 'manage', 'roles': [GROUP_LIST[0],]},
    {'name': '校内机构管理', 'url_name': 'school_manage', 'parent': '教学信息管理', 'icon': None, 'app_name': 'manage', 'roles': [GROUP_LIST[0],]},
    {'name': '班级管理', 'url_name': 'classes_manage', 'parent': '教学信息管理', 'icon': None, 'app_name': 'manage', 'roles': [GROUP_LIST[0],]},
    {'name': '教师管理', 'url_name': 'teacher_manage', 'parent': '教学信息管理', 'icon': None, 'app_name': 'manage', 'roles': [GROUP_LIST[0],]},
    {'name': '课程管理', 'url_name': 'course_manage', 'parent': '教学信息管理', 'icon': None, 'app_name': 'manage', 'roles': [GROUP_LIST[0],]},
    {'name': '实验室信息管理', 'url_name': None, 'parent': None, 'icon': '<i class="fa fa-laptop"></i>', 'app_name': 'manage', 'roles': [GROUP_LIST[0],]},
    {'name': '实验室管理', 'url_name': 'lab_manage', 'parent': '实验室信息管理', 'icon': None, 'app_name': 'manage', 'roles': [GROUP_LIST[0],]},
    {'name': '实验室属性管理', 'url_name': 'lab_attribute_manage', 'parent': '实验室信息管理', 'icon': None, 'app_name': 'manage', 'roles': [GROUP_LIST[0],]},
    {'name': '实验课管理', 'url_name': None, 'parent': None, 'icon': '<i class="fa fa-tasks"></i>', 'app_name': 'manage', 'roles': [GROUP_LIST[0],]},
    {'name': '实验类型设置', 'url_name': 'experiment_type_manage', 'parent': '实验课管理', 'icon': None, 'app_name': 'manage', 'roles': [GROUP_LIST[0],]},
    {'name': '智能排课', 'url_name': 'arrange', 'parent': '实验课管理', 'icon': None, 'app_name': 'manage', 'roles': [GROUP_LIST[0],]},
    {'name': '实验申请', 'url_name': None, 'parent': None, 'icon': '<i class="fa fa-edit"></i>', 'app_name': 'manage', 'roles': [GROUP_LIST[0], GROUP_LIST[1]]},
    {'name': '填写申请表', 'url_name': 'apply', 'parent': '实验申请', 'icon': None, 'app_name': 'manage', 'roles': [GROUP_LIST[0], GROUP_LIST[1]]},
    {'name': '实验申请表审批', 'url_name': 'application_manage', 'parent': '实验申请', 'icon': None, 'app_name': 'manage', 'roles': [GROUP_LIST[0], GROUP_LIST[1]]},
    {'name': '课程表', 'url_name': None, 'parent': None, 'icon': '<i class="fa fa-pie-chart"></i>', 'app_name': 'manage', 'roles': GROUP_LIST},
    {'name': '周次课程表', 'url_name': 'weeks_timetable', 'parent': '课程表', 'icon': None, 'app_name': 'manage', 'roles': GROUP_LIST},
    {'name': '实验室课程表', 'url_name': 'rooms_timetable', 'parent': '课程表', 'icon': None, 'app_name': 'manage', 'roles': GROUP_LIST},
    {'name': '', 'url_name': 'application_details', 'parent': None, 'icon': None, 'app_name': 'manage', 'roles': [GROUP_LIST[0],]},
]


def init_all(request):
    groups = Group.objects.all()
    if not groups:
        for group in GROUP_LIST:
            Group.objects.create(name=group)

    menus = Menu.objects.all()
    if not menus:
        for menu in MENUS:
            roles = []
            for role in menu['roles']:
                temp = Group.objects.get(name=role)
                roles.append(temp.id)
            parent = None
            if menu['parent']:
                parent = Menu.objects.get(name=menu['parent'])
            del menu['parent']
            del menu['roles']

            m = Menu.objects.create(**menu)
            m.roles.add(*roles)
            if parent:
                m.parent = parent
            m.save()

    return JsonResponse({'state': True})


# 后期需根据实际情况调整下列静态数据：
def set_choices_context(context):
    """
    为申请实验和修改实验页面提供的选项数据：实验类型、学时、（所有学院、所有实验室属性、所有实验室）括号内为暂时的
    :param context:
    :return:
    """
    # 实验类型
    context['experiments_type'] = ExperimentType.objects.all() if ExperimentType.objects.all() else ""
    # 学时
    context['lecture_time'] = [x for x in range(1, 11)]
    # TODO:因为找不到联动数据的解决方案，暂时用所有实验室来代替
    context['labs_of_institute'] = Institute.objects.all() if Institute.objects.all() else ""
    context['lab_attributes'] = LabAttribute.objects.all() if LabAttribute.objects.all() else ""
    context['all_labs'] = Lab.objects.filter(dispark=True)


def set_menu_name(context, url_name):
    """
    如果menu为根菜单，则设置context中的menu_parent_name为menu的name，否则设置menu_url_name为menu的url_name，
    并设置对应的menu_parent_name为menu的父菜单的name
    :param context:
    :param url_name:
    :return:
    """
    menu = Menu.objects.filter(url_name=url_name).first()
    if menu:
        context['title'] = menu.name
        if menu.parent:
            context['menu_parent_name'] = menu.parent.name
        context['menu_url_name'] = menu.url_name


# 验证登录
def require_login(view):
    @wraps(view)
    def new_view(request, *args, **kwargs):
        if request.session.get('user_account', None):
            this_logger.debug('验证登录：' + request.session['user_name'] + ' 用户已登录')
            return view(request, *args, **kwargs)
        return HttpResponseRedirect('/browse/login')

    return new_view


# 页面权限认证
def require_permission(url_name):
    def require_permission2(view_func):
        @wraps(view_func)
        def new_view(self, request, *args, **kwargs):
            if request.user:
                from apps.manage.models import User
                user = User.objects.get(id=request.user.id)
                if user:
                    if user.has_menu(url_name):
                        return view_func(self, request, *args, **kwargs)
            return HttpResponseRedirect('/browse/login')

        return new_view

    return require_permission2


# 本方法应该在每次创建一个新学校时被调用
def create_default_term_for_school(school):
    school_year = SchoolYear.objects.all()
    if not school_year:
        set_system_school_year()
        school_year = SchoolYear.objects.all()[0]
    else:
        school_year = school_year[0]
    Term.objects.create(name='第一学期', school_year=school_year, school=school)
    return True


# 该视图应该在注册时设置学校 和 跳过设置学校后在院校设置页面 被使用
@method_decorator(require_login, name='put')
class SetSchoolView(View):
    context = {
        'title': '设置学校',
        'status': True,
        'message': None,
    }

    def get(self, request):
        return render(request, 'browse/set_school.html', self.context)

    def post(self, request):  # 创建学校
        school_name = request.POST.get('school_name', None)
        if school_name:
            if School.objects.filter(name=school_name):
                this_logger.debug('已存在学校：' + school_name)
                return JsonResponse({'status': False, 'message': '该学校名称已经被人注册'})
            else:
                school = School.objects.create(name=school_name)
                try:
                    manager = User.objects.get(username=request.session.get('user_account', None))
                    manager.school = school
                    manager.save()
                    request.session['school_id'] = manager.school_id
                    # 创建一个学校的同时应该创建一个默认的学期给它
                    create_default_term_for_school(school)
                    return JsonResponse({'status': True})
                except User.DoesNotExist:
                    # 如果是用户恶意设置信息使得找不到管理员信息，那么刚注册的学校也应该删掉
                    school.delete()
                    raise Http404('管理员信息找不到，请重试')
        else:
            return JsonResponse({'status': False, 'message': '请输入学校名称'})

    def put(self, request):  # 修改学校信息
        put_data = QueryDict(request.body)
        this_logger.debug('设置学校视图：接收到put_data：' + str(put_data))
        put_data = json.loads(list(put_data.keys())[0])

        if School.objects.filter(name=put_data['school_name']):
            this_logger.debug('已存在学校：' + put_data['school_name'])
            return JsonResponse({'status': False, 'message': '该学校名称已经被人注册'})
        else:
            try:
                school = School.objects.get(id=request.session['school_id'])
                school.name = put_data['school_name']
                school.save()
                return JsonResponse({'status': True})
            except Exception as e:
                print(e)
                return JsonResponse({'status': False, 'message': '出错了，请重试'})


@method_decorator(require_login, name='dispatch')
class SystemSettingsView(View):
    url_name = 'system_settings'
    context = {
        'school_year': None,
        'term': None,
    }

    @require_permission(url_name=url_name)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        set_menu_name(self.context, self.url_name)

        # 学年学期数据要在判断设置完系统学年信息后才能获取
        self.context['school_year'] = SchoolYear.objects.all()[0]
        if request.session.get('school_id', None):
            self.context['term'] = Term.objects.get(school_id=request.session['school_id'])
        return render(request, 'manage/system_settings.html', self.context)

    def put(self, request):
        put_data = QueryDict(request.body)
        this_logger.debug('系统设置--接收到put数据：' + str(put_data))
        put_data = json.loads(list(put_data.keys())[0])

        try:
            term_name = put_data.get('term_name', None)
            begin_date = put_data.get('begin_date', None)
            this_logger.debug('term_name:' + term_name + '，begin_date:' + begin_date)
            self.context['term'].name = term_name
            self.context['term'].begin_date = begin_date
            self.context['term'].save()
            return JsonResponse({'status': True})
        except Exception as e:
            print(e)
            return JsonResponse({'status': False, 'message': '保存的信息有误'})


class LittleSameModelBaseView(View):
    # 以下是默认的参数
    model_Chinese_name = '校区'
    model = SchoolArea
    get_all_what_func_name = 'get_all_school_areas'

    # 通常，该方法被其他模型的视图使用时要重写
    def make_return_data(self, objects):
        return_data = []
        for obj, i in zip(objects, range(0, len(objects))):
            new_dict = {
                'id': i,
                'school_area_name': obj.name,
                'hide_school_area_name': obj.name,
                'id_in_database': obj.id
            }
            return_data.append(new_dict)
        return return_data

    def get(self, request, school_id):
        return_data = []
        if school_id:
            try:
                objects = getattr(School.objects.get(id=school_id), self.get_all_what_func_name)()
                return_data = self.make_return_data(objects)
            except Exception as e:
                this_logger.debug(str(e))
                raise Http404('找不到学校id为' + school_id + '的相关信息')
        # 这里的content_type="application/json"其实可有可无
        return HttpResponse(json.dumps(return_data), content_type="application/json")

    def put(self, request, school_id):  # 修改信息
        put_data = QueryDict(request.body)
        put_data = json.loads(list(put_data.keys())[0])
        this_logger.debug(self.model_Chinese_name + '信息--接收到put数据：' + str(put_data))

        for data in put_data:
            if self.model is User:
                user = User.objects.filter(id=data['id']).first()
                if self.model_Chinese_name == '教师':
                    user.groups.add(Group.objects.get(name=TEACHER))
                if 'password' in data.keys():
                    password = data['password']
                    user.set_password(password)
                    del data['password']
                user.save()
            self.model.objects.filter(id=data['id']).update(**data)

        return JsonResponse({'status': True})

    def post(self, request, school_id):  # 创建信息
        post_data = json.loads(list(request.POST.keys())[0])
        this_logger.debug(self.model_Chinese_name + '信息--接收到post数据：' + str(post_data))

        for data in post_data:
            if self.model is SchoolArea or self.model is LabAttribute or self.model is ExperimentType:
                self.model.objects.create(**data, school_id=school_id)
            elif self.model is User:
                user = User.objects.create_user(**data)
                if self.model_Chinese_name == '教师':
                    user.groups.add(Group.objects.get(name=TEACHER))
                    user.save()
            else:
                self.model.objects.create(**data)
        return JsonResponse({'status': True})

    def delete(self, request, school_id):
        delete_data = QueryDict(request.body)
        delete_data = json.loads(list(delete_data.keys())[0])
        this_logger.debug(self.model_Chinese_name + '信息--接收到delete数据：' + str(delete_data))

        for id in delete_data:
            self.model.objects.filter(id=id).delete()
        return JsonResponse({'status': True})


class SchoolAreasView(LittleSameModelBaseView):
    model_Chinese_name = '校区'
    model = SchoolArea
    get_all_what_func_name = 'get_all_school_areas'

    def make_return_data(self, objects):
        return_data = []
        for obj, i in zip(objects, range(0, len(objects))):
            new_dict = {
                'id': i,
                'school_area_name': obj.name,
                'hide_school_area_name': obj.name,
                'id_in_database': obj.id
            }
            return_data.append(new_dict)
        return return_data


class InstitutesView(LittleSameModelBaseView):
    model_Chinese_name = '学院'
    model = Institute
    get_all_what_func_name = 'get_all_institutes'

    def make_return_data(self, objects):
        return_data = []
        for obj, i in zip(objects, range(0, len(objects))):
            new_dict = {
                'id': i,
                'school_area': obj.school_area_id,
                'hide_school_area_id': obj.school_area_id,
                'institute_name': obj.name,
                'hide_institute_name': obj.name,
                'id_in_database': obj.id
            }
            return_data.append(new_dict)
        return return_data


class DepartmentsView(LittleSameModelBaseView):
    model_Chinese_name = '系别'
    model = Department
    get_all_what_func_name = 'get_all_departments'

    def make_return_data(self, objects):
        return_data = []
        for obj, i in zip(objects, range(0, len(objects))):
            new_dict = {
                'id': i,
                'institute': obj.institute_id,
                'hide_institute_id': obj.institute_id,
                'department_name': obj.name,
                'hide_department_name': obj.name,
                'id_in_database': obj.id
            }
            return_data.append(new_dict)
        return return_data


class GradesView(LittleSameModelBaseView):
    model_Chinese_name = '年级'
    model = Grade
    get_all_what_func_name = 'get_all_grades'

    def make_return_data(self, objects):
        return_data = []
        for obj, i in zip(objects, range(0, len(objects))):
            new_dict = {
                'id': i,
                'department': obj.department_id,
                'hide_department_id': obj.department_id,
                'grade_name': obj.name,
                'hide_grade_name': obj.name,
                'id_in_database': obj.id
            }
            return_data.append(new_dict)
        return return_data


class ClassesView(LittleSameModelBaseView):
    model_Chinese_name = '班级'
    model = Classes
    get_all_what_func_name = 'get_all_classes'

    def make_return_data(self, objects):
        return_data = []
        for obj, i in zip(objects, range(0, len(objects))):
            new_dict = {
                'id': i,
                'grade': obj.grade_id,
                'hide_grade_id': obj.grade_id,
                'classes_name': obj.name,
                'hide_classes_name': obj.name,
                'id_in_database': obj.id
            }
            return_data.append(new_dict)
        return return_data


class TeachersView(LittleSameModelBaseView):
    model_Chinese_name = '教师'
    model = User
    get_all_what_func_name = 'get_all_teachers'

    def make_return_data(self, objects):
        return_data = []
        for obj, i in zip(objects, range(0, len(objects))):
            new_dict = {
                'id': i,
                'department': obj.department_id,
                'hide_department_id': obj.department_id,
                'name': obj.name,
                'hide_name': obj.name,
                'username': obj.username,
                'hide_username': obj.username,
                'password': obj.password,
                'hide_password': obj.password,
                'id_in_database': obj.id
            }
            return_data.append(new_dict)
        return return_data


class CoursesView(LittleSameModelBaseView):
    model_Chinese_name = '课程'
    model = Course
    get_all_what_func_name = 'get_all_courses'

    def make_return_data(self, objects):
        return_data = []
        for obj, i in zip(objects, range(0, len(objects))):
            classes_ids_list = get_model_field_ids(obj, 'classes')
            classes_ids = list_to_str(classes_ids_list, ',')

            teachers_ids_list = get_model_field_ids(obj, 'teachers')
            teachers_ids = list_to_str(teachers_ids_list, ',')
            new_dict = {
                'id': i,
                'institute': obj.institute_id,
                'hide_institute_id': obj.institute_id,
                'course_name': obj.name,
                'hide_course_name': obj.name,
                'attribute': obj.attribute.id if obj.attribute else None,
                'hide_attribute': obj.attribute.id if obj.attribute else None,
                'classes': classes_ids,
                'hide_classes': classes_ids,
                'teachers': teachers_ids,
                'hide_teachers': teachers_ids,
                'id_in_database': obj.id
            }
            return_data.append(new_dict)
        return return_data

    def put(self, request, school_id):  # 修改信息
        put_data = QueryDict(request.body)
        put_data = json.loads(list(put_data.keys())[0])
        this_logger.debug(self.model_Chinese_name + '信息--接收到put数据：' + str(put_data))

        for data in put_data:
            me = self.model.objects.get(id=data['id'])
            if 'institute_id' in data.keys():
                me.institute = Institute.objects.get(id=data['institute_id'])
            if 'name' in data.keys():
                me.name = data['name']
            if 'attribute' in data.keys():
                me.attribute = LabAttribute.objects.get(id=data['attribute'])
            if 'classes' in data.keys():
                if data['classes']:
                    this_logger.debug(self.model_Chinese_name + '--classes：' + str(data['classes']))
                    classes_ids_list = str_to_non_repetitive_list(data['classes'], ',')
                    me.classes.set(classes_ids_list)
                else:
                    me.classes.clear()
            if 'teachers' in data.keys():
                if data['teachers']:
                    this_logger.debug(self.model_Chinese_name + '--teachers：' + str(data['teachers']))
                    teachers_ids_list = str_to_non_repetitive_list(data['teachers'], ',')
                    me.teachers.set(teachers_ids_list)
                else:
                    me.teachers.clear()
            me.save()
        return JsonResponse({'status': True})

    def post(self, request, school_id):  # 创建信息
        post_data = json.loads(list(request.POST.keys())[0])
        this_logger.debug(self.model_Chinese_name + '信息--接收到post数据：' + str(post_data))

        term = Term.objects.get(school_id=school_id)

        for data in post_data:
            me = self.model.objects.create(institute_id=data['institute_id'], name=data['name'], term=term)
            if 'attribute' in data.keys():
                me.attribute = LabAttribute.objects.get(id=data['attribute'])
            if 'classes' in data.keys():
                this_logger.debug(self.model_Chinese_name + '--classes：' + str(data['classes']))
                classes_ids_list = str_to_non_repetitive_list(data['classes'], ',')
                me.classes.set(classes_ids_list)
            if 'teachers' in data.keys():
                this_logger.debug(self.model_Chinese_name + '--teachers：' + str(data['teachers']))
                teachers_ids_list = str_to_non_repetitive_list(data['teachers'], ',')
                me.teachers.set(teachers_ids_list)
            me.save()
        return JsonResponse({'status': True})


class LabsView(LittleSameModelBaseView):
    model_Chinese_name = '实验室'
    model = Lab
    get_all_what_func_name = 'get_all_labs'

    def make_return_data(self, objects):
        return_data = []
        for obj, i in zip(objects, range(0, len(objects))):
            new_dict = {
                'id': i,
                'institute': obj.institute_id,
                'hide_institute_id': obj.institute_id,
                'lab_name': obj.name,
                'hide_lab_name': obj.name,
                'number_of_people': obj.number_of_people,
                'hide_number_of_people': obj.number_of_people,
                'dispark': '1' if obj.dispark else '0',
                'hide_dispark': '1' if obj.dispark else '0',
                'attribute1': obj.attribute1.id if obj.attribute1 else '',
                'hide_attribute1_id': obj.attribute1.id if obj.attribute1 else '',
                'attribute2': obj.attribute2.id if obj.attribute2 else '',
                'hide_attribute2_id': obj.attribute2.id if obj.attribute2 else '',
                'attribute3': obj.attribute3.id if obj.attribute3 else '',
                'hide_attribute3_id': obj.attribute3.id if obj.attribute3 else '',
                'equipments': obj.equipments if obj.equipments else '',
                'hide_equipments': obj.equipments if obj.equipments else '',
                'id_in_database': obj.id
            }
            return_data.append(new_dict)
        return return_data

    def put(self, request, school_id):  # 修改信息
        put_data = QueryDict(request.body)
        put_data = json.loads(list(put_data.keys())[0])
        this_logger.debug(self.model_Chinese_name + '信息--接收到put数据：' + str(put_data))

        for data in put_data:
            if 'dispark' in data.keys():
                data['dispark'] = True if data['dispark'] == '1' else False
            self.model.objects.filter(id=data['id']).update(**data)
        return JsonResponse({'status': True})

    def post(self, request, school_id):  # 创建信息
        post_data = json.loads(list(request.POST.keys())[0])
        this_logger.debug(self.model_Chinese_name + '信息--接收到post数据：' + str(post_data))

        for data in post_data:
            if 'dispark' in data.keys():
                data['dispark'] = True if data['dispark'] == '1' else False
            self.model.objects.create(**data)
        return JsonResponse({'status': True})


class LabAttributesView(LittleSameModelBaseView):
    model_Chinese_name = '实验室属性'
    model = LabAttribute
    get_all_what_func_name = 'get_all_lab_attributes'

    def make_return_data(self, objects):
        return_data = []
        for obj, i in zip(objects, range(0, len(objects))):
            new_dict = {
                'id': i,
                'lab_attribute_name': obj.name,
                'hide_lab_attribute_name': obj.name,
                'id_in_database': obj.id
            }
            return_data.append(new_dict)
        return return_data


class ExperimentTypesView(LittleSameModelBaseView):
    model_Chinese_name = '实验类型'
    model = ExperimentType
    get_all_what_func_name = 'get_all_experiment_types'

    def make_return_data(self, objects):
        return_data = []
        for obj, i in zip(objects, range(0, len(objects))):
            new_dict = {
                'id': i,
                'experiment_type_name': obj.name,
                'hide_experiment_type_name': obj.name,
                'id_in_database': obj.id
            }
            return_data.append(new_dict)
        return return_data


# 个人信息页面
@method_decorator(require_login, name='dispatch')
class PersonalInfo(View):
    context = {
        'term': None,
    }
    url_name = 'personal_info'

    @require_permission(url_name=url_name)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        set_menu_name(self.context, self.url_name)
        return render(request, 'manage/personal_info.html', self.context)


@method_decorator(require_login, name='dispatch')
class SchoolManageView(View):
    context = {
        'school': None,
        'school_areas': None,
        'institutes': None,
        'departments': None,
        'grades': None,
        'years': None,
    }
    url_name = 'school_manage'

    @require_permission(url_name=url_name)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        set_menu_name(self.context, self.url_name)

        if request.session.get('school_id', None):
            self.context['school'] = School.objects.get(id=request.session['school_id'])

        # 每次管理员登录就自动更新一下数据库的学年信息
        set_system_school_year()

        if self.context['school']:
            self.context['school_areas'] = self.context['school'].school_areas.all()

        if self.context['school_areas']:
            self.context['institutes'] = self.context['school'].get_all_institutes()

        if self.context['institutes']:
            self.context['departments'] = self.context['school'].get_all_departments()

        if self.context['departments']:
            self.context['grades'] = self.context['school'].get_all_grades()

        # 用于年级选择的年份
        self.context['years'] = [x for x in range(datetime.now().year - 5, datetime.now().year + 5)]
        return render(request, 'manage/school_manage.html', self.context)


@method_decorator(require_login, name='dispatch')
class ClassesManageView(View):
    context = {
        'departments': None,
        'grades': None,
        'classes_numbers': [x for x in range(1, 9)]
    }

    url_name = 'classes_manage'

    @require_permission(url_name=url_name)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        set_menu_name(self.context, self.url_name)

        if request.session.get('school_id', None):
            school = School.objects.get(id=request.session['school_id'])
            if school:
                self.context['grades'] = school.get_all_grades()
        return render(request, 'manage/classes_manage.html', self.context)


@method_decorator(require_login, name='dispatch')
class TeacherManageView(View):
    context = {
        'departments': [],
        'teachers': [],
    }

    url_name = 'teacher_manage'

    @require_permission(url_name=url_name)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        set_menu_name(self.context, self.url_name)
        school_id = request.session.get('school_id', None)
        if school_id:
            school = School.objects.get(id=school_id)
            if school:
                self.context['departments'] = school.get_all_departments()
                if self.context['departments']:
                    self.context['teachers'] = school.get_all_teachers()
        return render(request, 'manage/teacher_manage.html', self.context)


@method_decorator(require_login, name='dispatch')
class CourseManageView(View):
    context = {
        'institutes': None,
        'classes': None,
        'teachers': None,
        'attributes': None,
    }
    url_name = 'course_manage'

    @require_permission(url_name=url_name)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        set_menu_name(self.context, self.url_name)

        school_id = request.session.get('school_id', None)
        if school_id:
            school = School.objects.get(id=school_id)
            if school:
                self.context['institutes'] = school.get_all_institutes()
                self.context['classes'] = school.get_all_classes()
                self.context['teachers'] = school.get_all_teachers()
                self.context['attributes'] = school.get_all_lab_attributes()

        return render(request, 'manage/course_manage.html', self.context)
        # return Http404('没有对应的学校信息')


@method_decorator(require_login, name='dispatch')
class LabManageView(View):
    context = {
        'institutes': [],
        'labs': [],
        'lab_attributes': [],
    }
    url_name = 'lab_manage'

    @require_permission(url_name=url_name)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        set_menu_name(self.context, self.url_name)

        school_id = request.session.get('school_id', None)
        if school_id:
            school = School.objects.get(id=school_id)
            if school:
                self.context['institutes'] = school.get_all_institutes()
                self.context['lab_attributes'] = school.get_all_lab_attributes()

        return render(request, 'manage/lab_manage.html', self.context)


@method_decorator(require_login, name='dispatch')
class LabAttributeManageView(View):
    context = {
        'lab_attributes': None,
    }
    url_name = 'lab_attribute_manage'

    @require_permission(url_name=url_name)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        set_menu_name(self.context, self.url_name)

        school_id = request.session.get('school_id', None)
        if school_id:
            school = School.objects.get(id=school_id)
            if school:
                self.context['lab_attributes'] = school.get_all_lab_attributes()

        return render(request, 'manage/lab_attribute_manage.html', self.context)


@method_decorator(require_login, name='dispatch')
class ExperimentTypeManageView(View):
    context = {}
    url_name = 'experiment_type_manage'

    @require_permission(url_name=url_name)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        set_menu_name(self.context, self.url_name)
        return render(request, 'manage/experiment_type_manage.html', self.context)


# 数据联动，选择课程后动态加载班级数据
def load_classes_of_course(request):
    classes = get_classes_name_from_course(request.GET.get('course_id'))
    return JsonResponse({'classes': classes})


# 数据联动，选择院系后动态加载教师数据
def load_teachers_of_department(request):
    department_id = request.GET.get('department_id')
    this_logger.info('选择id为' + department_id + '的系别')
    teachers = User.objects.filter(department_id=department_id)
    return render(request, 'manage/teachers_options.html', {'teachers': teachers})


# 数据联动，选择教师后动态加载课程数据
def load_courses_of_teacher(request):
    teacher_account = request.GET.get('teacher_account')
    this_logger.info('选择name为' + teacher_account + '的教师')
    temp_courses = Course.objects.filter(teachers__name=teacher_account)
    courses = []
    for course in temp_courses:
        if len(Experiment.objects.filter(course=course)) <= 0:
            courses.append(course)
    return render(request, 'manage/courses_options.html', {'courses': courses})


@method_decorator(require_login, name='dispatch')
class ApplyView(View):
    url_name = 'apply'

    @require_permission(url_name=url_name)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        context = {
            'departments': None,
            'teachers': None,
            'courses': [],
            'classes': None,

            'experiments_type': None,
            'lecture_time': None,
            'which_week': None,
            'days_of_the_week': None,
            'section': None,
            'labs_of_institute': None,
            'lab_attribute': None,
            'all_labs': None,
        }
        set_menu_name(context, self.url_name)

        temp_courses = None
        if request.session['user_type'] == MANAGER:
            manager = User.objects.get(username=request.session['user_account'])
            if manager.school:
                context['departments'] = manager.school.get_all_departments()
                if context['departments']:
                    context['teachers'] = User.objects.filter(department_id=context['departments'][0].id)
                    if context['teachers']:
                        temp_courses = Course.objects.filter(
                            teachers__username__contains=context['teachers'][0].username)
        elif request.session['user_type'] == TEACHER:
            temp_courses = Course.objects.filter(teachers__username__contains=request.session['user_account'])

        if temp_courses:
            # 实验项目为空则证明该门课没有申请过，可以显示
            for course in temp_courses:
                if len(Experiment.objects.filter(course=course)) <= 0:
                    context['courses'].append(course)

            if context['courses']:
                # 初次打开页面如果有对应课程，则根据第一门课程先提供班级数据
                context['classes'] = get_classes_name_from_course(context['courses'][0].id)

        set_choices_context(context)
        set_time_for_context(context)

        return render(request, 'manage/apply.html', context)

    def post(self, request):
        data = json.loads(list(request.POST.keys())[0])
        this_logger.info('申请管理--接收到数据：' + str(data) + '类型为：' + str(type(data)))

        context = {
            'status': True,
            'message': "",
        }

        if data['course_id'] is not '' and data['experiments']:
            # --------------------------------------------------------------处理课程开始
            this_logger.info('申请实验的课程为id:' + str(data['course_id']))

            if data['teaching_materials'] is "" and data['consume_requirements'] is "" \
                    and data['system_requirements'] is "" and data['soft_requirements'] is "":
                this_logger.info('提交的信息中没有总体需求，将不会创建总体需求实例')
            else:
                TotalRequirements.objects.create(
                    teaching_materials=data['teaching_materials'],
                    total_consume_requirements=data['consume_requirements'],
                    total_system_requirements=data['system_requirements'],
                    total_soft_requirements=data['soft_requirements'],
                    course_id=data['course_id']
                )
            # --------------------------------------------------------------处理课程结束

            # 遍历所有的实验项目并创建、存储到数据库--------------------------------------------------处理实验项目开始
            for experiment_item in data['experiments']:
                if experiment_item['section'] != "":
                    if experiment_item['section'].startswith(','):
                        experiment_item['section'] = experiment_item['section'][1:]
                        this_logger.debug("修正后的experiment_item['section']：" + experiment_item['section'])

                new_experiment = Experiment.objects.create(
                    no=experiment_item['id'],
                    name=experiment_item['experiment_name'],
                    lecture_time=experiment_item['lecture_time'],
                    which_week=experiment_item['which_week'],
                    days_of_the_week=experiment_item['days_of_the_week'],
                    section=experiment_item['section'],
                    status=1,
                    course_id=data['course_id']
                )

                try:
                    if experiment_item['experiment_type']:
                        new_experiment.experiment_type = ExperimentType.objects.get(
                            id=int(experiment_item['experiment_type']))
                except (Exception) as e:
                    context['status'] = False
                    context['message'] = '获取id为' + experiment_item['experiment_type'] + '的实验类型失败:'
                    this_logger.debug('获取id为' + experiment_item['experiment_type'] + '的实验类型失败:' + str(e))

                # 判断该实验项目是否有特殊需求
                if experiment_item['special_consume_requirements'] is "" and experiment_item[
                    'special_system_requirements'] is "" \
                        and experiment_item['special_soft_requirements'] is "":
                    this_logger.info('该实验项目没有特殊实验需求')
                else:
                    SpecialRequirements.objects.create(
                        experiment_id=new_experiment.id,
                        special_consume_requirements=experiment_item['special_consume_requirements'],
                        special_system_requirements=experiment_item['special_system_requirements'],
                        special_soft_requirements=experiment_item['special_soft_requirements']
                    )

                if experiment_item['labs'] != "":
                    lab_ids_list = str_to_non_repetitive_list(experiment_item['labs'], ',')
                    new_experiment.labs.add(*lab_ids_list)

                new_experiment.save()
            # 遍历所有的实验项目并创建、存储到数据库--------------------------------------------------处理实验项目结束
        else:
            context['status'] = False
            context['message'] = '实验项目不能为空'
        return JsonResponse(context)


@method_decorator(require_login, name='dispatch')
class ApplicationManageView(View):
    context = {
        'courses': [],
    }
    url_name = 'application_manage'

    @require_permission(url_name=url_name)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        set_menu_name(self.context, self.url_name)

        self.context['courses'] = []
        school_id = request.session.get('school_id', None)
        if school_id:
            school = School.objects.get(id=school_id)
            if school:
                all_courses = school.get_all_courses()
                if all_courses:
                    for course, i in zip(all_courses, range(0, len(all_courses))):
                        experiments_of_the_course = Experiment.objects.filter(course=course)
                        if experiments_of_the_course:
                            experiments_amount = len(experiments_of_the_course)

                            classes_name = get_classes_name_from_course(course.id)
                            teachers = get_teachers_name_from_course(course.id)

                            course_item = {
                                "id": course.id,
                                "no": i,
                                "teachers": teachers,
                                "course": course.name,
                                "experiments_amount": experiments_amount,
                                "classes": classes_name,
                                "modify_time": course.modify_time,
                                "status": STATUS['%d' % experiments_of_the_course[0].status]
                            }
                            self.context['courses'].append(course_item)
        return render(request, 'manage/application_manage.html', self.context)


@method_decorator(require_login, name='dispatch')
class ApplicationDetailsView(View):
    url_name = 'application_details'

    @require_permission(url_name=url_name)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, course_id=None):
        context = {
            'course': None,
            'experiments': None,

            'experiments_type': None,
            'lecture_time': None,
            'which_week': None,
            'days_of_the_week': None,
            'section': None,
            'all_labs': None,  # 暂时用这个代替，因为前端还做不到下拉列表数据联动
        }

        set_menu_name(context, self.url_name)

        # CourseBlock.objects.filter(course=course).delete()
        # course.has_block = False
        # course.save()

        course = Course.objects.get(id=course_id)

        experiments_origin = Experiment.objects.filter(course_id=course_id).order_by('no')
        experiments = []
        if experiments_origin:
            for experiment in experiments_origin:
                temp_experiment = {
                    'experiment': experiment,
                    'lab_ids': get_labs_id_str(experiment.labs.all()),
                    'special_requirements': SpecialRequirements.objects.filter(experiment=experiment).first(),
                }
                experiments.append(temp_experiment)

            context['experiments'] = experiments

            context['course'] = {
                'course_id': course.id,
                'term': course.term,
                'course_name': course.name,
                'teachers': get_teachers_name_from_course(course_id),
                'classes': get_classes_name_from_course(course_id),
                'modify_time': course.modify_time,
                'status': STATUS['%d' % experiments_origin[0].status],
                'total_requirements': TotalRequirements.objects.filter(course_id=course_id).first()
            }

            set_choices_context(context)
            set_time_for_context(context)

            return render(request, 'manage/application_details.html', context)
        else:
            return HttpResponseRedirect('/manage/application_manage')


def application_check(request, course_id=None, status=None):
    this_logger.info('审核:接收到course_id：' + str(course_id) + '和status：' + status)

    course = Course.objects.get(id=course_id)
    experiments = course.experiments.all()
    for experiment in experiments:
        experiment.status = status
        experiment.save()

    if status == '3':
        # 审核通过则对安排数据整理一次课程块
        if not course.has_block:
            set_course_block(course, experiments)
    else:
        if course.has_block:
            CourseBlock.objects.filter(course=course).delete()
            course.has_block = False
            course.save()

    return HttpResponseRedirect('/manage/application_manage')


def make_special_requirements_for_experiment(experiment_id, data):
    s_r_name_list = ['special_consume_requirements', 'special_system_requirements', 'special_soft_requirements']
    special_requirements_dict = {}
    for name in s_r_name_list:
        if name in data.keys():
            special_requirements_dict[name] = data[name]
    if special_requirements_dict:
        sr = SpecialRequirements.objects.filter(experiment_id=experiment_id)
        if sr:
            sr.update(**special_requirements_dict)
        else:
            SpecialRequirements.objects.create(**special_requirements_dict, experiment_id=experiment_id)


class ExperimentsView(LittleSameModelBaseView):
    # 以下是默认的参数
    model_Chinese_name = '实验项目'
    model = Experiment

    def make_return_data(self, objects):
        return_data = []
        for obj in objects:
            new_dict = {
                'id': obj.no,
                'experiment_name': obj.name,
                'hide_experiment_name': obj.name,
                'id_in_database': obj.id
            }
            return_data.append(new_dict)
        return return_data

    def get(self, request, course_id):
        return_data = []
        if course_id:
            try:
                objects = Experiment.objects.filter(course_id=course_id).order_by('no')
                return_data = self.make_return_data(objects)
            except Exception as e:
                this_logger.debug(str(e))
                raise Http404('找不到课程id为' + course_id + '的相关实验信息')
        return HttpResponse(json.dumps(return_data), content_type="application/json")

    def put(self, request, course_id):  # 修改信息
        put_data = QueryDict(request.body)
        put_data = json.loads(list(put_data.keys())[0])
        this_logger.debug(self.model_Chinese_name + '信息--接收到put数据：' + str(put_data))

        for data in put_data:
            name_list = ['name', 'experiment_type_id', 'lecture_time', 'which_week', 'days_of_the_week', 'section']

            temp_dict = {}
            for name in name_list:
                if name in data.keys():
                    temp_dict[name] = data[name]
            this_logger.debug('整理出可直接赋值的实验项目修改数据' + str(temp_dict))

            me = self.model.objects.filter(id=data['id'])
            me.update(**temp_dict)
            me = me.first()

            if 'labs' in data.keys():
                if data['labs']:
                    this_logger.debug(self.model_Chinese_name + '--labs：' + str(data['labs']))
                    lab_ids_list = str_to_non_repetitive_list(data['labs'], ',')
                    me.labs.set(lab_ids_list)
                else:
                    me.labs.clear()
            me.save()
            make_special_requirements_for_experiment(me.id, data)
        return JsonResponse({'status': True})

    def post(self, request, course_id):  # 创建信息
        post_data = json.loads(list(request.POST.keys())[0])
        this_logger.debug(self.model_Chinese_name + '信息--接收到post数据：' + str(post_data))

        for data in post_data:
            name_list = ['no', 'name', 'experiment_type_id', 'lecture_time', 'which_week', 'days_of_the_week',
                         'section']

            temp_dict = {}
            for name in name_list:
                if name in data.keys():
                    temp_dict[name] = data[name]
            this_logger.debug('整理出可直接赋值的新增实验项目数据' + str(temp_dict))

            me = self.model.objects.create(**temp_dict, course_id=course_id)

            if 'labs' in data.keys():
                if data['labs']:
                    this_logger.debug(self.model_Chinese_name + '--labs：' + str(data['labs']))
                    lab_ids_list = str_to_non_repetitive_list(data['labs'], ',')
                    me.labs.set(lab_ids_list)
                else:
                    me.labs.clear()
            me.save()
            make_special_requirements_for_experiment(me.id, data)
        return JsonResponse({'status': True})

    def delete(self, request, course_id):
        if course_id != '-1':
            this_logger.debug('删除课程id为' + course_id + '的所有实验项目')
            Experiment.objects.filter(course_id=course_id).delete()
        else:
            delete_data = QueryDict(request.body)
            delete_data = json.loads(list(delete_data.keys())[0])
            this_logger.debug(self.model_Chinese_name + '信息--接收到delete数据：' + str(delete_data))

            for id in delete_data:
                self.model.objects.filter(id=id).delete()
        return JsonResponse({'status': True})


class TotalRequirementsView(LittleSameModelBaseView):
    # 以下是默认的参数
    model_Chinese_name = '总体需求'
    model = TotalRequirements

    def make_return_data(self, objects):
        return_data = []
        for obj in objects:
            new_dict = {
                'id': obj.id,
                'course_id': obj.course.id,
                'course_name': obj.course.name,
                'teaching_materials': obj.teaching_materials,
                'total_consume_requirements': obj.total_consume_requirements,
                'total_system_requirements': obj.total_system_requirements,
                'total_soft_requirements': obj.total_soft_requirements,
                'id_in_database': obj.id
            }
            return_data.append(new_dict)
        return return_data

    def get(self, request, course_id):
        return_data = []
        if course_id:
            try:
                objects = TotalRequirements.objects.filter(course_id=course_id)
                return_data = self.make_return_data(objects)
            except Exception as e:
                this_logger.debug(str(e))
                raise Http404('找不到课程id为' + course_id + '的相关总体需求信息')
        return HttpResponse(json.dumps(return_data), content_type="application/json")

    def put(self, request, course_id):  # 修改信息
        put_data = QueryDict(request.body)
        put_data = json.loads(list(put_data.keys())[0])
        this_logger.debug(self.model_Chinese_name + '信息--接收到put数据：' + str(put_data))

        for data in put_data:
            self.model.objects.filter(id=data['id']).update(**data)
        return JsonResponse({'status': True})

    def post(self, request, course_id):  # 创建信息
        post_data = json.loads(list(request.POST.keys())[0])
        this_logger.debug(self.model_Chinese_name + '信息--接收到post数据：' + str(post_data))

        for data in post_data:
            self.model.objects.create(**data, course_id=course_id)
        return JsonResponse({'status': True})

    def delete(self, request, course_id):
        delete_data = QueryDict(request.body)
        delete_data = json.loads(list(delete_data.keys())[0])
        this_logger.debug(self.model_Chinese_name + '信息--接收到delete数据：' + str(delete_data))

        for id in delete_data:
            self.model.objects.filter(id=id).delete()
        return JsonResponse({'status': True})


def make_empty_dict(d, labs, days_of_the_week=None):
    """
    d为返回的基础空字典，星期可选，不选则显示一周
    :param d:
    :param labs:
    :param days_of_the_week:
    :return:
    """
    new_dict = {}
    for lab in labs:
        new_dict["%s" % lab.name] = ""

    def temp(d, new_dict, days_of_the_week):
        for section in range(1, 12):
            temp_dict = new_dict.copy()
            temp_dict["days_of_the_week"] = days_of_the_week
            temp_dict["section"] = section

            d["d%s_s%d" % (days_of_the_week, section)] = temp_dict

    if days_of_the_week:
        temp(d, new_dict, days_of_the_week=days_of_the_week)
    else:
        for days_of_the_week in range(1, 8):
            temp(d, new_dict, days_of_the_week)


def today_in_which_week(school_id):
    """
    请传入学校id，将返回以星期1开始计算的周次
    :param school_id:
    :return:
    """
    term = Term.objects.get(school_id=school_id)
    begin_date = term.begin_date
    begin_date_days = int(begin_date.strftime('%j'))  # 起始日期在一年中的第几天

    begin_date_is_which_day = begin_date.weekday() + 1  # 起始日期是处于星期几，1-星期一，7-星期日
    days_in_first_week = 7 - begin_date_is_which_day  # 第一周有多少天

    now_date = datetime.now().date()
    now_date_days = int(now_date.strftime('%j'))  # 今天日期在一年中的第几天

    interval_days = now_date_days - begin_date_days  # 起始日期到现在日期的间隔天数

    this_logger.debug('今天：' + str(now_date) + ' 起始日期：' + str(begin_date))
    this_logger.debug(
        '第一周天数：' + str(days_in_first_week) + ' 间隔天数：' + str(interval_days) + ' 起始日期的星期：' + str(begin_date_is_which_day))

    if interval_days <= days_in_first_week - 1:  # 包含负数，即如果用户输入的起始日期比现在日期还要靠后，则默认为第一周
        return 1
    else:
        temp = divmod((interval_days - days_in_first_week), 7)  # interval_days - days_in_first_week只会大于1
        this_logger.debug('temp:' + str(temp))
        which_week = temp[0] + 2
        if which_week > 21:  # 把周次控制在 21 周内
            which_week = 21
        return which_week


@method_decorator(require_login, name='dispatch')
class WeeksTimeTableScheduleView(View):
    def get(self, request):
        data = {
            "total": 1,
            "rows": []
        }

        selected_data = request.session.get('weeks_timetable_selected_data', None)
        if selected_data:
            labs = Lab.objects.filter(institute_id=selected_data['selected_institute_id'], dispark=True)

            # 基础空数据
            base_dict = {}
            make_empty_dict(base_dict, labs, days_of_the_week=selected_data['selected_days_of_the_week'])
            empty_row = base_dict['d%d_s1' % int(selected_data['selected_days_of_the_week'])].copy()
            empty_row["days_of_the_week"] = empty_row["section"] = ""

            div = '<div class="course_div %s">%s</div>'

            courses = Course.objects.filter(institute_id=selected_data['selected_institute_id'], has_block=True)
            temp = divmod(len(courses), len(COLOR_DIVS))
            color_divs = COLOR_DIVS * temp[0] + COLOR_DIVS[:temp[1]]

            for course, color_div in zip(courses, color_divs):
                course_blocks = CourseBlock.objects.filter(course=course, need_adjust=False, aready_arrange=True)

                for course_block in course_blocks:
                    if course_block.days_of_the_week == int(selected_data['selected_days_of_the_week']):
                        if str(selected_data['selected_which_week']) in str_to_non_repetitive_list(course_block.weeks,
                                                                                                   '、'):
                            content = '课程：' + course.name + \
                                      '<br>老师：' + get_teachers_name_from_course(course.id) + \
                                      '<br>周次：[ ' + course_block.weeks + \
                                      ' ]<br>班级：' + get_classes_name_from_course(course.id)

                            new_div = div % (color_div, content)

                            for section in course_block.sections.split(','):
                                for lab in course_block.new_labs.all():
                                    if new_div not in base_dict['d%d_s%s' % (course_block.days_of_the_week, section)][
                                        '%s' % lab.name]:
                                        base_dict['d%d_s%s' % (course_block.days_of_the_week, section)][
                                            '%s' % lab.name] = \
                                            base_dict['d%d_s%s' % (course_block.days_of_the_week, section)][
                                                '%s' % lab.name] + new_div

            data['rows'] = [empty_row] + list(base_dict.values())
        return JsonResponse(data)


@method_decorator(require_login, name='dispatch')
class WeeksTimeTableView(View):
    url_name = 'weeks_timetable'

    @require_permission(url_name=url_name)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        context = {
            'institutes': None,
            'which_week': None,
            'days_of_the_week': None,

            'labs': None,
        }
        set_menu_name(context, self.url_name)

        school_id = request.session.get('school_id', None)
        if school_id:
            school = School.objects.get(id=school_id)
            context['institutes'] = school.get_all_institutes()

        if context['institutes']:
            # 如果用户通过点击选择下拉框筛选展示条件，则通过get方式传过来
            selected_data = {}

            for name in ['selected_institute_id', 'selected_which_week', 'selected_days_of_the_week']:
                temp = request.GET.get(name, None)
                if temp:
                    selected_data[name] = temp
            this_logger.debug('周次课程表接收get数据：' + str(selected_data))

            if not selected_data:  # 没有选择数据则说明用户是第一次请求得到页面，先看看session有没有记录
                # session中如果有周次课程表的选择数据，则直接使用这些数据
                selected_data = request.session.get('weeks_timetable_selected_data', None)

                if not selected_data:  # session中没有周次课程表的选择数据，先创建一个空字典，再按用户信息生成默认选择数据
                    selected_data = {}

            if 'selected_institute_id' not in selected_data:
                if request.session['user_type'] == TEACHER:
                    teacher = User.objects.get(username=request.session['user_account'])
                    selected_data['selected_institute_id'] = teacher.department.institute_id
                elif request.session['user_type'] == STUDENT:
                    student = User.objects.get(username=request.session['user_account'])
                    selected_data['selected_institute_id'] = student.classes.grade.department.institute_id
                else:  # 不是教师不是助理，则是管理员了，默认第一个学院
                    selected_data['selected_institute_id'] = context['institutes'][0].id

            # 如果没有选择周次，则通过周次计算算法得到当前周次
            if 'selected_which_week' not in selected_data:
                selected_data['selected_which_week'] = today_in_which_week(request.session['school_id'])
                this_logger.debug('今周是这个学校的第' + str(selected_data['selected_which_week']) + '周')

            # 如果没有选择星期，则设置为当前星期
            if 'selected_days_of_the_week' not in selected_data:
                d = datetime.now().weekday() + 1
                this_logger.debug('今天是星期' + str(d))
                selected_data['selected_days_of_the_week'] = d

            # 最后将当前正在使用的选择数据存入session
            if not request.session.get('weeks_timetable_selected_data', None):
                request.session['weeks_timetable_selected_data'] = {}
            for name in ['selected_institute_id', 'selected_which_week', 'selected_days_of_the_week']:
                if name in selected_data:
                    request.session['weeks_timetable_selected_data'][name] = selected_data[name]
            this_logger.debug('最终session:' + str(request.session['weeks_timetable_selected_data']))
            request.session.modified = True

            context['labs'] = Lab.objects.filter(institute_id=selected_data['selected_institute_id'], dispark=True)
        else:
            request.session['weeks_timetable_selected_data'] = None

        set_time_for_context(context)

        return render(request, 'manage/weeks_timetable.html', context)


@method_decorator(require_login, name='dispatch')
class RoomsTimeTableScheduleView(View):
    def get(self, request):
        data = {
            "total": 1,
            "rows": []
        }

        day_of_the_week = [{'d1': '星期一'}, {'d2': '星期二'}, {'d3': '星期三'}, {'d4': '星期四'}, {'d5': '星期五'}, {'d6': '星期六'},
                           {'d7': '星期日'}, ]

        selected_data = request.session.get('rooms_timetable_selected_data', None)
        if selected_data:
            lab = Lab.objects.filter(id=selected_data['selected_room'])
            if lab:
                lab = lab.first()
                # 基础空数据
                base_dict = {}

                new_dict = {}
                for day in day_of_the_week:
                    new_dict["%s" % list(day.keys())[0]] = ""

                for section in range(1, 12):
                    temp_dict = new_dict.copy()
                    temp_dict["section"] = section
                    base_dict["s%d" % section] = temp_dict

                empty_row = base_dict['s1'].copy()
                empty_row["section"] = ""

                div = '<div class="course_div %s">%s</div>'

                courses = Course.objects.filter(institute_id=selected_data['selected_institute_id'], has_block=True)
                temp = divmod(len(courses), len(COLOR_DIVS))
                color_divs = COLOR_DIVS * temp[0] + COLOR_DIVS[:temp[1]]

                for course, color_div in zip(courses, color_divs):
                    course_blocks = CourseBlock.objects.filter(course=course, need_adjust=False, aready_arrange=True)

                    for course_block in course_blocks:
                        if str(selected_data['selected_which_week']) in str_to_non_repetitive_list(course_block.weeks,
                                                                                                   '、'):
                            if lab in course_block.new_labs.all():
                                content = '课程：' + course.name + \
                                          '<br>老师：' + get_teachers_name_from_course(course.id) + \
                                          '<br>周次：[ ' + course_block.weeks + \
                                          ' ]<br>班级：' + get_classes_name_from_course(course.id)

                                new_div = div % (color_div, content)

                                for section in course_block.sections.split(','):
                                    day = list(day_of_the_week[course_block.days_of_the_week - 1].keys())[0]
                                    if new_div not in base_dict['s%s' % section]['%s' % day]:
                                        base_dict['s%s' % section]['%s' % day] = base_dict['s%s' % section][
                                                                                     '%s' % day] + new_div

                data['rows'] = [empty_row] + list(base_dict.values())
        return JsonResponse(data)


@method_decorator(require_login, name='dispatch')
class RoomsTimeTableView(View):
    url_name = 'rooms_timetable'

    @require_permission(url_name=url_name)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        context = {
            'institutes': None,
            'which_week': [x for x in range(1, 22)],
            'labs': None,

            'day_of_the_week': [{'d1': '星期一'}, {'d2': '星期二'}, {'d3': '星期三'}, {'d4': '星期四'}, {'d5': '星期五'},
                                {'d6': '星期六'}, {'d7': '星期日'}, ]
        }
        set_menu_name(context, self.url_name)

        school_id = request.session.get('school_id', None)
        if school_id:
            school = School.objects.get(id=school_id)
            context['institutes'] = school.get_all_institutes()

        if context['institutes']:
            # 如果用户通过点击选择下拉框筛选展示条件，则通过get方式传过来
            selected_data = {}

            for name in ['selected_institute_id', 'selected_which_week', 'selected_room']:
                temp = request.GET.get(name, None)
                if temp:
                    selected_data[name] = temp
            this_logger.debug('实验室课程表接收get数据：' + str(selected_data))

            if not selected_data:  # 没有选择数据则说明用户是第一次请求得到页面，先看看session有没有记录
                # session中如果有实验室课程表的选择数据，则直接使用这些数据
                selected_data = request.session.get('rooms_timetable_selected_data', None)

                if not selected_data:  # session中没有实验室课程表的选择数据，先创建一个空字典，再按用户信息生成默认选择数据
                    selected_data = {}

            if 'selected_institute_id' not in selected_data:
                if request.session['user_type'] == TEACHER:
                    teacher = User.objects.get(username=request.session['user_account'])
                    selected_data['selected_institute_id'] = teacher.department.institute_id
                elif request.session['user_type'] == STUDENT:
                    student = User.objects.get(username=request.session['user_account'])
                    selected_data['selected_institute_id'] = student.classes.grade.department.institute_id
                else:  # 不是教师不是助理，则是管理员了，默认第一个学院
                    selected_data['selected_institute_id'] = context['institutes'][0].id

            # 如果没有选择周次，则通过周次计算算法得到当前周次
            if 'selected_which_week' not in selected_data:
                selected_data['selected_which_week'] = today_in_which_week(request.session['school_id'])
                this_logger.debug('今周是这个学校的第' + str(selected_data['selected_which_week']) + '周')

            # 如果没有选择星期，则设置为当前星期
            if 'selected_room' not in selected_data:
                d = datetime.now().weekday() + 1
                this_logger.debug('今天是星期' + str(d))
                selected_data['selected_room'] = d

            # 最后将当前正在使用的选择数据存入session
            if not request.session.get('rooms_timetable_selected_data', None):
                request.session['rooms_timetable_selected_data'] = {}
            for name in ['selected_institute_id', 'selected_which_week', 'selected_room']:
                if name in selected_data:
                    request.session['rooms_timetable_selected_data'][name] = selected_data[name]
            this_logger.debug('最终session:' + str(request.session['rooms_timetable_selected_data']))
            request.session.modified = True

            context['labs'] = Lab.objects.filter(institute_id=selected_data['selected_institute_id'], dispark=True)

        return render(request, 'manage/rooms_timetable.html', context)


def make_course_block_dict(base_dict, courses, show_need_adjust=False):
    empty_row = base_dict['d1_s1'].copy()
    empty_row["days_of_the_week"] = empty_row["section"] = ""

    div = '<div class="course_div %s">%s</div>'
    need_adjust_div = '<div class="need_adjust_div %s">%s</div>'

    temp = divmod(len(courses), len(COLOR_DIVS))
    color_divs = COLOR_DIVS * temp[0] + COLOR_DIVS[:temp[1]]

    for course, color_div in zip(courses, color_divs):
        course_blocks = CourseBlock.objects.filter(course=course)
        for course_block in course_blocks:
            content = '课程：' + course.name + \
                      '<br>老师：' + get_teachers_name_from_course(course.id) + \
                      '<br>周次：[ ' + course_block.weeks + \
                      ' ]<br>班级：' + get_classes_name_from_course(course.id)
            if show_need_adjust:
                if course_block.need_adjust:
                    new_div = need_adjust_div % (color_div, content)
                else:
                    new_div = div % (color_div, content)
            else:
                new_div = div % (color_div, content)

            for section in course_block.sections.split(','):
                for lab in course_block.new_labs.all():
                    if new_div not in base_dict['d%d_s%s' % (course_block.days_of_the_week, section)][
                        '%s' % lab.name]:
                        base_dict['d%d_s%s' % (course_block.days_of_the_week, section)]['%s' % lab.name] = \
                            base_dict['d%d_s%s' % (course_block.days_of_the_week, section)]['%s' % lab.name] + new_div

    return [empty_row] + list(base_dict.values())


# 根据实验项目的扎堆情况设置课程块，课程块根据 星期、节次和实验室 区分
def set_course_block(course, experiments):
    experiments_dict = {}
    for experiment in experiments:
        key_str = 'd%d_s%s' % (experiment.days_of_the_week, experiment.section)
        for lab in experiment.labs.all():
            key_str = key_str + '_%s' % lab.name

        if key_str not in experiments_dict.keys():
            experiments_dict[key_str] = []

        experiments_dict[key_str].append(experiment)
    # print('整理出的实验项目块：', experiments_dict)

    # 获取该课程的总班级人数
    student_sum = 0
    for classes in course.classes.all():
        student_sum = student_sum + classes.amount

    for e_key, e_value in zip(experiments_dict.keys(), experiments_dict.values()):
        course_block = CourseBlock.objects.create(
            course=course,
            days_of_the_week=int(e_key[1]),
            sections=e_key.split('_')[1][1:]
        )

        weeks = []
        for experiment in e_value:
            weeks.append(experiment.which_week)
            course_block.experiments.add(experiment)

        course_block.weeks = list_to_str(weeks, '、')

        for lab in e_value[0].labs.all():
            course_block.old_labs.add(lab)
        course_block.student_sum = student_sum
        course_block.save()

    course.has_block = True
    course.save()


@method_decorator(require_login, name='dispatch')
class ScheduleView(View):
    data = {
        "total": 1,
        "rows": []
    }

    def get(self, request):
        labs = Lab.objects.filter(institute_id=request.session.get('current_institute_id'), dispark=True)

        # 先生成一个一周内应有的星期和节次的空字典
        # 一般学校的每天都是11节对吧？
        # 该字典的格式应该为：{"d1_s1":{"days_of_the_week": days_of_the_week, "section": section, "xxx":""}, }， 键表示星期几的第几节

        # 基础空数据
        base_dict = {}
        make_empty_dict(base_dict, labs)

        courses = Course.objects.filter(institute_id=request.session.get('current_institute_id'), has_block=True)

        self.data['rows'] = make_course_block_dict(base_dict, courses, show_need_adjust=True)
        # print('整理后，前端所需要的json数据：\n', self.data['rows'])
        return JsonResponse(self.data)


# 为前端页面定制的获取课程的班级名称函数
def get_classes_name_from_course(course_id):
    all_classes_str = ''
    for classes_item in Course.objects.get(id=course_id).classes.all():
        all_classes_str = all_classes_str + '<br>' + classes_item.grade.name + '级' + classes_item.grade.department.name + classes_item.name + '班'
    return all_classes_str[4:]


# 为前端页面定制的获取课程的教师姓名函数
def get_teachers_name_from_course(course_id):
    all_teachers_str = ''
    for teacher in Course.objects.get(id=course_id).teachers.all():
        all_teachers_str = all_teachers_str + '、' + teacher.name
    return all_teachers_str[1:]


# 获取一个实验室列表的总容纳人数
def get_labs_contain_num(labs):
    contain_num = 0
    for lab in labs:
        contain_num = contain_num + lab.number_of_people
    return contain_num


def find_labs(institute_id, course_block):
    course_attribute = course_block.course.attribute
    current_attributes = ['attribute1', 'attribute2', 'attribute3']
    # 暂且按照实验室的创建来作为实验室相邻的依据
    all_labs = Lab.objects.filter(institute_id=institute_id, dispark=True)

    def judge(free_labs, lab, course_block):
        if lab_in_used(lab, course_block):
            free_labs.clear()
            return False
        else:
            free_labs.append(lab)
            if get_labs_contain_num(free_labs) >= course_block.student_sum:
                print('为课程块：', course_block, '找到实验室：', free_labs)
                return free_labs

    # 严谨模式
    for current_attribute in current_attributes:
        free_labs = []
        for lab in all_labs:
            if course_attribute:
                if getattr(lab, current_attribute) == course_attribute:
                    if judge(free_labs, lab, course_block):
                        return free_labs
                else:
                    free_labs.clear()
            else:
                print(course_block, '的课程没有属性')
                if judge(free_labs, lab, course_block):
                    return free_labs

    print('课程块：', course_block, '通过严谨模式找不到实验室，下面将通过宽松模式寻找实验室：')
    # 宽松模式
    free_labs = []
    for lab in all_labs:
        attributes = [lab.attribute1, lab.attribute2, lab.attribute3]
        if course_attribute in attributes:
            if judge(free_labs, lab, course_block):
                return free_labs
        else:
            free_labs.clear()

    print('课程块：', course_block, '通过宽松模式还是找不到实验室')
    return None


def lab_in_used(lab, course_block):
    """
    判断符合某个课程块的某个实验室是否被占用,被占用则返回其中一个冲突课程，否则返回False
    :param lab: 要判断的实验室（单个）
    :param course_block: 要对比的课程块（单个）
    :return: 被占用则返回其中一个冲突课程，否则返回False
    """
    print('为课程块', course_block, '判断实验室', lab, '是否被占用')
    for course_block_for_new in lab.course_block_for_new.all():
        # 如果星期不同，则不是占用，如果星期相同，则判断节次：
        print('判断有使用该实验室的课程块：', course_block_for_new)
        if course_block_for_new.days_of_the_week == course_block.days_of_the_week:
            print('要对比课程块', course_block_for_new, '和本身的课程块', course_block, '的星期相同')
            print('下面准备判断节次，他们的节次分别为：', course_block_for_new.sections, course_block.sections)
            its_sections = str_to_set(course_block_for_new.sections, ',')
            my_sections = str_to_set(course_block.sections, ',')
            print('节次字符串转集合后：', its_sections, my_sections)

            # 如果没交集，则不是占用，如果有交集，则判断周次：
            if its_sections.intersection(my_sections):
                print('要对比课程块', course_block_for_new, '和本身的课程块', course_block, '的节次相同')
                print('下面准备判断周次，他们的周次分别为：', course_block_for_new.weeks, course_block.weeks)
                its_weeks = str_to_set(course_block_for_new.weeks, '、')
                my_weeks = str_to_set(course_block.weeks, '、')
                print('周次字符串转集合后：', its_weeks, my_weeks)

                # 如果有交集，则是占用，如果没交集，则不是占用
                if its_weeks.intersection(my_weeks):
                    print('要对比课程块', course_block_for_new, '和本身的课程块', course_block, '的周次相同')
                    print(lab, '该实验室被占用了')
                    return course_block_for_new
    print('该实验室没有被占用')
    return False


# 用于打印课程块集合的方法
def show_course_blocks(course_blocks, tag):
    print(tag)
    for x in course_blocks:
        print('课程名称：', x, ' 人数：', x.student_sum)


def auto_arrange(institute_id, attribute1_id, attribute2_id):
    # 该学院的所有课程块
    all_course_blocks = CourseBlock.objects.filter(course__institute_id=institute_id, no_change=False)
    # 每次排课前，一定要先将所有课程块的新实验室删掉
    for course_block in all_course_blocks:
        course_block.new_labs.clear()
        course_block.save()

    # 最优先排课的课程块
    course_blocks1 = all_course_blocks.filter(course__attribute_id=attribute1_id).order_by('-student_sum')
    if attribute1_id == attribute2_id:
        course_blocks2 = []
    else:
        # 次优先排课的课程块
        course_blocks2 = all_course_blocks.filter(course__attribute_id=attribute2_id).order_by('-student_sum')

    def get_student_sum(x):
        return x.student_sum

    # 剩下的课程块
    course_blocks3 = list(set(all_course_blocks) - set(course_blocks1) - set(course_blocks2))
    course_blocks3.sort(reverse=True, key=get_student_sum)

    # 把没有属性的课程提取出来放在最后
    new_course_block3 = course_blocks3[:]
    no_attr_course_blocks = []
    for c in course_blocks3:
        if not c.course.attribute:
            no_attr_course_blocks.append(c)
            new_course_block3.remove(c)

    if no_attr_course_blocks:
        course_blocks3 = new_course_block3 + no_attr_course_blocks

    # 打印看看排课的顺序有没有出错：
    show_course_blocks(course_blocks1, '最优先排课课程块：')
    show_course_blocks(course_blocks2, '次优先排课课程块：')
    show_course_blocks(course_blocks3, '剩下的课程块：')

    for course_blocks in [course_blocks1, course_blocks2, course_blocks3]:
        for course_block in course_blocks:
            print('为课程块：', course_block, ' 寻找实验室')
            result_labs = find_labs(institute_id, course_block)
            if result_labs:
                for lab in result_labs:
                    course_block.new_labs.add(lab)
                course_block.need_adjust = False
                course_block.aready_arrange = True  # 目前计划：需要人工调整的课程都属于未编排
                # 如果新分配的实验室和需求的实验室一致，则是皆大欢喜
                if course_block.new_labs.all() == course_block.old_labs.all():
                    course_block.same_new_old = True
            else:
                course_block.need_adjust = True
                for lab in course_block.old_labs.all():
                    course_block.new_labs.add(lab)
            course_block.save()

    # 排完课后，再来个偷天换日，把不需调整、新安排实验室和申请实验室不同的课程块原来申请的实验室检查一遍是否可用，可用则换过来
    temp_course_blocks = all_course_blocks.filter(same_new_old=False, need_adjust=False)
    for course_block_item in temp_course_blocks:
        labs_can_be_used = True
        for lab_item in course_block_item.old_labs.all():
            if lab_in_used(lab_item, course_block_item):
                labs_can_be_used = False
                break
        if labs_can_be_used:
            course_block_item.new_labs.clear()
            for old_lab in course_block_item.old_labs.all():
                course_block_item.new_labs.add(old_lab)
            course_block_item.save()


@method_decorator(require_login, name='dispatch')
class ArrangeView(View):
    context = {
        'superuser': None,
        'teacher': None,
        'school': None,

        'labs': None,
        'need_adjust_course_blocks': [],
        'no_need_adjust_course_blocks': [],
        'institutes': [],
        'attributes': None,
    }
    url_name = 'arrange'

    @require_permission(url_name=url_name)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        set_menu_name(self.context, self.url_name)
        set_time_for_context(self.context)

        school_id = request.session.get('school_id', None)
        if school_id:
            self.context['school'] = School.objects.get(id=school_id)

            self.context['institutes'] = self.context['school'].get_all_institutes()
            self.context['attributes'] = LabAttribute.objects.filter(school=self.context['school'])

        if self.context['institutes']:
            # 为用户记住最近编辑的学院，要百分百确保session中包含当前学院id
            if request.GET.get('current_institute_id', None):
                request.session['current_institute_id'] = request.GET.get('current_institute_id')
            elif not request.GET.get('current_institute_id', None) and not request.session.get('current_institute_id',
                                                                                               None):
                request.session['current_institute_id'] = self.context['institutes'][0].id

            # 为用户记住当前编辑学院排课设置的属性，如果数据库中没有该学院的排课设置数据，则说明该学院没排过课
            arrange_settings = ArrangeSettings.objects.filter(institute_id=request.session['current_institute_id'])
            if arrange_settings:
                request.session['current_attribute1_id'] = arrange_settings[0].attribute1_id
                request.session['current_attribute2_id'] = arrange_settings[0].attribute2_id
            else:
                if self.context['attributes']:
                    default_current_attribute_id = self.context['attributes'][0].id
                else:
                    default_current_attribute_id = None
                request.session['current_attribute1_id'] = default_current_attribute_id
                request.session['current_attribute2_id'] = default_current_attribute_id

            request.session['arrange_settings'] = {
                'institute_%s' % request.session['current_institute_id']: {
                    'attribute1_id': request.session['current_attribute1_id'],
                    'attribute2_id': request.session['current_attribute2_id']
                }
            }

            self.context['labs'] = Lab.objects.filter(institute_id=request.session['current_institute_id'],
                                                      dispark=True)
            # 获取有课程块的课程，有课程块说明已经通过了审核
            courses = Course.objects.filter(institute_id=request.session['current_institute_id'], has_block=True)
            self.context['need_adjust_course_blocks'] = self.get_course_blocks(courses, True)
            self.context['no_need_adjust_course_blocks'] = self.get_course_blocks(courses, False)

        return render(request, 'manage/arrange.html', self.context)

    # 生成前端人工调整课程块列表的数据的方法
    def get_course_blocks(self, the_courses, need_adjust):
        blocks_list = []
        i = 0
        for course in the_courses:
            course_blocks = CourseBlock.objects.filter(course=course, need_adjust=need_adjust)
            for course_block in course_blocks:
                new_dict = {
                    "no": i,
                    "weeks": course_block.weeks.replace('、', ','),
                    "course_block": course_block,
                    "classes": get_classes_name_from_course(course_block.course.id),
                    # "labs": self.have_selected_labs_list(course_block, self.context['labs'], need_adjust)
                    "labs": self.get_labs_ids_for_course_block(course_block, need_adjust),
                }
                blocks_list.append(new_dict)
                i = i + 1
        return blocks_list

    def get_labs_ids_for_course_block(self, course_block, need_adjust):
        if need_adjust:
            old_or_new = 'old_labs'
        else:
            old_or_new = 'new_labs'
        return get_labs_id_str(getattr(course_block, old_or_new).all())

    def put(self, request):  # 更新，在这里就是执行排课的意思，更新课程表
        put_data = QueryDict(request.body)
        attribute1_id = put_data.get('attribute1_id')
        attribute2_id = put_data.get('attribute2_id')

        change = False  # change用于标记用户是否有修改排课属性，如果没修改，则不用修改session和数据库中的数据
        arrange_settings = ArrangeSettings.objects.filter(institute_id=request.session['current_institute_id'])
        if arrange_settings:
            if attribute1_id != arrange_settings[0].attribute1_id or attribute2_id != arrange_settings[0].attribute2_id:
                arrange_settings.update(attribute1_id=attribute1_id, attribute2_id=attribute2_id)
                change = True
        else:
            ArrangeSettings.objects.create(
                institute_id=request.session['current_institute_id'],
                attribute1_id=attribute1_id,
                attribute2_id=attribute2_id,
            )
            change = True

        if change:
            request.session['arrange_settings'] = {
                'institute_%s' % request.session['current_institute_id']: {
                    'attribute1_id': attribute1_id,
                    'attribute2_id': attribute2_id
                }
            }
        re_arrange = put_data.get('re_arrange')

        all_courses = Course.objects.filter(institute_id=request.session['current_institute_id'], has_block=True)

        for course in all_courses:
            if re_arrange == '1':
                CourseBlock.objects.filter(course=course).delete()
                course.has_block = False
                course.save()

                experiments = course.experiments.all()
                set_course_block(course, experiments)
            else:
                CourseBlock.objects.filter(course=course, aready_arrange=True).update(no_change=True)

        auto_arrange(request.session['current_institute_id'], attribute1_id, attribute2_id)

        return render(request, 'manage/arrange.html', self.context)


class CourseBlockView(View):
    context = {
        'status': True,
        'message': "",
    }

    def put(self, request, course_block_id):
        """
        更新课程块数据，通过request传入更新的数据即可
        :param request: request中可能存在的课程块更新数据字段：'weeks'、'days_of_the_week'、'lab_ids'
        :param course_block_id:
        :return: 返回json，包含status和message
        """
        put_data = QueryDict(request.body)
        print('接收到的数据：', put_data)
        course_block = CourseBlock.objects.filter(id=course_block_id)

        if course_block:
            course_block = course_block[0]
            temp_data = {}  # 暂存数据，用于临时存放课程块原来的数据

            change = False
            if 'weeks' in put_data.keys():
                weeks = non_repetitive_strlist(put_data['weeks'][0], ',').replace(',', '、')
                this_logger.info('修改后的所有周次去重后的转化出来的字符串：' + weeks)
                if weeks != course_block.weeks:
                    temp_data['weeks'] = course_block.weeks
                    course_block.weeks = weeks
                    change = True

            if 'days_of_the_week' in put_data.keys():
                if put_data['days_of_the_week'][0] != course_block.days_of_the_week:
                    temp_data['days_of_the_week'] = course_block.days_of_the_week
                    course_block.days_of_the_week = int(put_data['days_of_the_week'][0])
                    change = True

            old_lab_ids = get_model_field_ids(course_block, 'old_labs')
            if 'lab_ids' in put_data.keys():
                lab_ids = non_repetitive_strlist(put_data['lab_ids'][0], ',')
                print('用户提交的实验室id列表：', lab_ids, type(lab_ids), ' 课程块的实验室id列表：', old_lab_ids)

                if lab_ids != old_lab_ids:
                    temp_data['lab_ids'] = old_lab_ids
                    change = True
            else:
                # 如果用户没有申请新的实验室，而如果下面change=True，则说明用户修改了时间，
                # 所以要检查新时间下原来的实验室是否还可用
                lab_ids = old_lab_ids

            print('暂存数据：', temp_data)

            if change:
                # 课程块原来在数据库内的新实验室不能丢，因为判断实验室是否可用的算法是会判断自身课程的。。这个以后得改进
                # 但现在的作用很大，用于在实验室获取不成功时还原数据
                temp_data['course_block_new_labs'] = [lab for lab in course_block.new_labs.all()]
                course_block.new_labs.clear()
                course_block.save()  # 如果有数据改变，则暂时更新一下课程的数据，然后通过检查新申请的实验室是否可用

                lab_in_used_return = False
                for lab_id in lab_ids:
                    lab = Lab.objects.get(id=int(lab_id))
                    # 只要有一个实验室被占用都不可以为这个课程块设置新的实验室
                    lab_in_used_return = lab_in_used(lab, course_block)
                    if lab_in_used_return:
                        break
                if not lab_in_used_return:
                    # 如果新申请的实验室都可用，则课程块的新实验室数据更新即可，
                    # 同时设置不需人工调整了，时间信息由于在上面已经更新，所以不用变
                    course_block.new_labs.add(*lab_ids)
                    course_block.need_adjust = False
                    course_block.aready_arrange = True
                    course_block.save()

                    self.context['status'] = True
                    self.context['message'] = ""
                else:
                    # 如果新申请的实验室不满足条件，就要将这个课程块通过暂存数据恢复课程块原来的信息
                    if 'weeks' in temp_data.keys():
                        course_block.weeks = temp_data['weeks']
                    if 'days_of_the_week' in temp_data.keys():
                        course_block.days_of_the_week = temp_data['days_of_the_week']

                    course_block.new_labs.clear()
                    for lab in temp_data['course_block_new_labs']:
                        course_block.new_labs.add(lab)

                    course_block.aready_arrange = False
                    course_block.save()

                    self.context['status'] = False
                    self.context['message'] = '课程：《' + lab_in_used_return.course.name + '》与其冲突，请将其移走再修改本课程'
        else:
            self.context['status'] = False
            self.context['message'] = '传入的课程块id有误，请重新提交'

        return JsonResponse(self.context)
