import json
from datetime import datetime

from django.http import JsonResponse, HttpResponseRedirect, QueryDict
from django.shortcuts import render
from django.views import View

from apps.manage.models import School, SchoolArea, Institute, Department, Grade, SuperUser, Classes, Teacher, \
    SchoolYear, Term, Course, LabsAttribute, Lab, Experiment, ExperimentType, CourseBlock, ArrangeSettings

from logging_setting import ThisLogger
from manage.tools.string_tool import list_to_str, str_to_set

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
        # 设计10个可用的颜色
        color_divs = ['green1_div', 'blue4_div', 'green4_div', 'blue1_div', 'green5_div', 'blue2_div', 'green2_div', 'blue3_div', 'blue5_div', 'green3_div']
        temp = divmod(len(courses), len(color_divs))
        color_divs = color_divs * temp[0] + color_divs[:temp[1]]

        for course, color_div in zip(courses, color_divs):
            course_blocks = CourseBlock.objects.filter(course=course)
            for course_block in course_blocks:
                if course_block.need_adjust:
                    new_div = need_adjust_div % (color_div, (course.name + '<br>周次[' + course_block.weeks + ']' + get_classes_name_from_course(course.id)))
                else:
                    new_div = div % (color_div, (course.name + '<br>周次[' + course_block.weeks + ']' + get_classes_name_from_course(course.id)))

                for section in course_block.sections.split(','):
                    for lab in course_block.new_labs.all():
                        if new_div not in base_dict['d%d_s%s' % (course_block.days_of_the_week, section)]['%s' % lab.name]:
                            base_dict['d%d_s%s' % (course_block.days_of_the_week, section)]['%s' % lab.name] = base_dict['d%d_s%s' % (course_block.days_of_the_week, section)]['%s' % lab.name] + new_div

        self.data['rows'] = [empty_row] + list(base_dict.values())
        # print('整理后，前端所需要的json数据：\n', self.data['rows'])
        return JsonResponse(self.data)


# 为前端页面定制的获取课程的班级信息函数
def get_classes_name_from_course(course_id):
    all_classes_str = ''
    for classes_item in Course.objects.get(id=course_id).classes.all():
        all_classes_str = all_classes_str + '<br>' + classes_item.grade.name + '级' + classes_item.grade.department.name + classes_item.name + '班'
    return all_classes_str









# 为前端设计的获取可选实验室的函数
def get_available_labs_for_course_block(institute_id, course_block):
    all_labs = list(Lab.objects.filter(institute_id=institute_id, dispark=True))
    # 找同一个星期的课程块进行周次的比较
    same_day_course_blocks = CourseBlock.objects.filter(course__institute_id=institute_id, days_of_the_week=course_block.days_of_the_week)
    sections = set(course_block.sections.split(','))
    conflic_blocks = []
    for block in same_day_course_blocks:
        its_sections = block.sections.split(',')
        if sections.intersection(set(its_sections)):
            conflic_blocks.append(block)

    aready_used_labs = []
    for block in conflic_blocks:
        for lab in block.new_labs.all():
            if lab not in aready_used_labs:
                aready_used_labs.append(lab)
    for lab in aready_used_labs:
        all_labs.remove(lab)
    free_labs = all_labs + list(course_block.new_labs.all())
    return free_labs


def the_sort(course_blocks, tag):
    print(tag)
    for x in course_blocks:
        print('课程名称：', x, ' 人数：', x.student_sum)


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
    for current_attribute in current_attributes:
        free_labs = []
        for lab in all_labs:
            if getattr(lab, current_attribute) == course_attribute:
                if not lab_in_used(lab, course_block):
                    free_labs.clear()
                else:
                    free_labs.append(lab)
                    if get_labs_contain_num(free_labs) >= course_block.student_sum:
                        print('为课程块：', course_block, '找到实验室：', free_labs)
                        return free_labs
            else:
                free_labs.clear()
    print('课程块：', course_block, '找不到实验室：')
    return None


def lab_in_used(lab, course_block):
    """
    判断符合某个课程块的某个实验室是否被占用
    :param lab: 要判断的实验室（单个）
    :param course_block: 要对比的课程块（单个）
    :return: 被占用则返回True，否则返回False
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
                    return False
    print('没有被占用')
    return True


def auto_arrange(institute_id, attribute1_id, attribute2_id):
    # 该学院的所有课程块
    all_course_blocks = CourseBlock.objects.filter(course__institute_id=institute_id)
    # 每次排课前，一定要先将所有课程块的新实验室删掉
    for course_block in all_course_blocks:
        course_block.new_labs.clear()
        course_block.save()

    # 最优先排课的课程块
    course_blocks1 = all_course_blocks.filter(course__attribute_id=attribute1_id).order_by('student_sum')
    # 次优先排课的课程块
    course_blocks2 = all_course_blocks.filter(course__attribute_id=attribute2_id).order_by('student_sum')

    def get_student_sum(x):
        return x.student_sum
    # 剩下的课程块
    course_blocks3 = list(set(all_course_blocks) - set(course_blocks1) - set(course_blocks2))
    course_blocks3.sort(reverse=True, key=get_student_sum)

    # 打印看看有没有出错：
    the_sort(course_blocks1, '最优先排课课程块：')
    the_sort(course_blocks2, '次优先排课课程块：')
    the_sort(course_blocks3, '剩下的课程块：')

    for course_blocks in [course_blocks1, course_blocks2, course_blocks3]:
        for course_block in course_blocks:
            print('为课程块', course_block, '寻找实验室')
            result_labs = find_labs(institute_id, course_block)
            if result_labs:
                for lab in result_labs:
                    course_block.new_labs.add(lab)
                course_block.need_adjust = False
            else:
                course_block.need_adjust = True
                for lab in course_block.old_labs.all():
                    course_block.new_labs.add(lab)
            course_block.save()


class Arrange(View):
    context = {
        'title': '实验类型设置',
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

        self.context['institutes'] = get_all_institutes(self.context['school'])
        self.context['attributes'] = LabsAttribute.objects.filter(school=self.context['school'])

        # 为用户记住最近编辑的学院
        if request.GET.get('current_institute_id'):
            request.session['current_institute_id'] = request.GET.get('current_institute_id')
        elif not request.GET.get('current_institute_id') and not request.session.get('current_institute_id', None):
            request.session['current_institute_id'] = self.context['institutes'][0].id

        # 为用户记住当前编辑学院排课设置的属性
        arrange_settings = ArrangeSettings.objects.filter(institute_id=request.session['current_institute_id'])
        if arrange_settings:
            request.session['current_attribute1_id'] = arrange_settings[0].attribute1_id
            request.session['current_attribute2_id'] = arrange_settings[0].attribute2_id
        else:
            request.session['current_attribute1_id'] = self.context['attributes'][0].id
            request.session['current_attribute2_id'] = self.context['attributes'][0].id

        request.session['arrange_settings'] = {
            'institute_%s' % request.session['current_institute_id']: {
                'attribute1_id': request.session['attribute1_id'],
                'attribute2_id': request.session['attribute2_id']
            }
        }

        self.context['labs'] = Lab.objects.filter(institute_id=request.session['current_institute_id'], dispark=True)
        courses = Course.objects.filter(institute_id=request.session['current_institute_id'])
        self.context['need_adjust_course_blocks'] = self.set_course_blocks(courses, True, request.session['current_institute_id'])
        self.context['no_need_adjust_course_blocks'] = self.set_course_blocks(courses, False, request.session['current_institute_id'])

        return render(request, 'manage/arrange.html', self.context)

    # 生成前端人工调整课程块列表的数据的方法
    def set_course_blocks(self, the_courses, need_adjust, institute_id):
        blocks_list = []
        i = 0
        for course in the_courses:
            course_blocks = CourseBlock.objects.filter(course=course, need_adjust=need_adjust)
            for course_block in course_blocks:
                i = i + 1
                new_dict = {
                    "no": i,
                    "course_block": course_block,
                    "classes": get_classes_name_from_course(course_block.course.id),
                    "free_labs": get_available_labs_for_course_block(institute_id, course_block)
                }
                blocks_list.append(new_dict)
        return blocks_list

    def post(self, request):  # 创建
        print(self.context)
        return render(request, 'manage/arrange.html', self.context)

    def put(self, request):  # 更新
        put_data = QueryDict(request.body)
        attribute1_id = put_data.get('attribute1_id')
        attribute2_id = put_data.get('attribute2_id')

        change = False
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

            auto_arrange(request.session['current_institute_id'], attribute1_id, attribute2_id)

        return render(request, 'manage/arrange.html', self.context)
