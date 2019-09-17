import json
from datetime import datetime

from django.http import JsonResponse
from django.shortcuts import render

from apps.apply_experiments.views import set_user_for_context
from apps.super_manage.models import School, SchoolArea, Institute, Department, Grade, SuperUser, Classes, Teacher, \
    SchoolYear, Term
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
                SchoolYear.objects.filter(id=school_year.id).update(since=year_now, to=year_now+1)
        else:
            if school_year.to != year_now:
                # 学年的结束年份不是当前年份，需要更新
                SchoolYear.objects.filter(id=school_year.id).update(since=year_now-1, to=year_now)
    else:
        SchoolYear.objects.create(since=year_now, to=year_now+1)


def get_all_school_areas(school):
    if school:
        return school.school_areas.all()


def get_all_institutes(school):
    institutes = []
    school_areas = get_all_school_areas(school)
    if school_areas:
        for school_area in school_areas:
            institutes.append(school_area.institutes.all())
    return institutes


def get_all_departments(school):
    departments = []
    institutes = get_all_institutes(school)
    if institutes:
        for institute in institutes:
            departments.append(institute.departments.all())
    return departments


def get_all_grades(school):
    grades = []
    departments = get_all_departments(school)
    if departments:
        for department in departments:
            grades.append(department.grades.all())
    return grades


def get_all_classes(school):
    classes = []
    grades = get_all_grades(school)
    if grades:
        for grade in grades:
            classes.append(grade.classes.all())
    return classes


def get_all_teachers(school):
    teachers = []
    departments = get_all_departments(school)
    if departments:
        for department in departments:
            teachers.append(department.teachers.all())
    return teachers


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

        'school_year': None,
        'term': None,
        'term_begin_date': None,
    }

    set_user_for_context(request.session['user_account'], context)

    if context['superuser']:
        context['school'] = context['superuser'].school

    set_system_school_year()
    # 学年学期数据要在判断设置完系统学年信息后才能获取
    context['school_year'] = SchoolYear.objects.all()[0]
    context['term'] = Term.objects.filter(school=context['school'])[0]
    context['term_begin_date'] = context['term'].begin_date

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
    
    return render(request, 'super_manage/teacher_manage.html', context)


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
                         ' 删除对象模型为：'+ data['remove_objects_model'])

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

        try:
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

        except:
            context['status'] = False
            context['message'] = '修改失败，请重试'

        return JsonResponse(context)


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
