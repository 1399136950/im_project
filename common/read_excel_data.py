# -*- coding:utf-8 -*-
# @author  : ywt
# @file   : read_excel_data.py
# @ide    : PyCharm
# @time    : 2021/3/26 13:39
import xlrd


def get_excel_data(excel_dir, sheet, info, body=7, reps=9):
    data = xlrd.open_workbook(excel_dir)
    table = data.sheet_by_name(sheet)
    res = table.col_values(0)
    count = []
    for i in range(len(res)):
        if info == res[i]:
            count.append(i)
    start_row = min(count)+1
    end_row = max(count)+1
    res_list = []
    for one in range(start_row-1, end_row):
        data_body = table.cell(one, body).value
        data_reps = table.cell(one, reps).value
        res_list.append((data_body, data_reps))
    return res_list


if __name__ == '__main__':
    print(get_excel_data('../data/im/ZXIM接口测试用例-v1.0.xls', '用户管理模块', 'user_avatar_update'))
