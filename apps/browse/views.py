from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from apps.browse.models import Assistant
from apps.super_manage.models import Teacher

from logging_setting import ThisLogger

this_logger = ThisLogger().logger


def check_is_login(request):
    if 'user_account' in request.session and 'user_type' in request.session:
        if request.session['user_account'] and request.session['user_type']:
            this_logger.info(str(request.session['user_account']) + '已登录')
            if request.session['user_type'] == 'assistant':
                return 'assistant'
            else:
                return 'teacher'
    else:
        return 'need_login'


def homepage(request):
    flag = check_is_login(request)
    if flag == 'assistant':
        return HttpResponseRedirect('/browse/assistant_view')
    elif flag == 'teacher':
        return HttpResponseRedirect('/apply_experiments/apply')
    return HttpResponseRedirect('/browse/login')


@csrf_exempt
def login(request):
    context = {'title': '登录', 'message': None}

    if request.method == 'POST':
        account = request.POST['account']
        password = request.POST['password']
        try:
            assistant = Assistant.objects.get(account=account, password=password)
            if assistant:
                this_logger.info(assistant.name + '助理登录成功')
                request.session['user_account'] = assistant.account
                request.session['user_type'] = 'assistant'
                return HttpResponseRedirect('/browse/assistant_view')
        except:
            try:
                teacher = Teacher.objects.get(account=account, password=password)
                if teacher:
                    this_logger.info(teacher.name + '教师登录成功')
                    request.session['user_account'] = teacher.account
                    request.session['user_type'] = 'teacher'
                    return HttpResponseRedirect('/apply_experiments/apply')
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
