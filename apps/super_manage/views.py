import json
from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render

from apps.apply_experiments.models import Experiment, ExperimentType
from apps.apply_experiments.views import set_user_for_context
from apps.super_manage.models import School, SchoolArea, Institute, Department, Grade, SuperUser, Classes, Teacher, \
    SchoolYear, Term, Course, LabsAttribute, Labs
from apps.browse.views import create_default_term_for_school

from logging_setting import ThisLogger

this_logger = ThisLogger().logger


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

    return render(request, 'super_manage/personal_info.html', context)


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

    return render(request, 'super_manage/system_settings.html', context)


def school_manage(request):
    context = {
        'title': '学校管理',
        'school_active': True,  # 激活导航
        'superuser': None,
        'teacher': None,

        'school': None,
        'school_areas': None,
        'institutes': [],
        'departments': [],
        'grades': [],
    }

    set_user_for_context(request.session['user_account'], context)

    if context['superuser']:
        context['school'] = context['superuser'].school

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

    return render(request, 'super_manage/school_manage.html', context)


def classes_manage(request):
    context = {
        'title': '班级管理',
        'classes_active': True,  # 激活导航
        'superuser': None,
        'teacher': None,

        'grades': [],
        'classes': [],
    }

    set_user_for_context(request.session['user_account'], context)

    school = context['superuser'].school
    context['grades'] = get_all_grades(school)
    context['classes'] = get_all_classes(school)

    return render(request, 'super_manage/classes_manage.html', context)


def teacher_manage(request):
    context = {
        'title': '教师管理',
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

    return render(request, 'super_manage/teacher_manage.html', context)


def course_manage(request):
    context = {
        'title': '课程管理',
        'course_active': True,  # 激活导航
        'superuser': None,
        'teacher': None,

        'institutes': [],
        'classes': [],
        'teachers': [],
        'courses': [],
    }

    set_user_for_context(request.session['user_account'], context)

    school = context['superuser'].school
    context['institutes'] = get_all_institutes(school)
    context['classes'] = get_all_classes(school)
    context['teachers'] = get_all_teachers(school)

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

    return render(request, 'super_manage/course_manage.html', context)


def labs_attribute_manage(request):
    context = {
        'title': '实验室属性管理',
        'labs_attribute_active': True,  # 激活导航
        'superuser': None,
        'teacher': None,

        'labs_attributes': None,
    }

    set_user_for_context(request.session['user_account'], context)

    if context['superuser'].school:
        context['labs_attributes'] = context['superuser'].school.labs_attributes.all()

    return render(request, 'super_manage/labs_attribute_manage.html', context)


def experiment_type_manage(request):
    context = {
        'title': '实验类型管理',
        'experiment_type_active': True,  # 激活导航
        'superuser': None,
        'teacher': None,

        'experiment_types': None,
    }

    set_user_for_context(request.session['user_account'], context)

    if context['superuser'].school:
        context['experiment_types'] = context['superuser'].school.experiment_types.all()

    return render(request, 'super_manage/experiment_type_manage.html', context)


def lab_manage(request):
    context = {
        'title': '实验室管理',
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
        all_labs = get_all_labs(school)

        for lab in all_labs:
            attributes_of_the_lab = lab.attributes.all()
            attributes_ids = ""
            for attribute in attributes_of_the_lab:
                attributes_ids = attributes_ids + ',%d' % attribute.id

            temp = {
                'lab': lab,
                'labs_attributes': attributes_ids[1:],
            }
            context['labs'].append(temp)

    return render(request, 'super_manage/lab_manage.html', context)


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
                    Labs.objects.get(id=id).delete()

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

        if data['delete_ids_in_database']:
            this_logger.info('将要删除：'+str(data['delete_ids_in_database']))

            # 删除情况
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
                    Labs.objects.get(id=id).delete()


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
                    add_teachers_classes_to_course(c[0], save_object)
                elif data['save_objects_model'] == 'labs_attributes':
                    l = LabsAttribute.objects.filter(id=int(save_object['id_in_database']))
                    l.update(name=save_object['labs_attribute_name'])
                elif data['save_objects_model'] == 'experiment_types':
                    et = ExperimentType.objects.filter(id=int(save_object['id_in_database']))
                    et.update(name=save_object['experiment_type_name'])
                elif data['save_objects_model'] == 'labs':
                    lab = Labs.objects.filter(id=int(save_object['id_in_database']))
                    if str(save_object['dispark']) == '1':
                        dispark = True
                    else:
                        dispark = False
                    lab.update(name=save_object['lab_name'],
                               institute=Institute.objects.get(id=save_object['institute']),
                               number_of_people=save_object['number_of_people'],
                               dispark=dispark,
                               equipments=save_object['equipments'])
                    add_labs_attributes_to_lab(lab[0], save_object)

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
                    lab = Labs.objects.create(name=save_object['lab_name'],
                                              institute=Institute.objects.get(id=save_object['institute']),
                                              number_of_people=save_object['number_of_people'],
                                              dispark=dispark,
                                              equipments=save_object['equipments'])
                    add_labs_attributes_to_lab(lab, save_object)

        # except:
        #     context['status'] = False
        #     context['message'] = '修改失败，请重试'

        return JsonResponse(context)


def add_labs_attributes_to_lab(lab, save_object):
    labs_attributes_ids = make_ids(str(save_object['labs_attributes']))
    for labs_attributes_id in labs_attributes_ids:
        if labs_attributes_id:
            lab.attributes.add(LabsAttribute.objects.get(id=labs_attributes_id))


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
