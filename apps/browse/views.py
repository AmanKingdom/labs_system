from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views import View

from apps.browse.models import Assistant
from apps.manage.models import Teacher, SuperUser
from browse.forms import LoginForm

from manage.views import require_login

from apps.manage.views import this_logger


@require_login
def homepage(request):
    this_logger.debug('主页获取用户类型：' + request.session['user_type'])
    if request.session.get('user_type', None):
        if request.session['user_type'] == 'assistant':
            return HttpResponseRedirect('/browse/assistant_view')
        elif request.session['user_type'] == 'teacher':
            return HttpResponseRedirect('/apply_experiments/apply')
        elif request.session['user_type'] == 'superuser':
            return HttpResponseRedirect('/manage/school_manage')
    return HttpResponseRedirect('/browse/login')


# 只能是管理员注册，教师和学生不需要注册
class RegisterView(View):
    context = {
        'title': '注册',
        'status': True,
        'message': None,
    }

    def get(self, request):
        return render(request, 'browse/register.html', self.context)

    def post(self, request):
        name = request.POST.get('name', None)
        if name:
            account = request.POST.get('account', None)
            if account.startswith('1') and len(account) == 11:
                if SuperUser.objects.filter(account=account):
                    self.context['status'] = False
                    self.context['message'] = '该手机账号已被人注册'
                else:
                    password = request.POST.get('password', None)
                    if len(password) >= 6:
                        superuser = SuperUser.objects.create(name=name, account=account, password=password)
                        request.session['user_account'] = superuser.account
                        request.session['user_type'] = 'superuser'
                        request.session['user_id'] = superuser.id
                        request.session['user_name'] = superuser.name
                        this_logger.info(superuser.name + '超级管理员注册成功')
                    else:
                        self.context['status'] = False
                        self.context['message'] = '密码太短了'
            else:
                self.context['status'] = False
                self.context['message'] = '请输入正确的手机号码'
        else:
            self.context['status'] = False
            self.context['message'] = '请输入昵称'
        return JsonResponse(self.context)


class LoginView(View):
    context = {'title': '登录', 'message': None}

    def get(self, request):
        return render(request, 'browse/login.html', self.context)

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            def set_user_info_to_session(request, user_account, user_type, user_name, user_id):
                request.session['user_account'] = user_account
                request.session['user_type'] = user_type
                request.session['user_name'] = user_name
                request.session['user_id'] = user_id
            try:
                superuser = SuperUser.objects.get(**login_form.cleaned_data)
                this_logger.info(superuser.name + '超级管理员登录成功')
                set_user_info_to_session(request, superuser.account, 'superuser', superuser.name, superuser.id)
                # request.session['user_account'] = superuser.account
                # request.session['user_type'] = 'superuser'
                # request.session['user_name'] = superuser.name
                # request.session['user_id'] = superuser.id
                if superuser.school:
                    request.session['school_id'] = superuser.school_id

                return HttpResponseRedirect('/manage/school_manage')
            except SuperUser.DoesNotExist:
                try:
                    teacher = Teacher.objects.get(**login_form.cleaned_data)
                    this_logger.info(teacher.name + '教师登录成功')
                    set_user_info_to_session(request, teacher.account, 'superuser', teacher.name, teacher.id)

                    # request.session['user_account'] = teacher.account
                    # request.session['user_type'] = 'teacher'
                    # request.session['user_name'] = teacher.name
                    # request.session['user_id'] = teacher.id

                    # 教师所属的学校id由将来在前端登录时选择学校后传入

                    return HttpResponseRedirect('/apply_experiments/apply')
                except Teacher.DoesNotExist:
                    try:
                        assistant = Assistant.objects.get(**login_form.cleaned_data)
                        this_logger.info(assistant.name + '助理登录成功')
                        set_user_info_to_session(request, assistant.account, 'superuser', assistant.name, assistant.id)

                        # request.session['user_account'] = assistant.account
                        # request.session['user_type'] = 'assistant'
                        # request.session['user_name'] = assistant.name
                        # request.session['user_id'] = assistant.id

                        # 助理所属的学校id由将来在前端登录时选择学校后传入

                        return HttpResponseRedirect('/browse/assistant_view')
                    except Assistant.DoesNotExist:
                        this_logger.info('登录失败')

            self.context['message'] = '登录失败，请检查账号或重新输入密码'
        return render(request, 'browse/login.html', self.context)


@require_login
def assistant_view(request):
    return render(request, 'browse/assistant_view.html')


def logout(request):
    del request.session['user_account']
    del request.session['user_type']
    del request.session['user_name']
    del request.session['user_id']
    del request.session['school_id']
    return HttpResponseRedirect('/browse/login')
