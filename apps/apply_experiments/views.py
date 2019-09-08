import json
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, Http404
from django.shortcuts import render

from apps.apply_experiments.models import ExperimentType, Experiment, SpecialRequirements
from apps.super_manage.models import Teacher, Course, Classes, Institute, Labs, LabsAttribute, Department, \
    TotalRequirements, SchoolYear, Term

from logging_setting import ThisLogger

this_logger = ThisLogger().logger


STATUS = {
    '1': '已提交待审核',
    '2': '审核不通过',
    '3': '审核通过'
}


# 数据联动，动态加载班级数据
def load_classes_of_course(request):
    course_id = request.GET.get('course_id')
    this_logger.info('选择id为' + course_id + '的课程')
    classes = Classes.objects.filter(course=course_id).values('id', 'name', 'grade__name', 'grade__department__name')
    return render(request, 'apply_experiments/classes_options.html', {'classes': classes})

# 数据联动，动态加载实验室数据 -- 暂不启用
# def load_labs_of_institute(request):
#     institute_id = request.GET.get('institute_id')
#     this_logger.info('选择id为' + institute_id + '的学院')
#     labs_data = Labs.objects.filter(institute=institute_id).values('id', 'name')
#     print(labs_data)
#
#     return render(request, 'apply_experiments/labs_options.html', {'labs_data': labs_data})


# context中的值有则提供给前端，无数据则由前端自行判断处理
def apply(request):
    context = {
        'title': '申请实验室',
        'apply_experiments_active': True,   # 激活导航
        'user': None,
        'courses': [],    # 默认筛选出当前学期的课程，因为只能申请当前学期的课程实验
        'classes': None,
        'experiments_type': None,
        'lecture_time': None,
        'which_week': None,
        'days_of_the_week': None,
        'section': None,
        'labs_of_institute': None,
        'labs_attribute': None,
        'all_labs': None,
    }

    context['user'] = Teacher.objects.get(account=request.session['user_account'])
    temp_courses = Course.objects.filter(teachers=context['user'])

    # 实验项目为空则证明该门课没有申请过，可以显示
    for course in temp_courses:
        experiments_amount = Experiment.objects.filter(course=course)
        if len(experiments_amount) == 0:
            context['courses'].append(course)

    if len(context['courses']) != 0:
        # 初次打开页面如果有对应课程，则根据第一门课程先提供班级数据
        context['classes'] = Classes.objects.filter(course=context['courses'][0]).values('id',
                                                                                         'name',
                                                                                         'grade__name',
                                                                                         'grade__department__name')

    context['experiments_type'] = ExperimentType.objects.all()

    # 后期根据实际情况调整下列静态数据：
    # 学时
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

    context = {
        'status': True,  # 检验是否通过
        'message': "",    # 反馈信息
    }

    if data['course_id'] is not '':
        if data['experiments']:
            # 先通过提交的课程id获取课程
            try:
                course = Course.objects.get(id=data['course_id'])
                this_logger.info('获取course:' + course.name)

                # 判断是否需要创建总体需求的实例
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
                    this_logger.info('当前处理的实验项目：' + str(experiment_item))
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
                        if experiment_item['experiment_type']:
                            new_experiment.experiment_type = ExperimentType.objects.get(
                                id=int(experiment_item['experiment_type']))
                    except (Exception) as e:
                        context['status'] = False
                        print('id为' + experiment_item['experiment_type'] + '的实验类型获取失败', e)

                    # 判断该实验项目是否有特殊需求
                    if experiment_item['special_consume_requirements'] is "" and experiment_item[
                        'special_system_requirements'] is "" \
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
                    this_logger.info('待处理的实验室的id列表：' + str(labs_ids))
                    for lab_item_id in labs_ids:
                        try:
                            lab = Labs.objects.get(id=int(lab_item_id))
                            this_logger.info('获取到lab：' + lab.name)
                            new_experiment.labs.add(lab)
                        except (Exception) as e:
                            context['status'] = False
                            print('获取id为' + lab_item_id + '的实验室失败', e)

                    labs_attributes_ids = experiment_item['labs_attribute'].split(',')[1:]
                    this_logger.info('待处理的实验室属性的id列表' + str(labs_attributes_ids))
                    for labs_attribute_item_id in labs_attributes_ids:
                        try:
                            labs_attribute = LabsAttribute.objects.get(id=int(labs_attribute_item_id))
                            this_logger.info('获取到lab_attribute：' + labs_attribute.name)
                            new_experiment.labs_attribute.add(labs_attribute)
                        except (Exception) as e:
                            context['status'] = False
                            print('获取id为' + labs_attribute_item_id + '的实验室属性失败', e)

                    new_experiment.save()
            except (Exception) as e:
                context['status'] = False
        else:
            this_logger.info('experiments没有内容')
            context['status'] = False
            context['empty_experiment'] = '实验项目不能为空'
    else:
        this_logger.info('课程为空')
        context['status'] = False
        context['message'] = context['message'] + "课程不能为空"
    return JsonResponse(context)


def manage_application(request):
    context = {
        'title': '申请信息管理',
        'apply_info_active': True,  # 激活导航
        'courses': [],
    }

    try:
        courses_of_the_user = Course.objects.filter(teachers__account__contains=request.session['user_account'])
        this_logger.info('获取到课程：' + str(courses_of_the_user))

        if courses_of_the_user:
            i = 1
            for course in courses_of_the_user:
                experiments_of_the_course = Experiment.objects.filter(course=course)
                if experiments_of_the_course:
                    experiments_amount = len(experiments_of_the_course)

                    classes_name = ""
                    for class_item in course.classes.all():
                        classes_name = classes_name+','+class_item.grade.name+"级"+class_item.grade.department.name+str(class_item.name)

                    teaching_materials = ""
                    if course.total_requirements:
                        teaching_materials = course.total_requirements.teaching_materials

                    # 或许不止一个老师上一门课
                    teachers = ""
                    for teacher in course.teachers.all():
                        teachers = teachers+','+teacher.name

                    course_item = {
                        "no": i,
                        "teachers": teachers[1:],
                        "term": course.term if course.term else "",
                        "course": course.name,
                        "teaching_materials": teaching_materials,
                        "experiments_amount": experiments_amount,
                        "classes": classes_name[1:],
                        "create_time": course.modify_time,
                        "status": STATUS['%d' % experiments_of_the_course[0].status]
                    }
                    context['courses'].append(course_item)
                    i = i + 1

    except (Exception) as e:
        print('获取实验申请信息时出错', e)

    return render(request, 'apply_experiments/manage_application.html', context)


def change_experiments(request, term=None, course_name=None):
    this_logger.info('实验项目申请信息管理页面视图，接收到学年学期：'+str(term)+' 课程：'+str(course_name))

    context = {
        'title': '申请信息管理',
        'apply_info_active': True,  # 激活导航
        'status': True,
        'experiments': None,
        'course': None,
        'message': "",

        'experiments_type': ExperimentType.objects.all() if ExperimentType.objects.all() else "",
        'lecture_time': None,
        'which_week': None,
        'days_of_the_week': None,
        'section': None,
        'labs_of_institute': None,
        'labs_attribute': None,
        'all_labs': None,
    }

    # 后期根据实际情况调整下列静态数据：
    # 学时
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

    try:
        course = Course.objects.get(teachers__account=request.session['user_account'], name=course_name)
    except (Exception) as e:
        print('无法获取', request.session['user_account'], '的', course_name, '课程实例', e)

    if course:
        experiments_origin = Experiment.objects.filter(course=course)
        if len(experiments_origin) > 0:

            experiments = []
            for experiment in experiments_origin:

                labs = experiment.labs.all()
                labs_of_institute = ""
                if len(labs) > 0:
                    labs_of_institute = labs[0].institute

                labs_attributes_of_experiment = experiment.labs_attribute.all()
                labs_attributes = ""
                for labs_attribute in labs_attributes_of_experiment:
                    labs_attributes = labs_attributes + ',%d' % labs_attribute.id

                labs_ids = ""
                for lab in labs:
                    labs_ids = labs_ids + ',%d' % lab.id

                temp_experiment = {
                    'experiment': experiment,
                    'labs_of_institute': labs_of_institute,
                    'labs_attribute': labs_attributes[1:],
                    'labs': labs_ids[1:]
                }
                experiments.append(temp_experiment)

            context['experiments'] = experiments

            teachers = ""
            for teacher in course.teachers.all():
                teachers = teachers+','+teacher.name

            classes_name = ""
            for class_item in course.classes.all():
                classes_name = classes_name + ',' + class_item.grade.name + "级" + class_item.grade.department.name + \
                               str(class_item.name)

            context['course'] = {
                'course': course,
                'teachers': teachers[1:],
                'classes': classes_name[1:],
                'status': STATUS['%d' % experiments_origin[0].status],
            }
        else:
            context['status'] = False
            context['message'] = '出错，实验项目数据为空'
    else:
        context['status'] = False
        context['message'] = '出错，该课程存在异常'
    return render(request, 'apply_experiments/change_experiments.html', context)
