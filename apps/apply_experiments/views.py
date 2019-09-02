import json
from django.http import HttpResponseRedirect
from django.shortcuts import render

from apps.apply_experiments.models import ExperimentType, Experiment
from apps.super_manage.models import Teacher, Course, Classes, Institute, Labs, LabsAttribute

from logging_setting import ThisLogger

this_logger = ThisLogger().logger


def load_classes_of_course(request):
    course_id = request.GET.get('course_id')
    this_logger.info('选择id为' + course_id + '的课程')
    classes_data = Classes.objects.filter(course=course_id).values('id', 'name', 'grade__name',
                                                                   'grade__department__name')
    # print('classes_data:', classes_data, 'type:', type(classes_data))

    # classes_data_list = []
    # for x in classes_data:
    #     classes_data_list.append({'value': x['id'], 'text': x['name']})
    # print(classes_data_list)
    # classes_data = classes_data_list
    #
    # return JsonResponse(classes_data)

    return render(request, 'apply_experiments/classes_options.html', {'classes_data': classes_data})


def load_labs_of_institute(request):
    institute_id = request.GET.get('institute_id')
    this_logger.info('选择id为' + institute_id + '的学院')
    labs_data = Labs.objects.filter(institute=institute_id).values('id', 'name')
    print(labs_data)

    return render(request, 'apply_experiments/labs_options.html', {'labs_data': labs_data})


def apply(request):
    try:
        account = request.session['user_account']
    except:
        return HttpResponseRedirect('/browse/login')

    context = {
        'title': '申请实验室',
        'apply_experiments_active': True,
        'user': None,
        'courses': None,
        'experiments_type': None,
        'experiment_lecture_time': None,
        'which_week': None,
        'experiment_on_week': None,
        'experiment_section': None,
        'labs_of_institute': None,
        'labs_attribute': None,
        'all_labs': None,
    }
    this_logger.info(account + '进入申请实验室页面')

    user = Teacher.objects.get(account=account)
    context['user'] = user

    context['courses'] = Course.objects.filter(teachers=user)

    context['experiments_type'] = ExperimentType.objects.all()

    # 后期根据实际情况调整下列静态数据：
    # 学时：
    context['lecture_time'] = [x for x in range(1, 11)]
    # 周次
    context['which_week'] = [x for x in range(1, 21)]
    # 星期
    context['days_of_the_week'] = [x for x in range(1, 8)]
    # 节次
    context['section'] = [x for x in range(1, 12)]

    context['labs_of_institute'] = Institute.objects.all()
    context['labs_attribute'] = LabsAttribute.objects.all()
    # 因为找不到联动数据的解决方案，暂时用所有实验室来代替
    context['all_labs'] = Labs.objects.all()
    return render(request, 'apply_experiments/apply.html', context)


def submit_experiments(request):
    data = json.loads(list(request.POST.keys())[0])
    this_logger.info('接收到提交的数据：'+str(data)+'类型为：'+str(type(data)))
    # for x in data['experiments']:
    #     new_experiment = Experiment(no=x['id'], name=x['experiment_name'], lecture_time=x['lecture_time'],
    #                                 which_week=x['which_week'], days_of_the_week=x['days_of_the_week'],
    #                                 section=x['section'], status=1)
    #     new_experiment.experiment_type = ExperimentType.objects.get(name=x['experiment_type'])
    #     new_experiment.labs.add(Labs.objects)
    #     if new_experiment.save():
    #         print('成功一个')

    return render(request, 'apply_experiments/apply.html')
