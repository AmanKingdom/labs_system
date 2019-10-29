import json
from datetime import datetime
from functools import wraps

from django.http import JsonResponse, HttpResponseRedirect, QueryDict, Http404, HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View

from apps.manage.models import School, SchoolArea, Institute, Department, Grade, SuperUser, Classes, Teacher, \
    SchoolYear, Term, Course, LabsAttribute, Lab, Experiment, ExperimentType, CourseBlock, ArrangeSettings

from logging_setting import ThisLogger
from manage.tools.list_tool import get_model_field_ids
from manage.tools.setting_tool import set_time_for_context, set_system_school_year
from manage.tools.string_tool import list_to_str, str_to_set, get_labs_id_str, non_repetitive_strlist, \
    str_to_non_repetitive_list

this_logger = ThisLogger().logger

STATUS = {
    '1': '已提交待审核',
    '2': '审核不通过',
    '3': '审核通过'
}

# 设计13个可用的课程块背景颜色
COLOR_DIVS = ['color1_div','color2_div','color3_div','color4_div','color5_div','color6_div',
              'color7_div','color8_div','color9_div','color10_div','color11_div','color12_div','color13_div']


# 验证登录视图
def require_login(view):
    @wraps(view)
    def new_view(request, *args, **kwargs):
        if request.session.get('user_account', None):
            this_logger.debug('验证登录视图：' + request.session['user_name'] + ' 用户已登录')
            return view(request, *args, **kwargs)
        return HttpResponseRedirect('/browse/login')
    return new_view


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

    def post(self, request):    # 创建学校
        school_name = request.POST.get('school_name', None)
        if school_name:
            if School.objects.filter(name=school_name):
                this_logger.debug('已存在学校：' + school_name)
                return JsonResponse({'status': False, 'message': '该学校名称已经被人注册'})
            else:
                school = School.objects.create(name=school_name)
                try:
                    superuser = SuperUser.objects.get(account=request.session.get('user_account', None))
                    superuser.school = school
                    superuser.save()
                    request.session['school_id'] = superuser.school_id
                    # 创建一个学校的同时应该创建一个默认的学期给它
                    create_default_term_for_school(school)
                    return JsonResponse({'status': True})
                except SuperUser.DoesNotExist:
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
    context = {
        'title': '系统设置',
        'system_settings_active': True,  # 激活导航

        'school_year': None,
        'term': None,
    }

    def get(self, request):
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
            this_logger.debug('term_name:'+ term_name+ '，begin_date:' + begin_date)
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
                raise Http404('找不到学校id为'+school_id+'的相关信息')
        # 这里的content_type="application/json"其实可有可无
        return HttpResponse(json.dumps(return_data), content_type="application/json")

    def put(self, request, school_id):     # 修改信息
        put_data = QueryDict(request.body)
        put_data = json.loads(list(put_data.keys())[0])
        this_logger.debug(self.model_Chinese_name + '信息--接收到put数据：' + str(put_data))

        for data in put_data:
            self.model.objects.filter(id=data['id']).update(**data)
        return JsonResponse({'status': True})

    def post(self, request, school_id):       # 创建信息
        post_data = json.loads(list(request.POST.keys())[0])
        this_logger.debug(self.model_Chinese_name + '信息--接收到post数据：' + str(post_data))

        for data in post_data:
            if self.model is SchoolArea or self.model is LabsAttribute:
                self.model.objects.create(**data, school_id=school_id)
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
    model = Teacher
    get_all_what_func_name = 'get_all_teachers'

    def make_return_data(self, objects):
        return_data = []
        for obj, i in zip(objects, range(0, len(objects))):
            new_dict = {
                'id': i,
                'department': obj.department_id,
                'hide_department_id': obj.department_id,
                'teacher_name': obj.name,
                'hide_teacher_name': obj.name,
                'account': obj.account,
                'hide_account': obj.account,
                'password': obj.password,
                'hide_password': obj.password,
                'phone': obj.phone,
                'hide_phone': obj.phone,
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

    def put(self, request, school_id):     # 修改信息
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
                me.attribute = LabsAttribute.objects.get(id=data['attribute'])
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

    def post(self, request, school_id):       # 创建信息
        post_data = json.loads(list(request.POST.keys())[0])
        this_logger.debug(self.model_Chinese_name + '信息--接收到post数据：' + str(post_data))

        term = Term.objects.get(school_id=school_id)

        for data in post_data:
            me = self.model.objects.create(institute_id=data['institute_id'], name=data['name'], term=term)
            if 'attribute' in data.keys():
                me.attribute = LabsAttribute.objects.get(id=data['attribute'])
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





class LabAttributesView(LittleSameModelBaseView):
    model_Chinese_name = '实验室属性'
    model = LabsAttribute
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


# 个人主页
def personal_info(request):
    context = {
        'title': '个人主页',
        'personal_info_active': True,  # 激活导航
        'superuser': None,
        'teacher': None,

        'course_amount': None,
        'departments': [],
        'term': None,
    }

    if request.session.get('school_id', None):
        context['departments'] = School.objects.get(id=request.session['school_id']).get_all_departments()

    return render(request, 'manage/personal_info.html', context)


@method_decorator(require_login, name='dispatch')
class SchoolManageView(View):
    context = {
        'title': '学校管理',
        'active_1': True,  # 激活导航
        'school_active': True,  # 激活导航

        'school': None,
        'school_areas': None,
        'institutes': None,
        'departments': None,
        'grades': None,
        'years': None,
    }

    def get(self, request):
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
        'title': '班级管理',
        'active_1': True,  # 激活导航
        'classes_active': True,  # 激活导航

        'departments': None,
        'grades': None,
        'classes_numbers': [x for x in range(1, 9)]
    }

    def get(self, request):
        if request.session.get('school_id', None):
            school = School.objects.get(id=request.session['school_id'])
            if school:
                    self.context['grades'] = school.get_all_grades()
        return render(request, 'manage/classes_manage.html', self.context)


@method_decorator(require_login, name='dispatch')
class TeacherManageView(View):
    context = {
        'title': '教师管理',
        'active_1': True,  # 激活导航
        'teacher_active': True,  # 激活导航

        'departments': [],
        'teachers': [],
    }

    def get(self, request):
        school = School.objects.get(id=request.session['school_id'])
        if school:
            self.context['departments'] = school.get_all_departments()
            if self.context['departments']:
                self.context['teachers'] = school.get_all_teachers()
        return render(request, 'manage/teacher_manage.html', self.context)


@method_decorator(require_login, name='dispatch')
class CourseManageView(View):
    context = {
        'title': '课程管理',
        'active_1': True,  # 激活导航
        'course_active': True,  # 激活导航

        'institutes': None,
        'classes': None,
        'teachers': None,
        'attributes': None,
    }

    def get(self, request):
        school = School.objects.get(id=request.session['school_id'])
        if school:
            self.context['institutes'] = school.get_all_institutes()
            self.context['classes'] = school.get_all_classes()
            self.context['teachers'] = school.get_all_teachers()
            self.context['attributes'] = school.labs_attributes.all()

            return render(request, 'manage/course_manage.html', self.context)


@method_decorator(require_login, name='dispatch')
class LabAttributeManageView(View):
    context = {
        'title': '实验室属性管理',
        'active_2': True,  # 激活导航
        'labs_attribute_active': True,  # 激活导航

        'labs_attributes': None,
    }

    def get(self, request):
        school = School.objects.get(id=request.session['school_id'])
        if school:
            self.context['labs_attributes'] = school.get_all_lab_attributes()

        return render(request, 'manage/labs_attribute_manage.html', self.context)


def experiment_type_manage(request):
    context = {
        'title': '实验类型设置',
        'active_3': True,  # 激活导航
        'experiment_type_active': True,  # 激活导航
        'superuser': None,
        'teacher': None,

        'experiment_types': None,
    }

    if context['superuser'].school:
        context['experiment_types'] = context['superuser'].school.experiment_types.all()

    return render(request, 'manage/experiment_type_manage.html', context)


def lab_manage(request):
    context = {
        'title': '实验室管理',
        'active_2': True,  # 激活导航
        'lab_active': True,  # 激活导航
        'superuser': None,
        'teacher': None,

        'institutes': [],
        'labs': [],
        'labs_attributes': [],
    }


    school = context['superuser'].school
    if school:
        context['labs_attributes'] = school.labs_attributes.all()

    return render(request, 'manage/lab_manage.html', context)


def application_manage(request):
    context = {
        'title': '实验申请表审批',
        'active_3': True,  # 激活导航
        'application_active': True,  # 激活导航
        'superuser': None,
        'teacher': None,

        'courses': [],
    }

    # if all_courses:
    #     i = 1
    #     for course in all_courses:
    #         experiments_of_the_course = Experiment.objects.filter(course=course)
    #         if experiments_of_the_course:
    #             experiments_amount = len(experiments_of_the_course)
    #
    #             classes_name = ""
    #             for class_item in course.classes.all():
    #                 classes_name = classes_name + '<br>' + class_item.grade.name + "级" + class_item.grade.department.name + str(
    #                     class_item.name)
    #
    #             teaching_materials = ""
    #             if course.total_requirements:
    #                 teaching_materials = course.total_requirements.teaching_materials
    #
    #             # 或许不止一个老师上一门课
    #             teachers = ""
    #             for teacher in course.teachers.all():
    #                 teachers = teachers + ',' + teacher.name
    #
    #             course_item = {
    #                 "id": course.id,
    #                 "no": i,
    #                 "teachers": teachers[1:],
    #                 "term": course.term if course.term else "",
    #                 "course": course.name,
    #                 "teaching_materials": teaching_materials,
    #                 "experiments_amount": experiments_amount,
    #                 "classes": classes_name[4:],
    #                 "create_time": course.modify_time,
    #                 "status": STATUS['%d' % experiments_of_the_course[0].status]
    #             }
    #             context['courses'].append(course_item)
    #             i = i + 1

    return render(request, 'manage/application_manage.html', context)


# 如果传入的旧名称和新名称一样就是要创建新学校
def create_or_modify_school_ajax(request):
    data = json.loads(list(request.POST.keys())[0])

    context = {
        'status': True,
        'message': None,
    }
    if request.is_ajax():
        old_school_name = data['old_school_name']
        new_school_name = data['new_school_name']

        if old_school_name and new_school_name:
            this_logger.info('接收到old_school_name:' + old_school_name + ' new_school_name:' + new_school_name)
            if old_school_name == new_school_name:
                s = School.objects.create(name=new_school_name)
                superuser = SuperUser.objects.filter(account=request.session['user_account'])
                superuser.update(school=s)
                # 创建一个学校的同时应该创建一个默认的学年学期给它
                create_default_term_for_school(s)
            else:
                school = School.objects.filter(name=old_school_name)
                school.update(name=new_school_name)
        else:
            context['status'] = False
            context['message'] = '传入参数为空'
        return JsonResponse(context)


def remove_ajax(request):
    data = json.loads(list(request.POST.keys())[0])

    context = {
        'status': True,
        'message': None,
    }
    if request.is_ajax():
        remove_ids = data['remove_ids']
        this_logger.info('接收到remove_ids:' + str(remove_ids) + '类型为：' + str(type(remove_ids)) +
                         ' 删除对象模型为：' + data['remove_objects_model'])

        try:
            for id in remove_ids:
                if data['remove_objects_model'] == 'school_areas':
                    SchoolArea.objects.get(id=id).delete()
                elif data['remove_objects_model'] == 'institutes':
                    Institute.objects.get(id=id).delete()
                elif data['remove_objects_model'] == 'departments':
                    Department.objects.get(id=id).delete()
                elif data['remove_objects_model'] == 'grades':
                    Grade.objects.get(id=id).delete()
                elif data['remove_objects_model'] == 'classes':
                    Classes.objects.get(id=id).delete()
                elif data['remove_objects_model'] == 'teachers':
                    Teacher.objects.get(id=id).delete()
                elif data['remove_objects_model'] == 'courses':
                    Course.objects.get(id=id).delete()
                elif data['remove_objects_model'] == 'labs_attributes':
                    LabsAttribute.objects.get(id=id).delete()
                elif data['remove_objects_model'] == 'experiment_types':
                    ExperimentType.objects.get(id=id).delete()
                elif data['remove_objects_model'] == 'labs':
                    Lab.objects.get(id=id).delete()

        except:
            context['status'] = False
            context['message'] = '删除失败，请重试'

        return JsonResponse(context)


def save_ajax(request):
    data = json.loads(list(request.POST.keys())[0])

    context = {
        'status': True,
        'message': None,
    }

    if request.is_ajax():

        save_objects_data = data['save_objects_data']
        school_id = data['school_id']
        print('save_objects_data：', save_objects_data, 'school_id：', school_id)

        # 删除情况
        if data['delete_ids_in_database']:
            this_logger.info('将要删除：' + str(data['delete_ids_in_database']))

            for id in data['delete_ids_in_database']:
                if data['save_objects_model'] == 'school_areas':
                    SchoolArea.objects.get(id=id).delete()
                elif data['save_objects_model'] == 'institutes':
                    Institute.objects.get(id=id).delete()
                elif data['save_objects_model'] == 'departments':
                    Department.objects.get(id=id).delete()
                elif data['save_objects_model'] == 'grades':
                    Grade.objects.get(id=id).delete()
                elif data['save_objects_model'] == 'classes':
                    Classes.objects.get(id=id).delete()
                elif data['save_objects_model'] == 'teachers':
                    Teacher.objects.get(id=id).delete()
                elif data['save_objects_model'] == 'courses':
                    Course.objects.get(id=id).delete()
                elif data['save_objects_model'] == 'labs_attributes':
                    LabsAttribute.objects.get(id=id).delete()
                elif data['save_objects_model'] == 'experiment_types':
                    ExperimentType.objects.get(id=id).delete()
                elif data['save_objects_model'] == 'labs':
                    Lab.objects.get(id=id).delete()

        # try:
        for save_object in save_objects_data:
            if 'id_in_database' in save_object.keys():
                # 修改情况
                if data['save_objects_model'] == 'school_areas':
                    s = SchoolArea.objects.filter(id=int(save_object['id_in_database']))
                    s.update(name=save_object['school_area_name'])
                elif data['save_objects_model'] == 'institutes':
                    i = Institute.objects.filter(id=int(save_object['id_in_database']))
                    i.update(name=save_object['institute_name'],
                             school_area=SchoolArea.objects.get(id=save_object['school_area']))
                elif data['save_objects_model'] == 'departments':
                    d = Department.objects.filter(id=int(save_object['id_in_database']))
                    d.update(name=save_object['department_name'],
                             institute=Institute.objects.get(id=save_object['institute']))
                elif data['save_objects_model'] == 'grades':
                    g = Grade.objects.filter(id=int(save_object['id_in_database']))
                    g.update(name=save_object['grade_name'],
                             department=Department.objects.get(id=save_object['department']))
                elif data['save_objects_model'] == 'classes':
                    c = Classes.objects.filter(id=int(save_object['id_in_database']))
                    c.update(name=save_object['classes_name'],
                             grade=Grade.objects.get(id=save_object['grade']))
                elif data['save_objects_model'] == 'teachers':
                    t = Teacher.objects.filter(id=int(save_object['id_in_database']))
                    t.update(name=save_object['teacher_name'],
                             account=save_object['account'],
                             password=save_object['password'],
                             phone=save_object['phone'],
                             department=Department.objects.get(id=save_object['department']))
                elif data['save_objects_model'] == 'courses':
                    term = Term.objects.filter(
                        school=SuperUser.objects.get(account=request.session.get('user_account')).school)[0]
                    c = Course.objects.filter(id=int(save_object['id_in_database']))
                    c.update(name=save_object['course_name'],
                             institute=Institute.objects.get(id=save_object['institute']),
                             term=term)
                    if save_object['attribute']:
                        c.update(attribute=LabsAttribute.objects.get(id=save_object['attribute']))
                    add_teachers_classes_to_course(c[0], save_object)
                elif data['save_objects_model'] == 'labs_attributes':
                    l = LabsAttribute.objects.filter(id=int(save_object['id_in_database']))
                    l.update(name=save_object['labs_attribute_name'])
                elif data['save_objects_model'] == 'experiment_types':
                    et = ExperimentType.objects.filter(id=int(save_object['id_in_database']))
                    et.update(name=save_object['experiment_type_name'])
                elif data['save_objects_model'] == 'labs':
                    lab = Lab.objects.filter(id=int(save_object['id_in_database']))
                    if str(save_object['dispark']) == '1':
                        dispark = True
                    else:
                        dispark = False
                    lab.update(name=save_object['lab_name'],
                               institute=Institute.objects.get(id=save_object['institute']),
                               number_of_people=save_object['number_of_people'],
                               dispark=dispark,
                               equipments=save_object['equipments'])
                    set_attribute_for_lab(lab[0], save_object)

            else:
                # 创建情况
                if data['save_objects_model'] == 'school_areas':
                    SchoolArea.objects.create(name=save_object['school_area_name'],
                                              school=School.objects.get(id=school_id))
                elif data['save_objects_model'] == 'institutes':
                    Institute.objects.create(name=save_object['institute_name'],
                                             school_area=SchoolArea.objects.get(id=save_object['school_area']))
                elif data['save_objects_model'] == 'departments':
                    Department.objects.create(name=save_object['department_name'],
                                              institute=Institute.objects.get(id=save_object['institute']))
                elif data['save_objects_model'] == 'grades':
                    Grade.objects.create(name=save_object['grade_name'],
                                         department=Department.objects.get(id=save_object['department']))
                elif data['save_objects_model'] == 'classes':
                    Classes.objects.create(name=save_object['classes_name'],
                                           grade=Grade.objects.get(id=save_object['grade']))
                elif data['save_objects_model'] == 'teachers':
                    Teacher.objects.create(name=save_object['teacher_name'],
                                           account=save_object['account'],
                                           password=save_object['password'],
                                           phone=save_object['phone'],
                                           department=Department.objects.get(id=save_object['department']))
                elif data['save_objects_model'] == 'courses':
                    term = Term.objects.filter(
                        school=SuperUser.objects.get(account=request.session.get('user_account')).school)[0]
                    c = Course.objects.create(name=save_object['course_name'],
                                              institute=Institute.objects.get(id=save_object['institute']),
                                              term=term)
                    if save_object['attribute']:
                        c.attribute = LabsAttribute.objects.get(id=save_object['attribute'])
                        c.save()
                    add_teachers_classes_to_course(c, save_object)
                elif data['save_objects_model'] == 'labs_attributes':
                    LabsAttribute.objects.create(name=save_object['labs_attribute_name'],
                                                 school=SuperUser.objects.get(
                                                     account=request.session.get('user_account')).school)
                elif data['save_objects_model'] == 'experiment_types':
                    ExperimentType.objects.create(name=save_object['experiment_type_name'],
                                                  school=SuperUser.objects.get(
                                                      account=request.session.get('user_account')).school)
                elif data['save_objects_model'] == 'labs':
                    if str(save_object['dispark']) == '1':
                        dispark = True
                    else:
                        dispark = False
                    lab = Lab.objects.create(name=save_object['lab_name'],
                                             institute=Institute.objects.get(id=save_object['institute']),
                                             number_of_people=save_object['number_of_people'],
                                             dispark=dispark,
                                             equipments=save_object['equipments'])
                    set_attribute_for_lab(lab, save_object)

            # except:
            #     context['status'] = False
            #     context['message'] = '修改失败，请重试'

        return JsonResponse(context)


def set_attribute_for_lab(lab, save_object):
    if save_object['attribute1'] != "":
        lab.attribute1 = LabsAttribute.objects.get(id=save_object['attribute1'])
    if save_object['attribute2'] != "":
        lab.attribute2 = LabsAttribute.objects.get(id=save_object['attribute2'])
    if save_object['attribute3'] != "":
        lab.attribute3 = LabsAttribute.objects.get(id=save_object['attribute3'])
    lab.save()


def add_teachers_classes_to_course(course, save_object):
    classes_ids = make_ids(str(save_object['classes']))

    for classes_id in classes_ids:
        if classes_id:
            course.classes.add(Classes.objects.get(id=classes_id))

    teachers_ids = make_ids(str(save_object['teachers']))

    for teacher_id in teachers_ids:
        if teacher_id:
            course.teachers.add(Teacher.objects.get(id=teacher_id))


# 整理ids
def make_ids(ids):
    if ids.startswith(','):
        ids = ids[1:]
    return ids.split(',')


def become_a_teacher(request):
    data = json.loads(list(request.POST.keys())[0])

    context = {
        'status': True,
        'message': None,
    }

    if request.is_ajax():
        try:
            from_department_id = data['from_department_id']
            superuser = SuperUser.objects.get(account=request.session['user_account'])
            teacher = Teacher.objects.create(department_id=from_department_id,
                                             name=superuser.name,
                                             account=superuser.account,
                                             password=superuser.password,
                                             phone=superuser.account)
            superuser.is_teacher = teacher
            superuser.save()

        except:
            context['status'] = False
            context['message'] = '修改失败，请重试'

        return JsonResponse(context)


def cancel_the_teacher(request):
    data = json.loads(list(request.POST.keys())[0])

    context = {
        'status': True,
        'message': None,
    }

    if request.is_ajax():
        try:
            SuperUser.objects.filter(id=data['superuser_id'])[0].is_teacher.delete()

        except:
            context['status'] = False
            context['message'] = '修改失败，请重试'

        return JsonResponse(context)
















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

        new_dict = {}
        for lab in labs:
            new_dict["%s" % lab.name] = ""

        for days_of_the_week in range(1, 8):
            for section in range(1, 12):
                temp_dict = new_dict.copy()
                temp_dict["days_of_the_week"] = days_of_the_week
                temp_dict["section"] = section

                base_dict["d%s_s%d" % (days_of_the_week, section)] = temp_dict
        empty_row = base_dict['d1_s1'].copy()
        empty_row["days_of_the_week"] = empty_row["section"] = ""

        div = '<div class="course_div %s">%s</div>'
        need_adjust_div = '<div class="need_adjust_div %s">%s</div>'

        courses = Course.objects.filter(institute_id=request.session.get('current_institute_id'), has_block=True)

        temp = divmod(len(courses), len(COLOR_DIVS))
        color_divs = COLOR_DIVS * temp[0] + COLOR_DIVS[:temp[1]]

        for course, color_div in zip(courses, color_divs):
            course_blocks = CourseBlock.objects.filter(course=course)
            for course_block in course_blocks:
                content = '课程：' + course.name + \
                          '<br>老师：' + get_teachers_name_from_course(course.id) + \
                          '<br>周次：[ ' + course_block.weeks + \
                          ' ]<br>班级：' + get_classes_name_from_course(course.id)
                if course_block.need_adjust:
                    new_div = need_adjust_div % (color_div, content)
                else:
                    new_div = div % (color_div, content)

                for section in course_block.sections.split(','):
                    for lab in course_block.new_labs.all():
                        if new_div not in base_dict['d%d_s%s' % (course_block.days_of_the_week, section)]['%s' % lab.name]:
                            base_dict['d%d_s%s' % (course_block.days_of_the_week, section)]['%s' % lab.name] = base_dict['d%d_s%s' % (course_block.days_of_the_week, section)]['%s' % lab.name] + new_div

        self.data['rows'] = [empty_row] + list(base_dict.values())
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


class ArrangeView(View):
    context = {
        'title': '智能排课',
        'active_3': True,  # 激活导航
        'arrange_active': True,  # 激活导航

        'superuser': None,
        'teacher': None,
        'school': None,

        'labs': None,
        'need_adjust_course_blocks': [],
        'no_need_adjust_course_blocks': [],
        'institutes': [],
        'attributes': None,
    }

    def get(self, request):
        set_time_for_context(self.context)

        self.context['institutes'] = self.context['school'].get_all_institutes()
        self.context['attributes'] = LabsAttribute.objects.filter(school=self.context['school'])

        # 为用户记住最近编辑的学院，要百分百确保session中包含当前学院id
        if request.GET.get('current_institute_id', None):
            request.session['current_institute_id'] = request.GET.get('current_institute_id')
        elif not request.GET.get('current_institute_id', None) and not request.session.get('current_institute_id', None):
            request.session['current_institute_id'] = self.context['institutes'][0].id

        # 为用户记住当前编辑学院排课设置的属性，如果数据库中没有该学院的排课设置数据，则说明该学院没排过课
        arrange_settings = ArrangeSettings.objects.filter(institute_id=request.session['current_institute_id'])
        if arrange_settings:
            request.session['current_attribute1_id'] = arrange_settings[0].attribute1_id
            request.session['current_attribute2_id'] = arrange_settings[0].attribute2_id
        else:
            request.session['current_attribute1_id'] = self.context['attributes'][0].id
            request.session['current_attribute2_id'] = self.context['attributes'][0].id

        request.session['arrange_settings'] = {
            'institute_%s' % request.session['current_institute_id']: {
                'attribute1_id': request.session['current_attribute1_id'],
                'attribute2_id': request.session['current_attribute2_id']
            }
        }

        self.context['labs'] = Lab.objects.filter(institute_id=request.session['current_institute_id'], dispark=True)
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
                this_logger.info('修改后的所有周次去重后的转化出来的字符串：'+weeks)
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
                course_block.save()     # 如果有数据改变，则暂时更新一下课程的数据，然后通过检查新申请的实验室是否可用

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
