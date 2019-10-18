
def list_to_str(list_data, tag):
    temp = ''
    for x in list_data:
        temp = temp + tag + str(x)
    tag_len = len(tag)
    return temp[tag_len:]


def str_to_set(str_data, tag):
    temp = []
    for x in str_data.split(tag):
        if x != tag:
            temp.append(x)
    return set(temp)


def get_labs_id_str(labs):
    labs_ids = ""
    for lab in labs:
        labs_ids = labs_ids + ',%d' % lab.id
    return labs_ids[1:]


def str_to_non_repetitive_list(str_data, tag):
    """
    给列表形式的字符串转化为列表并去重，并且不能改变原顺序，最后返回该列表
    :param str_data:
    :return:
    """
    str_list = str_data.split(tag)
    while '' in str_list:
        str_list.remove('')
    print(str_data, '字符串分割成列表后：', str_list)
    temp_list = list(set(str_list))
    temp_list.sort(key=str_list.index)
    return temp_list


def non_repetitive_strlist(str_data, tag):
    data_list = str_to_non_repetitive_list(str_data, tag)
    print('字符串 ', str_data, '转去重的列表后：', data_list)
    return list_to_str(data_list, tag)
