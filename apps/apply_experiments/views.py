import json
from django.http import HttpResponseRedirect
from django.shortcuts import render

from apps.apply_experiments.models import ExperimentType, Experiment, SpecialRequirements
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

    if data['experiments'] is not None and data['experiments'] is not "":
        # 先通过提交的课程id获取课程
        try:
            course = Course.objects.get(id=data['course_id'])
            this_logger.info('获取course:' + course.name)

            # 判断是否需要创建总体需求模型的实例
            if data['teaching_materials'] is "" and data['consume_requirements'] is "" \
                    and data['system_requirements'] is "" and data['soft_requirements'] is "":
                this_logger.info('提交的信息中没有总体需求')
            else:
                total_requirements = TotalRequirements.objects.create(
                    teaching_materials=data['teaching_materials'],
                    total_consume_requirements=data['consume_requirements'],
                    total_system_requirements=data['system_requirements'],
                    total_soft_requirements=data['soft_requirements']
                )
                # 把总体需求实例添加到该课程的对应外键
                course.total_requirements = total_requirements
                course.save()
                this_logger.info('提交的总体需求已存入课程，该总体需求的id为：' + str(course.total_requirements.pk))

                # 遍历所有的实验项目并创建、存储到数据库
                for experiment_item in data['experiments']:
                    this_logger.info('当前实验项目：'+str(experiment_item))
                    new_experiment = Experiment()

                    new_experiment.no = int(experiment_item['id'])
                    new_experiment.name = experiment_item['experiment_name']
                    new_experiment.lecture_time = int(experiment_item['lecture_time'])
                    new_experiment.which_week = int(experiment_item['which_week'])
                    new_experiment.days_of_the_week = int(experiment_item['days_of_the_week'])
                    new_experiment.section = experiment_item['section'][1:]
                    new_experiment.status = 1
                    new_experiment.course = course
                    new_experiment.save()

                    try:
                        new_experiment.experiment_type = ExperimentType.objects.get(id=int(experiment_item['experiment_type']))
                    except (Exception) as e:
                        print('id为'+experiment_item['experiment_type']+'的实验类型获取失败',e)

                    # 判断该实验项目是否有特殊需求
                    if experiment_item['special_consume_requirements'] is "" and experiment_item['special_system_requirements'] is "" \
                            and experiment_item['special_soft_requirements'] is "":
                        this_logger.info('该实验项目没有特殊实验需求')
                    else:
                        special_requirements = SpecialRequirements.objects.create(
                            special_consume_requirements=experiment_item['special_consume_requirements'],
                            special_system_requirements=experiment_item['special_system_requirements'],
                            special_soft_requirements=experiment_item['special_soft_requirements']
                        )
                        new_experiment.special_requirements = special_requirements

                    labs_ids = experiment_item['labs'].split(',')[1:]
                    this_logger.info('待处理的实验室的id列表：'+str(labs_ids))
                    for lab_item_id in labs_ids:
                        try:
                            lab = Labs.objects.get(id=int(lab_item_id))
                            this_logger.info('获取到lab：'+lab.name)
                            new_experiment.labs.add(lab)
                        except (Exception) as e:
                            print('获取id为'+lab_item_id+'的实验室失败',e)

                    labs_attributes_ids = experiment_item['labs_attribute'].split(',')[1:]
                    this_logger.info('待处理的实验室属性的id列表'+str(labs_attributes_ids))
                    for labs_attribute_item_id in labs_attributes_ids:
                        try:
                            labs_attribute = LabsAttribute.objects.get(id=int(labs_attribute_item_id))
                            this_logger.info('获取到lab_attribute：' + labs_attribute.name)
                            new_experiment.labs_attribute.add(labs_attribute)
                        except (Exception) as e:
                            print('获取id为' + labs_attribute_item_id + '的实验室属性失败', e)

                    new_experiment.save()
        except (Exception) as e:
            print('处理id为' + data['course_id'] + '的课程的实验项目时失败',e)

    return render(request, 'apply_experiments/apply.html')
