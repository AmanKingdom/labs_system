def set_time_for_context(context):
    # 周次
    context['which_week'] = [x for x in range(1, 21)]
    # 星期
    context['days_of_the_week'] = [x for x in range(1, 8)]
    # 节次
    context['section'] = [x for x in range(1, 12)]
