import json
from django.http import HttpResponseRedirect
from django.shortcuts import render

from apps.apply_experiments.models import ExperimentType, Experiment
from apps.super_manage.models import Teacher, Course, Classes, Institute, Labs, LabsAttribute, Department, \
    TotalRequirements

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
    this_logger.info('接收到提交的数据：' + str(data) + '类型为：' + str(type(data)))

    # 通过提交的 系 获取开课单位 学院
    try:
        institute = Department.objects.get(name=data['department']).institute
        this_logger.info('获取institute:' + institute.name)
    except:
        this_logger.info('获取系别为' + data['department'] + '的学院失败')

    # 通过提交的课程id获取课程
    try:
        course = Course.objects.get(id=data['course_id'])
        this_logger.info('获取course:' + course.name)

        if data['teaching_materials'] is "" and data['consume_requirements'] is "" \
                and data['system_requirements'] is "" and data['soft_requirements'] is "":
            this_logger.info('提交的信息中没有总体需求')
        else:
            total_requirements = TotalRequirements.objects.create(
                teaching_materials=data['teaching_materials'], consume_requirements=data['consume_requirements'],
                system_requirements=data['system_requirements'], soft_requirements=data['soft_requirements']
            )
            course.total_requirements = total_requirements
            course.save()
            this_logger.info('提交的总体需求已存入课程，该总体需求的id为：'+course.total_requirements.pk)
    except:
        this_logger.info('获取id为' + data['course_id'] + '的课程失败')

    # 通过提交的授课班级的id列表分别获取对应班级并添加进实验项目
    this_logger.info('data["classes_id"]的类型：'+str(type(data['classes_id'])))
    for x in data['classes_id']:
        try:
            classes = Classes.objects.get(id=int(x))
            this_logger.info('获取到classes:'+classes.name)
        except:
            this_logger.info('获取id为' + data['classes_id'] + '的班级失败')

    # for x in data['experiments']:
    #     new_experiment = Experiment(no=x['id'], name=x['experiment_name'], lecture_time=x['lecture_time'],
    #                                 which_week=x['which_week'], days_of_the_week=x['days_of_the_week'],
    #                                 section=x['section'], status=1)
    #     new_experiment.experiment_type = ExperimentType.objects.get(name=x['experiment_type'])
    #     new_experiment.labs.add(Labs.objects.all())
    #     if new_experiment.save():
    #         print('成功一个')

    return render(request, 'apply_experiments/apply.html')
