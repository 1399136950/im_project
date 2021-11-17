# -*- coding:utf-8 -*-
# @project : teacher_sq
# @author  : ywt
# @file   : read_txt_data.py
# @ide    : PyCharm
# @time    : 2021/4/6 15:12
import re


def read_txt_data(filedir):
    """
    从txt文件读取敏感词函数
    data_type = 0   匹配全部的中文
    data_type = 1   匹配全部的小写英文
    data_type = 2   匹配全部的大写英文
    data_type = 4   匹配首字母大写，其他字母小写
    data_type = 4   匹配全部的中+英，中文+特殊字符
    :param filedir:
    :param data_type:
    :return:
    """
    f = open(filedir, 'r', encoding='utf8')
    data = f.read().strip().split(";")

    # if data_type == 0:
    #     return [i.strip() for i in data if re.match("^[\u4e00-\u9fa5]+$", i)]
    #
    # elif data_type == 1:
    #     return [i.strip().lower() for i in data if re.match("^[a-zA-Z]+$", i)]
    #
    # elif data_type == 2:
    #     return [i.strip().upper() for i in data if re.match("^[a-zA-Z]+$", i)]
    #
    # elif data_type == 3:
    #     return [i.strip().capitalize() for i in data if re.match("^[a-zA-Z]+$", i)]
    #
    # elif data_type == 4:
    #     return [i.strip() for i in data if re.match("[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+\.?", i)]
    # elif data_type == 5:
    #     return set(data) - set([i.strip() for i in data if re.match("^[\u4e00-\u9fa5]+$", i)]) - set([i.strip() for i in data if re.match("^[a-zA-Z]+$", i)]) - set([i.strip() for i in data if re.match("[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+\.?", i)])
    # elif data_type == 5:
    #     return [i.strip() for i in data if re.match("(^[a-z A-Z]+[\u4e00-\u9fa5]+[a-z A-Z \u4e00-\u9fa5]*$)|(^[\u4e00-\u9fa5]+[a-z A-Z]+[a-z A-Z \u4e00-\u9fa5]*$)", i)]
    return tuple(data)


if __name__ == '__main__':
    print(read_txt_data('../data/im/sensitive_file/sensitive.txt'))


