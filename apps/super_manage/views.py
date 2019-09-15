import json

from django.http import JsonResponse
from django.shortcuts import render

from apps.apply_experiments.views import set_user_for_context
from apps.super_manage.models import School, SchoolArea, Institute, Department, Grade

from logging_setting import ThisLogger

this_logger = ThisLogger().logger


def school_manage(request):
    context = {
        'title': '学校管理',
        'school_active': True,  # 激活导航
        'user': None,
        'superuser': None,
        'teacher': None,

        'school': None,
        'school_areas': None,
        'institutes': [],
        'departments': [],
        'grades': [],
    }

    set_user_for_context(request.session['user_account'], context)

    context['school'] = context['superuser'].school

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
        'user': None,
        'superuser': None,
        'teacher': None,

        'grades': [],
    }

    set_user_for_context(request.session['user_account'], context)

    # if context['departments']:
    #     for department in context['departments']:
    #         for grade in department.grades.all():
    #             context['grades'].append(grade)

    return render(request, 'super_manage/classes_manage.html', context)


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
                School.objects.create(name=new_school_name)
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

        except:
            context['status'] = False
            context['message'] = '修改失败，请重试'

        return JsonResponse(context)
