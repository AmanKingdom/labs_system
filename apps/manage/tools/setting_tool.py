from datetime import datetime


def set_time_for_context(context):
    """
    为申请实验和修改实验页面提供的选项数据：周次、星期、节次
    :param context:
    :return:
    """
    # 周次
    context['which_week'] = [x for x in range(1, 21)]
    # 星期
    context['days_of_the_week'] = [x for x in range(1, 8)]
    # 节次
    context['section'] = [x for x in range(1, 12)]


# 设置本系统的唯一学年，当当前月份为8月份时，如果有超级管理员登录本系统，即可更新数据库的学年表的唯一一条学年数据
def set_system_school_year():
    from apps.manage.views import this_logger
    from apps.manage.models import SchoolYear
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
                this_logger.debug('学年有更新')
        else:
            if school_year.to != year_now:
                # 学年的结束年份不是当前年份，需要更新
                SchoolYear.objects.filter(id=school_year.id).update(since=year_now - 1, to=year_now)
                this_logger.debug('学年有更新')
    else:
        SchoolYear.objects.create(since=year_now, to=year_now + 1)
        this_logger.debug('创建了学年')
