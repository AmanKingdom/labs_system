from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views import View

from browse.forms import LoginForm

from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, permission_required

from apps.manage.views import this_logger
from apps.manage.models import User
from apps.manage.views import MANAGER, TEACHER, STUDENT


@login_required(login_url='/browse/login')
def homepage(request):
    this_logger.debug('主页获取用户类型：' + request.session['user_type'])
    if request.session.get('user_type', None):
        return HttpResponseRedirect('/manage/weeks_timetable')
    return HttpResponseRedirect('/browse/login')


def set_user_info_to_session(request, username, user_type, user_name, user_id):
    request.session['user_account'] = username  # user_account是账号username，不是姓名，user_name才是姓名
    request.session['user_type'] = user_type
    request.session['user_name'] = user_name
    request.session['user_id'] = user_id

    role = User.objects.get(id=user_id).groups.all().first()
    """
    由于本系统的菜单只有二级，故菜单字典格式应该为：
    {'菜单id': {
        'name':'xxx', 
        'icon':'xxx', 
        'url':'xxx', 
        'children':[
            {
                'name':'xxx', 
                'icon':'xxx', 
                'url':'xxx',
            }
        ],
    ...}
    """
    menus = role.menus.all()
    menus_dict = {}

    def get_new_menu_dict(menu):
        return {
                    'name': menu.name,
                    'icon': menu.icon,
                    'url': menu.get_URL(),
                    'children': [],
                }
    this_logger.debug('用户'+username+'拥有的菜单有：'+str(menus))
    for menu in menus:
        if menu.parent:
            if str(menu.parent.id) not in menus_dict.keys():
                menus_dict['%d' % menu.parent.id] = get_new_menu_dict(menu.parent)
            menus_dict['%d' % menu.parent.id]['children'].append(get_new_menu_dict(menu))
        else:
            if str(menu.id) not in menus_dict.keys():
                menus_dict['%d' % menu.id] = get_new_menu_dict(menu)
    print('整理数据提供到前端：')
    for key, menu in menus_dict.items():
        print(menu['name'])
        if menu['children']:
            for m in menu['children']:
                print('----', m['name'])

    request.session['user_menus'] = menus_dict


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
            username = request.POST.get('username', None)
            if not User.objects.filter(username=username):
                password = request.POST.get('password', None)
                if len(password) >= 6:
                    user = User.objects.create_user(name=name, username=username, password=password)
                    user.groups.add(Group.objects.get(name=MANAGER))
                    user.save()

                    set_user_info_to_session(request, username, MANAGER, user.name, user.id)
                    this_logger.info(user.name + '管理员注册成功')
                else:
                    self.context['status'] = False
                    self.context['message'] = '这密码也太短了8'
            else:
                self.context['status'] = False
                self.context['message'] = '该账号已被注册'
        else:
            self.context['status'] = False
            self.context['message'] = '请输入姓名'
        return JsonResponse(self.context)


class LoginView(View):
    context = {'title': '登录', 'message': None}

    def get(self, request):
        return render(request, 'browse/login.html', self.context)

    def post(self, request):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            if User.objects.filter(username=login_form.cleaned_data['username']):
                user = authenticate(**login_form.cleaned_data)
                if user:
                    if user.is_active:
                        login(request, user)
                        this_logger.info(user.name + '登录成功')

                        if user.groups.all()[0].name == MANAGER:
                            set_user_info_to_session(request, user.username, MANAGER, user.name, user.id)
                            if user.school:
                                request.session['school_id'] = user.school_id
                        elif user.groups.all()[0].name == TEACHER:
                            set_user_info_to_session(request, user.username, TEACHER, user.name, user.id)
                            request.session['department_name'] = user.department.name
                        else:
                            set_user_info_to_session(request, user.username, STUDENT, user.name, user.id)

                        return HttpResponseRedirect('/')
                    else:
                        self.context['message'] = '该用户已被注销'
                else:
                    self.context['message'] = '密码错误'
            else:
                self.context['message'] = '此账号不存在'

        return render(request, 'browse/login.html', self.context)


@login_required
def assistant_view(request):
    return render(request, 'browse/assistant_view.html')


def logout_view(request):
    logout(request)

    return HttpResponseRedirect('/browse/login')
