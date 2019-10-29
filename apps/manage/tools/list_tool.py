def get_model_field_ids(model, field_name):
    """
    获取某个模型的某个多对多字段的所有数据的id
    :param model:
    :param field_name: 模型对应字段名称的字符串
    :return: 返回id列表
    """
    field = getattr(model, field_name)
    # print('获取到：', model, ' field:', field)
    temp = []
    for x in field.all():
        temp.append(x.id)
    return temp
