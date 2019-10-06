import json
from datetime import datetime

from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render

from apps.super_manage.models import School, SchoolArea, Institute, Department, Grade, SuperUser, Classes, Teacher, \
    SchoolYear, Term, Course, LabsAttribute, Lab, Experiment, ExperimentType, Schedule

from logging_setting import ThisLogger
this_logger = ThisLogger().logger

STATUS = {
    '1': '已提交待审核',
    '2': '审核不通过',
    '3': '审核通过'
}


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

    context['years'] = [x for x in range(datetime.now().year-5, datetime.now().year+5)]

    return render(request, 'super_manage/school_manage.html', context)


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

    return render(request, 'super_manage/classes_manage.html', context)


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

    return render(request, 'super_manage/teacher_manage.html', context)


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

    return render(request, 'super_manage/course_manage.html', context)


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

    return render(request, 'super_manage/labs_attribute_manage.html', context)


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

    return render(request, 'super_manage/experiment_type_manage.html', context)


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

    return render(request, 'super_manage/lab_manage.html', context)


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

    return render(request, 'super_manage/application_manage.html', context)


def application_check(request, course_id=None, status=None):
    this_logger.info('审核，接收到id：' + str(course_id) + '和status：' + str(status))

    course = Course.objects.get(id=course_id)
    experiments = course.experiments.all()
    for experiment in experiments:
        experiment.status = status
        experiment.save()

    return HttpResponseRedirect('/super_manage/application_manage')


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


# 做出前端排课结果表格所需的json数据，将要去除该函数。
def get_schedule(request, school_id=None):
    data = {
        "total": 1,
        "rows": []
    }

    school = School.objects.get(id=school_id)

    labs = get_all_labs(school)
    courses = get_all_courses(school)

    for course in courses:
        experiments = course.experiments.all()
        if experiments:
            for experiment in experiments:
                if experiment.status == 3:
                    new_dict = {
                        "days_of_the_week": experiment.days_of_the_week,
                        "section": experiment.section
                    }
                    labs_in_experiment = experiment.labs.all()
                    for lab in labs:
                        if lab in labs_in_experiment:
                            new_dict["%s" % lab.name] = "<div>%s</div>" % course.name
                        else:
                            new_dict["%s" % lab.name] = ""
                    data['rows'].append(new_dict)

    temp_dict = {"days_of_the_week": "", "section": ""}
    for lab in labs:
        temp_dict["%s" % lab.name] = ""
    data['rows'].insert(0, temp_dict)
    print(data['rows'])

    return JsonResponse(data)


# 获取某学校所有审核通过了的实验项目
def get_all_experiments_3(school):
    return_experiments = []
    courses = get_all_courses(school)
    for course in courses:
        experiments = course.experiments.all()
        if experiments:
            for experiment in experiments:
                if experiment.status == 3:  # 取审核通过的实验
                    return_experiments.append(experiment)

    return return_experiments


def arrange(request):
    context = {
        'title': '实验类型设置',
        'active_3': True,  # 激活导航
        'arrange_active': True,  # 激活导航
        'superuser': None,
        'teacher': None,

        'school': None,
        'labs': None,
        'conflict_courses': [],
    }

    set_user_for_context(request.session['user_account'], context)
    if context['superuser'].school:
        context['school'] = context['superuser'].school

        # 实验室数据用来前端生成表头
        context['labs'] = get_all_labs_dispark(context['school'])

        create_schedules_set_suitable(context['school'])

        # 整理出冲突课程的数据以供人工解决
        need_adjust_schedules = Schedule.objects.filter(school=context['school'], need_adjust=True)
        need_adjust_courses = []  # 先得到不重复的需要人工调整的课程
        for schedule_item in need_adjust_schedules:
            if schedule_item.experiment.course not in need_adjust_courses:
                need_adjust_courses.append(schedule_item.experiment.course)

        i = 1
        all_labs = get_all_labs_dispark(context['school'])
        for course in need_adjust_courses:
            schedules_of_the_course = Schedule.objects.filter(experiment__course=course)
            new_dict = {'no': i, 'weeks': '', 'days_of_the_week': '', 'section': '', 'course': course, 'classes': [],
                        'free_labs': []}

            for classes_item in Classes.objects.filter(course=course).values('id', 'name', 'grade__name',
                                                                             'grade__department__name'):
                new_dict['classes'].append(classes_item)

            weeks = []
            days_of_the_week = []
            section = []

            self_labs = []
            for schedule_item in schedules_of_the_course:
                if schedule_item.which_week not in weeks:
                    weeks.append(schedule_item.which_week)
                if schedule_item.days_of_the_week not in days_of_the_week:
                    days_of_the_week.append(schedule_item.days_of_the_week)
                if schedule_item.section not in section:
                    section.append(schedule_item.section)

                aready_in_used_labs = []
                # 这里的冲突安排包含了自身，在这里的逻辑中，自身安排的实验室也是可以作为可用实验室提供给前端的，所以还要去掉自身
                conflict_schedules = Schedule.objects.filter(which_week=schedule_item.which_week,
                                                             days_of_the_week=schedule_item.days_of_the_week,
                                                             section=schedule_item.section)

                free_labs_of_the_schedule = []

                for temp_schedule in conflict_schedules:
                    if temp_schedule.lab not in aready_in_used_labs:
                        aready_in_used_labs.append(temp_schedule.lab)

                for lab in all_labs:
                    if lab not in aready_in_used_labs:
                        free_labs_of_the_schedule.append(lab)  # 这些空闲实验室只是当前这个安排的情况下有空闲而已，而总的空闲实验室还要根据该课程下所有安排的时间决定

                self_labs.append(schedule_item.lab)
                new_dict["free_labs"].append(free_labs_of_the_schedule)

            def list_to_string(l, tag):
                temp_str = ''
                for s in l:
                    temp_str = temp_str + tag + str(s)
                return temp_str[1:]

            new_dict['weeks'] = list_to_string(weeks, ',')
            new_dict['days_of_the_week'] = list_to_string(days_of_the_week, ',')
            new_dict['section'] = list_to_string(section, ',')

            # 要对课程的空闲实验室进行 交集 处理
            if len(new_dict['free_labs']) > 1:
                temp_free_labs = new_dict['free_labs']

                result_set = set(temp_free_labs[0])
                for index in range(1, len(temp_free_labs)):
                    result_set = result_set.intersection(set(temp_free_labs[index]))
                new_dict['free_labs'] = list(result_set)
            elif len(new_dict['free_labs']) == 1:
                new_dict['free_labs'] = new_dict['free_labs'][0]

            # 实验安排自身的实验室也是可用实验室
            new_dict['free_labs'] = list(set(self_labs))[::-1] + new_dict['free_labs']

            context['conflict_courses'].append(new_dict)

            i = i + 1

    return render(request, 'super_manage/arrange.html', context)


def re_arrange(request):
    context = {
        'status': True,
        'message': None,
    }

    school = SuperUser.objects.get(account=request.session.get('user_account')).school
    Schedule.objects.filter(school=school).delete()

    experiments = get_all_experiments_3(school)
    for experiment in experiments:
        experiment.aready_schedule = False
        experiment.save()

    return JsonResponse(context)


# 给schedule数据库做一遍数据，并计算出适合度存入
def create_schedules_set_suitable(school):
    experiments = get_all_experiments_3(school)
    for experiment in experiments:
        if not experiment.aready_schedule:
            experiment.aready_schedule = True
            experiment.save()

            sections = experiment.section.split(',')
            for section in sections:

                labs = experiment.labs.all()
                for lab in labs:

                    # 判断是否有冲突
                    schedules = Schedule.objects.filter(
                        school=school,
                        which_week=experiment.which_week,
                        days_of_the_week=experiment.days_of_the_week,
                        section=int(section),
                        lab=lab
                    )

                    schedules_len = len(schedules)

                    # same_schedules = Schedule.objects.filter(
                    #     school=school,
                    #     which_week=experiment.which_week,
                    #     days_of_the_week=experiment.days_of_the_week,
                    #     section=int(section),
                    #     experiment=experiment
                    # )
                    # print('数据库中是否存在实验：', experiment, '的安排数据?', same_schedules)

                    # 当数据库没有这条记录时可以考虑存入
                    # if not same_schedules:
                    conflict = False
                    if schedules_len > 0:
                        conflict = True
                        schedules.update(conflict=conflict)

                    s = Schedule.objects.create(
                        school=school,
                        which_week=experiment.which_week,
                        days_of_the_week=experiment.days_of_the_week,
                        section=int(section),
                        lab=lab,
                        experiment=experiment,
                        conflict=conflict
                    )
                    print('set_suitable_and_schedule()创建', s)

                    for schedule_item in schedules:
                        # 通过课程的属性设置适合度，实验室的层级属性的权值分别为：一级-15，二级-10，三级-5
                        the_attribute = schedule_item.experiment.course.attribute
                        if the_attribute:
                            if the_attribute == lab.attribute1:
                                schedule_item.suitable = 15
                            elif the_attribute == lab.attribute2:
                                schedule_item.suitable = 10
                            elif the_attribute == lab.attribute3:
                                schedule_item.suitable = 5
                            schedule_item.save()

                        # 通过班级数量设置适合度，因为班级一般不会超过3，所以可以用个位数表示其优先权
                        classes_num = len(Classes.objects.filter(course=schedule_item.experiment.course))
                        schedule_item.suitable = schedule_item.suitable + classes_num
                        schedule_item.save()
    # 数据做完，则处理一遍冲突
    dispose_conflict(school)


def dispose_conflict(school):
    while True:
        # 以 适合度 作为第一排序依据、课程作为第二排序依据、实验项目作为第三排序依据获取所有 冲突且不用人工调整的 条目
        conflict_no_need_adjust_schedules = Schedule.objects.filter(school=school, conflict=True,
                                                                    need_adjust=False).order_by('-suitable',
                                                                                                'experiment__course',
                                                                                                'experiment')
        if conflict_no_need_adjust_schedules:
            print('存在 冲突且不需人工调整 的条目')

            first = True  # 用来说明冲突己方已在最期望的最适合位置上，不需要自动调整实验室，否则需要调整
            conflict_me = conflict_no_need_adjust_schedules[0]  # 冲突己方
            print('冲突己方：', conflict_me)

            # 冲突双方集合，包含冲突己方，获取冲突对方则要从[1:]取
            all_conflict = conflict_no_need_adjust_schedules.filter(
                which_week=conflict_me.which_week,
                days_of_the_week=conflict_me.days_of_the_week,
                section=conflict_me.section,
                lab=conflict_me.lab
            )

            if len(all_conflict) > 1:
                i = 2
                for conflict_you in all_conflict[1:]:
                    print('冲突对方：', conflict_you)
                    if conflict_me.suitable == conflict_you.suitable:
                        print('冲突双方的适合度相同:', conflict_me.suitable, conflict_you.suitable)
                        for conflict_item in all_conflict:  # 这里的冲突条目都是来自不同课程的，需要对这些课程的所有冲突与非冲突安排都设置为需要人工调整
                            Schedule.objects.filter(experiment__course=conflict_item.experiment.course).update(
                                need_adjust=True)
                        break
                    elif conflict_me.suitable > conflict_you.suitable:
                        print('冲突己方的适合度大:', conflict_me.suitable, conflict_you.suitable, '取消冲突己方课程的所有冲突条目的冲突')

                        if first:
                            print(conflict_me, '冲突己方不需要重新设置实验室')
                            conflict_no_need_adjust_schedules.filter(
                                experiment__course=conflict_me.experiment.course).update(conflict=False)
                            first = False
                        else:
                            print(conflict_me, '冲突己方课程的所有条目要重新设置实验室')
                            new_labs_for_schedule(school, conflict_me)

                        if i < len(all_conflict):
                            print('有下一个冲突对方:', all_conflict[i])
                            conflict_me = conflict_you
                        else:
                            print('没有下一个冲突对方，重新设置当前冲突对方课程的所有条目的实验室')
                            new_labs_for_schedule(school, conflict_you)
            else:
                print(conflict_me, '的冲突对方已被设置为人工调整，所以冲突己方也要被设置为人工调整')
                Schedule.objects.filter(experiment__course=conflict_me.experiment.course).update(need_adjust=True)
                break
        else:
            this_logger.info('已经没有 冲突且不需人工调整 的条目了')
            break


# 通过调用find_free_labs()寻找合适的实验室给这条安排的课程的所有条目，由于条目的更新并不容易，所以直接删除后从实验项目做一遍新数据
def new_labs_for_schedule(school, conflict_schedule):
    print('执行赋值新实验室函数------------------------------------' * 2)
    labs = find_free_labs(school, conflict_schedule.experiment.course)
    if labs:
        course = conflict_schedule.experiment.course
        Schedule.objects.filter(experiment__course=course).delete()
        create_schedule_for_course(school, course, labs)

    else:
        Schedule.objects.filter(experiment__course=conflict_schedule.experiment.course).update(need_adjust=True)


def create_schedule_for_course(school, course, labs):
    experiments = Experiment.objects.filter(course=course)
    for experiment in experiments:
        sections = experiment.section.split(',')
        for section in sections:

            for lab in labs:
                new_schedule = Schedule.objects.create(
                    school=school,
                    which_week=experiment.which_week,
                    days_of_the_week=experiment.days_of_the_week,
                    section=int(section),
                    lab=lab,
                    experiment=experiment,
                )
                print('create_schedule_for_course创建schedule：', new_schedule)


def find_free_labs(school, course):
    print('执行查找空闲实验室函数------------------------------------' * 2)
    attribute = course.attribute
    student_sum = 0  # 该门课的学生总人数
    for classes_item in course.classes.all():
        student_sum = student_sum + classes_item.amount

    # 被占用的实验室们
    aready_in_used_labs = []

    for schdule_item in Schedule.objects.filter(experiment__course=course):
        for same_time_schdule in Schedule.objects.filter(which_week=schdule_item.which_week,
                                                         days_of_the_week=schdule_item.days_of_the_week,
                                                         section=schdule_item.section):
            if same_time_schdule.lab not in aready_in_used_labs:
                aready_in_used_labs.append(same_time_schdule.lab)

    # 所有开放的实验室
    all_dispark_labs = get_all_labs_dispark(school)
    # 所有空闲的实验室们
    all_free_labs = []

    for free_lab in all_dispark_labs:
        if free_lab not in aready_in_used_labs:
            all_free_labs.append(free_lab)

    # 最终获取的空闲实验室们
    free_labs = []
    success = False

    # 有空闲实验室才干活
    if all_free_labs:

        # 获取匹配实验室的方式：通过属性1和容纳人数来获取，并且实验室是连续的
        i = 0
        while not success:
            if i >= len(all_free_labs):
                break

            if attribute == all_free_labs[i].attribute1:
                free_labs.append(all_free_labs[i])
                print('找到合适的实验室：', free_labs)

                # 目前所得到的符合情况的实验室的容纳人数总和：
                temp_sum = 0
                for lab in free_labs:
                    temp_sum = temp_sum + lab.number_of_people

                if temp_sum >= student_sum:
                    success = True
                    print('处理课程：', course, '。通过属性1和容纳人数找到合适的连续实验室')
            else:
                free_labs.clear()
                print('处理课程：', course, '。没有连续的包含该课程属性的空闲实验室，清空原来获取到的实验室')

            i = i + 1

        # 获取匹配实验室的方式：通过属性2和容纳人数来获取，并且实验室是连续的
        i = 0
        while not success:
            if i >= len(all_free_labs):
                break

            if attribute == all_free_labs[i].attribute2:
                free_labs.append(all_free_labs[i])
                print('找到合适的实验室：', free_labs)

                # 目前所得到的符合情况的实验室的容纳人数总和：
                temp_sum = 0
                for lab in free_labs:
                    temp_sum = temp_sum + lab.number_of_people

                if temp_sum >= student_sum:
                    success = True
                    print('处理课程：', course, '。通过属性2和容纳人数找到合适的连续实验室')
            else:
                free_labs.clear()
                print('处理课程：', course, '。没有连续的包含该课程属性的空闲实验室，清空原来获取到的实验室')

            i = i + 1

        # 获取匹配实验室的方式：通过属性3和容纳人数来获取，并且实验室是连续的
        i = 0
        while not success:
            if i >= len(all_free_labs):
                break

            if attribute == all_free_labs[i].attribute3:
                free_labs.append(all_free_labs[i])
                print('找到合适的实验室：', free_labs)

                # 目前所得到的符合情况的实验室的容纳人数总和：
                temp_sum = 0
                for lab in free_labs:
                    temp_sum = temp_sum + lab.number_of_people

                if temp_sum >= student_sum:
                    success = True
                    print('处理课程：', course, '。通过属性3和容纳人数找到合适的连续实验室')
            else:
                free_labs.clear()
                print('处理课程：', course, '。没有连续的包含该课程属性的空闲实验室，清空原来获取到的实验室')

            i = i + 1

        if success:
            return free_labs
    return None


# 做出前端排课结果表格所需的json数据
def schedule(request, school_id=None):
    data = {
        "total": 1,
        "rows": []
    }

    school = School.objects.get(id=school_id)

    # set_suitable_and_schedule(school)

    labs = get_all_labs_dispark(school)
    # courses = get_all_courses(school)

    # 先生成一个一周内应有的星期和节次的空字典
    # 一般学校的每天都是11节对吧？
    # 该字典的格式应该为：{"d1_s1":{"days_of_the_week": days_of_the_week, "section": section, "xxx":""}, }， 键表示星期几的第几节

    # 基础空数据
    base_dict = {}
    for days_of_the_week in range(1, 8):
        for section in range(1, 12):
            new_dict = {"days_of_the_week": days_of_the_week, "section": section}
            for lab in labs:
                new_dict["%s" % lab.name] = ""
            base_dict["d%d_s%d" % (days_of_the_week, section)] = new_dict

    all_schedules = Schedule.objects.filter(school=school)

    div = '<div class="course_div">%s</div>'
    for schedule_item in all_schedules:
        # new_div = div % schedule_item.experiment.course.name
        new_div = div % schedule_item.experiment.course.name
        if new_div not in base_dict["d%d_s%d" % (schedule_item.days_of_the_week, schedule_item.section)][
            "%s" % schedule_item.lab.name]:
            base_dict["d%d_s%d" % (schedule_item.days_of_the_week, schedule_item.section)][
                "%s" % schedule_item.lab.name] = \
                base_dict["d%d_s%d" % (schedule_item.days_of_the_week, schedule_item.section)][
                    "%s" % schedule_item.lab.name] + new_div

    data['rows'] = list(base_dict.values())

    empty_row = {"days_of_the_week": "", "section": ""}
    for lab in labs:
        empty_row["%s" % lab.name] = ""
    data['rows'].insert(0, empty_row)

    # print('整理后，前端所需要的json数据：\n', data['rows'])

    return JsonResponse(data)


def adjust_labs_for_schedule(request):
    data = json.loads(list(request.POST.keys())[0])

    context = {
        'status': True,
        'message': None,
    }

    if request.is_ajax():
        try:
            course = Course.objects.get(id=data['course_id'])
            Schedule.objects.filter(experiment__course=course).delete()

            selected_labs = []
            for lab_id in data['selected_labs_id']:
                selected_labs.append(Lab.objects.get(id=lab_id))

            school = SuperUser.objects.get(account=request.session.get('user_account')).school
            create_schedule_for_course(school, course, selected_labs)

        except:
            context['status'] = False
            context['message'] = '修改失败，请重试'

        return JsonResponse(context)
