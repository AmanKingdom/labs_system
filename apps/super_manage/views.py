from django.shortcuts import render

from apps.apply_experiments.views import set_user_for_context


def school_manage(request):
    context = {
        'title': '学校管理',
        'user': None,
        'superuser': None,
        'teacher': None,

        'school': None,
    }

    set_user_for_context(request.session['user_account'], context)

    context['school'] = context['superuser'].school

    return render(request, 'super_manage/school_manage.html', context)
