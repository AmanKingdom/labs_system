import json
import apps.manage.models as models
from datetime import datetime

from django.http import JsonResponse, HttpResponseRedirect, QueryDict
from django.shortcuts import render
from django.views import View

from apps.manage.models import School, SchoolArea, Institute, Department, Grade, SuperUser, Classes, Teacher, \
    SchoolYear, Term, Course, LabsAttribute, Lab, Experiment, ExperimentType, CourseBlock, ArrangeSettings

from logging_setting import ThisLogger
from manage.tools.setting_tool import set_time_for_context
from manage.tools.string_tool import list_to_str, str_to_set, get_labs_id_str, non_repetitive_strlist

this_logger = ThisLogger().logger

STATUS = {
    '1': '已提交待审核',
    '2': '审核不通过',
    '3': '审核通过'
}

# 设计13个可用的课程块背景颜色
COLOR_DIVS = ['color1_div','color2_div','color3_div','color4_div','color5_div','color6_div',
              'color7_div','color8_div','color9_div','color10_div','color11_div','color12_div','color13_div']


# 设置本系统的唯一学年，当当前月份为8月份时，如果有超级管理员登录本系统，即可更新数据库的学年表的唯一一条学年数据
def set_system_school_year():
    year_now = datetime.now().year
    school_year = SchoolYear.objects.all()
    if school_year:
        school_year = school_year[0]
        # 如果是一年中的八月份之后，则学年的起始年份为当前年份，否则学年的结束年份为当前年份
        # 而是否需要对数据库进行修改，则根据这条学年数据是否符合以上所述情况
        if 7 < datetime.now().month:
            if school_year.since != year_now:
                # 学年的起始年份不是当前年份，需要更新
                SchoolYear.objects.filter(id=school_year.id).update(since=year_now, to=year_now + 1)
        else:
            if school_year.to != year_now:
                # 学年的结束年份不是当前年份，需要更新
                SchoolYear.objects.filter(id=school_year.id).update(since=year_now - 1, to=year_now)
    else:
        SchoolYear.objects.create(since=year_now, to=year_now + 1)


def set_user_for_context(user_account, context):
    context['superuser'] = SuperUser.objects.filter(account=user_account)
    if context['superuser']:
        context['superuser'] = context['superuser'][0]
        context['teacher'] = context['superuser'].is_teacher
        if context['superuser'].school:
            context['school'] = context['superuser'].school
        if context['teacher']:
            return 'superuser_is_teacher'
        else:
            return 'superuser'
    else:
        context['teacher'] = Teacher.objects.filter(account=user_account)
        if context['teacher']:
            context['teacher'] = context['teacher'][0]
            return 'teacher'
        else:
            return None


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


def get_all_school_areas(school):
    if school:
        return school.school_areas.all()


def get_all_institutes(school):
    institutes = []
    school_areas = get_all_school_areas(school)
    if school_areas:
        for school_area in school_areas:
            if school_area:
                temp_institutes = school_area.institutes.all()
                for institute in temp_institutes:
                    if institute:
                        institutes.append(institute)
    return institutes


def get_all_departments(school):
    departments = []
    institutes = get_all_institutes(school)
    if institutes:
        for institute in institutes:
            if institute:
                temp_departments = institute.departments.all()
                for department in temp_departments:
                    if department:
                        departments.append(department)
    return departments


def get_all_grades(school):
    grades = []
    departments = get_all_departments(school)
    if departments:
        for department in departments:
            if department:
                temp_grades = department.grades.all()
                for grade in temp_grades:
                    if grade:
                        grades.append(grade)
    return grades


def get_all_classes(school):
    classes = []
    grades = get_all_grades(school)
    if grades:
        for grade in grades:
            if grade:
                temp_classes = grade.classes.all()
                for classes_item in temp_classes:
                    if classes_item:
                        classes.append(classes_item)
    return classes


def get_all_teachers(school):
    teachers = []
    departments = get_all_departments(school)
    if departments:
        for department in departments:
            if department:
                temp_teachers = department.teachers.all()
                for teacher in temp_teachers:
                    if teacher:
                        teachers.append(teacher)
    return teachers


def get_all_courses(school):
    courses = []
    institutes = get_all_institutes(school)
    if institutes:
        for institute in institutes:
            if institute:
                temp_courses = institute.courses.all()
                for course in temp_courses:
                    if course:
                        courses.append(course)
    return courses


def get_all_labs(school):
    labs = []
    institutes = get_all_institutes(school)
    if institutes:
        for institute in institutes:
            if institute:
                temp_labs = institute.labs.all()
                for lab in temp_labs:
                    if lab:
                        labs.append(lab)
    return labs


def get_all_labs_dispark(school):
    labs = []
    institutes = get_all_institutes(school)
    if institutes:
        for institute in institutes:
            if institute:
                temp_labs = institute.labs.all()
                for lab in temp_labs:
                    if lab:
                        if lab.dispark:
                            labs.append(lab)
    return labs


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

    user = set_user_for_context(request.session['user_account'], context)
    if user == 'superuser_is_teacher' or user == 'teacher':
        context['course_amount'] = len(Course.objects.filter(teachers__account=context['teacher'].account))
        context['term'] = Term.objects.filter(school=context['superuser'].school)[0]

    if context['superuser']:
        school = context['superuser'].school
        if school:
            school_areas = school.school_areas.all()
            if school_areas:
                for school_area in school_areas:
                    institutes = school_area.institutes.all()
                    if institutes:
                        for institute in institutes:
                            departments = institute.departments.all()
                            if departments:
                                for department in departments:
                                    context['departments'].append(department)

    return render(request, 'manage/personal_info.html', context)


def system_settings(request):
    context = {
        'title': '系统设置',
        'system_settings_active': True,  # 激活导航
        'superuser': None,
        'teacher': None,
        'school': None,

        'school_year': None,
        'term': None,
        'term_begin_date': None,
    }

    set_user_for_context(request.session['user_account'], context)
    if context['superuser'].school:
        context['school'] = context['superuser'].school

    # 学年学期数据要在判断设置完系统学年信息后才能获取
    context['school_year'] = SchoolYear.objects.all()[0]

    if context['school']:
        context['term'] = Term.objects.filter(school=context['school'])[0]
        context['term_begin_date'] = context['term'].begin_date

    return render(request, 'manage/system_settings.html', context)


def school_manage(request):
    context = {
        'title': '学校管理',
        'active_1': True,  # 激活导航
        'school_active': True,  # 激活导航
        'superuser': None,
        'teacher': None,

        'school': None,
        'school_areas': None,
        'institutes': [],
        'departments': [],
        'grades': [],
        'years': None,
    }

    set_user_for_context(request.session['user_account'], context)

    if context['superuser']:
        context['school'] = context['superuser'].school

    # 放在这里的作用是使得每次管理员登录就自动更新一下数据库的学年信息
    set_system_school_year()

    if context['school']:
        context['school_areas'] = context['school'].school_areas.all()

    if context['school_areas']:
        for school_area in context['school_areas']:
            for institute in school_area.institutes.all():
                context['institutes'].append(institute)

    if context['institutes']:
        for institute in context['institutes']:
            for department in institute.departments.all():
                context['departments'].append(department)

    if context['departments']:
        for department in context['departments']:
            for grade in department.grades.all():
                context['grades'].append(grade)

    context['years'] = [x for x in range(datetime.now().year - 5, datetime.now().year + 5)]

    return render(request, 'manage/school_manage.html', context)


def classes_manage(request):
    context = {
        'title': '班级管理',
        'active_1': True,  # 激活导航
        'classes_active': True,  # 激活导航
        'superuser': None,
        'teacher': None,

        'grades': [],
        'classes': [],
        'classes_numbers': [x for x in range(1, 9)]
    }

    set_user_for_context(request.session['user_account'], context)

    school = context['superuser'].school
    context['grades'] = get_all_grades(school)
    context['classes'] = get_all_classes(school)

    return render(request, 'manage/classes_manage.html', context)


def teacher_manage(request):
    context = {
        'title': '教师管理',
        'active_1': True,  # 激活导航
        'teacher_active': True,  # 激活导航
        'superuser': None,
        'teacher': None,

        'departments': [],
        'teachers': [],
    }

    set_user_for_context(request.session['user_account'], context)

    school = context['superuser'].school
    context['departments'] = get_all_departments(school)
    context['teachers'] = get_all_teachers(school)

    return render(request, 'manage/teacher_manage.html', context)


def course_manage(request):
    context = {
        'title': '课程管理',
        'active_1': True,  # 激活导航
        'course_active': True,  # 激活导航
        'superuser': None,
        'teacher': None,

        'institutes': [],
        'classes': [],
        'teachers': [],
        'courses': [],
        'attributes': None,
    }

    set_user_for_context(request.session['user_account'], context)

    school = context['superuser'].school
    context['institutes'] = get_all_institutes(school)
    context['classes'] = get_all_classes(school)
    context['teachers'] = get_all_teachers(school)
    context['attributes'] = school.labs_attributes.all()

    courses = get_all_courses(school)

    for course in courses:
        classes_of_the_course = course.classes.all()
        classes_ids = ""
        for classes_item in classes_of_the_course:
            classes_ids = classes_ids + ',%d' % classes_item.id

        teachers_of_the_course = course.teachers.all()
        teachers_ids = ""
        for teacher in teachers_of_the_course:
            teachers_ids = teachers_ids + ',%d' % teacher.id

        temp = {
            'course': course,
            'classes': classes_ids[1:],
            'teachers': teachers_ids[1:],
        }
        context['courses'].append(temp)

    return render(request, 'manage/course_manage.html', context)


def labs_attribute_manage(request):
    context = {
        'title': '实验室属性管理',
        'active_2': True,  # 激活导航
        'labs_attribute_active': True,  # 激活导航
        'superuser': None,
        'teacher': None,

        'labs_attributes': None,
    }

    set_user_for_context(request.session['user_account'], context)

    if context['superuser'].school:
        context['labs_attributes'] = context['superuser'].school.labs_attributes.all()

    return render(request, 'manage/labs_attribute_manage.html', context)


def experiment_type_manage(request):
    context = {
        'title': '实验类型设置',
        'active_3': True,  # 激活导航
        'experiment_type_active': True,  # 激活导航
        'superuser': None,
        'teacher': None,

        'experiment_types': None,
    }

    set_user_for_context(request.session['user_account'], context)

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

    set_user_for_context(request.session['user_account'], context)

    school = context['superuser'].school
    if school:
        context['labs_attributes'] = school.labs_attributes.all()

        context['institutes'] = get_all_institutes(school)
        context['labs'] = get_all_labs(school)

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

    set_user_for_context(request.session['user_account'], context)

    all_courses = None
    if context['superuser']:
        if context['superuser'].school:
            all_courses = get_all_courses(context['superuser'].school)

    if all_courses:
        i = 1
        for course in all_courses:
            experiments_of_the_course = Experiment.objects.filter(course=course)
            if experiments_of_the_course:
                experiments_amount = len(experiments_of_the_course)

                classes_name = ""
                for class_item in course.classes.all():
                    classes_name = classes_name + '<br>' + class_item.grade.name + "级" + class_item.grade.department.name + str(
                        class_item.name)

                teaching_materials = ""
                if course.total_requirements:
                    teaching_materials = course.total_requirements.teaching_materials

                # 或许不止一个老师上一门课
                teachers = ""
                for teacher in course.teachers.all():
                    teachers = teachers + ',' + teacher.name

                course_item = {
                    "id": course.id,
                    "no": i,
                    "teachers": teachers[1:],
                    "term": course.term if course.term else "",
                    "course": course.name,
                    "teaching_materials": teaching_materials,
                    "experiments_amount": experiments_amount,
                    "classes": classes_name[4:],
                    "create_time": course.modify_time,
                    "status": STATUS['%d' % experiments_of_the_course[0].status]
                }
                context['courses'].append(course_item)
                i = i + 1

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


def save_term_ajax(request):
    data = json.loads(list(request.POST.keys())[0])

    context = {
        'status': True,
        'message': None,
    }

    if request.is_ajax():

        try:
            term_id = data['term_id']
            term_name = data['term_name']
            begin_date = data['begin_date']

            Term.objects.filter(id=term_id).update(name=term_name, begin_date=begin_date)

        except:
            context['status'] = False
            context['message'] = '修改失败，请重试'

        return JsonResponse(context)


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
        set_user_for_context(request.session['user_account'], self.context)

        set_time_for_context(self.context)

        self.context['institutes'] = get_all_institutes(self.context['school'])
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


def get_model_field_ids(model, field_name):
    """
    获取某个模型的某个多对多字段的所有数据的id
    :param model:
    :param field_name: 模型对应字段名称的字符串
    :return: 返回id列表
    """
    field = getattr(model, field_name)
    print('获取到：', model, field)
    temp = []
    for x in field.all():
        temp.append(x.id)
    return temp


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
