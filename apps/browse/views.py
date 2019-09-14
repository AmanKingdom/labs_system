from django.http import HttpResponseRedirect, Http404, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from apps.browse.models import Assistant
from apps.super_manage.models import Teacher, SuperUser, School

from logging_setting import ThisLogger

this_logger = ThisLogger().logger


# 基础视图，检查登录
def require_login(view):
    def new_view(request, *args, **kwargs):
        if 'user_account' in request.session and 'user_type' in request.session:
            if not request.session['user_account'] or not request.session['user_type']:
                return HttpResponseRedirect('/browse/login')
            else:
                return view(request, *args, **kwargs)
        else:
            return HttpResponseRedirect('/browse/login')
    return new_view


def homepage(request):
    if request.session['user_type'] == 'assistant':
        return HttpResponseRedirect('/browse/assistant_view')
    elif request.session['user_type'] == 'teacher':
        return HttpResponseRedirect('/apply_experiments/personal_homepage')
    elif request.session['user_type'] == 'superuser':
        return HttpResponseRedirect('/super_manage/school_manage')
    else:
        return HttpResponseRedirect('/browse/login')


@csrf_exempt
def register(request):
    context = {
        'title': '注册',
        'status': True,
        'message': None,
    }
    if request.is_ajax():
        name = request.POST.get('name', None)
        if name:
            account = request.POST.get('account', None)
            if account.startswith('1') and len(account) == 11:
                if SuperUser.objects.filter(account=account):
                    context['status'] = False
                    context['message'] = '该手机账号已被人注册'
                else:
                    password = request.POST.get('password', None)
                    if len(password) >= 6:
                        superuser = SuperUser.objects.create(name=name, account=account, password=password)
                        request.session['user_account'] = superuser.account
                        request.session['user_type'] = 'superuser'
                        this_logger.info(superuser.name + '超级管理员注册并直接登录')
                    else:
                        context['status'] = False
                        context['message'] = '密码太短了'
            else:
                context['status'] = False
                context['message'] = '请输入正确的手机号码'
        else:
            context['status'] = False
            context['message'] = '请输入昵称'
    else:
        return render(request, 'browse/register.html', context)
    return JsonResponse(context)


@csrf_exempt
def set_school(request):
    context = {
        'title': '设置学校',
        'status': True,
        'message': None,
    }
    if request.is_ajax():
        school_name = request.POST.get('school_name', None)
        if school_name:
            if School.objects.filter(name=school_name):
                this_logger.info('已存在学校：' + school_name)
                context['status'] = False
                context['message'] = '该学校名称已经被人注册'
            else:
                school = School.objects.create(name=school_name)
                superuser = SuperUser.objects.get(account=request.session['user_account'])
                superuser.school = school
                superuser.save()
        else:
            context['status'] = False
            context['message'] = '请输入学校名称'
        return JsonResponse(context)
    else:
        return render(request, 'browse/set_school.html', context)


@csrf_exempt
def login(request):
    context = {'title': '登录', 'message': None}

    if request.method == 'POST':
        # 建议用get()获取，不要用['xxx']获取
        account = request.POST.get('account')
        password = request.POST.get('password')
        try:
            superuser = SuperUser.objects.get(account=account, password=password)
            if superuser:
                this_logger.info(superuser.name + '超级管理员登录成功')
                request.session['user_account'] = superuser.account
                request.session['user_type'] = 'superuser'
                return HttpResponseRedirect('/super_manage/school_manage')
        except:
            try:
                teacher = Teacher.objects.get(account=account, password=password)
                if teacher:
                    this_logger.info(teacher.name + '教师登录成功')
                    request.session['user_account'] = teacher.account
                    request.session['user_type'] = 'teacher'
                    return HttpResponseRedirect('/apply_experiments/apply')
            except:
                try:
                    assistant = Assistant.objects.get(account=account, password=password)
                    if assistant:
                        this_logger.info(assistant.name + '助理登录成功')
                        request.session['user_account'] = assistant.account
                        request.session['user_type'] = 'assistant'
                        return HttpResponseRedirect('/browse/assistant_view')
                except:
                    this_logger.info('登录失败')

        context['message'] = '登录失败，请检查账号或重新输入密码，助理忘记密码请向老师申请找回。'
    return render(request, 'browse/login.html', context)


def assistant_view(request):
    return render(request, 'browse/assistant_view.html')


def logout(request):
    request.session['user_account'] = None
    request.session['user_type'] = None
    return HttpResponseRedirect('/browse/login')
