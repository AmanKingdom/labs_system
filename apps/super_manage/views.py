import json

from django.http import JsonResponse
from django.shortcuts import render

from apps.apply_experiments.views import set_user_for_context
from apps.super_manage.models import School, SchoolArea

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
    }

    set_user_for_context(request.session['user_account'], context)

    context['school'] = context['superuser'].school

    if context['school']:
        context['school_areas'] = context['school'].school_areas.all()

    if context['school_areas']:
        for school_area in context['school_areas']:
            for institute in school_area.institutes.all():
                context['institutes'].append(institute)

    return render(request, 'super_manage/school_manage.html', context)


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


def remove_school_areas_ajax(request):
    data = json.loads(list(request.POST.keys())[0])

    context = {
        'status': True,
        'message': None,
    }
    if request.is_ajax():
        remove_school_areas_ids = data['remove_school_areas_ids']
        this_logger.info('接收到remove_school_areas_ids:' + str(remove_school_areas_ids) + '类型为：' + str(type(remove_school_areas_ids)))

        try:
            for id in remove_school_areas_ids:
                SchoolArea.objects.get(id=id).delete()
        except:
            context['status'] = False
            context['message'] = '删除失败，请重试'

        return JsonResponse(context)


def save_school_areas_ajax(request):
    data = json.loads(list(request.POST.keys())[0])

    context = {
        'status': True,
        'message': None,
    }

    if request.is_ajax():
        school_areas = data['school_areas']
        school_name = data['school_name']
        print(school_areas, school_name)

        try:
            for school_area in school_areas:
                if 'id_in_database' in school_area.keys():
                    s = SchoolArea.objects.filter(id=int(school_area['id_in_database']), school__name=school_name)
                    s.update(name=school_area['school_area_name'])
                else:
                    SchoolArea.objects.create(name=school_area['school_area_name'], school=School.objects.get(name=school_name))
        except:
            context['status'] = False
            context['message'] = '修改失败，请重试'

        return JsonResponse(context)
