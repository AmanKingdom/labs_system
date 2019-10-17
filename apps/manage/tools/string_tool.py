
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
