from copy import copy

def list_order(orig_list):

    sorted_list = copy(orig_list)
    sorted_list.sort()

    order_list = []
    prev_val = sorted_list[0]
    prev_id = orig_list.index(prev_val)
    order_list.append(prev_id)
    copy_list = copy(orig_list)
    repeat_num = 0

    for val in sorted_list[1:]:

        id = orig_list.index(val)

        if id==prev_id:
            copy_list.pop(id)
            repeat_num += 1
            prev_id = copy_list.index(val) + repeat_num
            order_list.append(prev_id)
        else:
            order_list.append(id)
            prev_id = id
            copy_list = copy(orig_list)
            repeat_num = 0

    return order_list

def order_for_val(list_of_lists, match_value, level=0):
    match_list = []
    for i, val in enumerate(list_of_lists[level]):
        if match_value == val:
            match_list.append(i)
    if len(match_list) == 0:
        return 0, None
    elif len(match_list) == 1:
        return 1, match_list[0]
    elif len(list_of_lists) == 1:
        return 2, match_list
    else:
        next_level_list = []
        for old_list in list_of_lists[1:]:
            new_list = []
            for id in match_list:
                new_list.append(old_list[id])
            next_level_list.append(new_list)
        return 2, order_for_level(next_level_list, reposition = match_list)

def order_for_level(list_of_lists, reposition=None):
    count = 0
    export_order_list = []
    order_list = list_order(list_of_lists[0])
    for id, pos in enumerate(order_list):
        if id < count:
            continue
        else:
            # print('{} -- {}'.format(list_of_lists, list_of_lists[0][pos]))
            res, value = order_for_val(list_of_lists, list_of_lists[0][pos])
            # print(value)
            if reposition is not None:
                print('{} -- {} -- {} -- {}'.format(list_of_lists, reposition, list_of_lists[0][pos], value))
            if res == 0:
                continue
            elif res == 1:
                if reposition is not None:
                    print(order_list, id)
                    value = reposition[value]
                export_order_list.append(value)
                count += 1
            elif res == 2:
                for val in value:
                    export_order_list.append(val)
                count += len(value)
            else:
                print('Unknown res: {}'.format(res))
                raise Exception()
    return export_order_list

list_1 = [1,3,5,6,2,6,8,3]
list_2 = [5,3,0,7,0,1,9,3]

correct = [0,4,7,1,2,5,3,6]

list_of_lists = [list_1, list_2]

print(order_for_level(list_of_lists))
