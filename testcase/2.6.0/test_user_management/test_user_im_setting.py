# -*- coding:utf-8 -*-
# @author  : ywt
# @file   : test_user_im_setting.py
# @ide    : PyCharm
# @time    : 2021/4/1 10:27

import pytest,json
from lib.im_api_lib.user import user_detail
from common.read_excel_data import get_excel_data
from common.my_log import my_log
import allure


# @allure.story("用户设置信息接口")
# @pytest.mark.parametrize("inData,repsData", get_excel_data('../data/im/ZXIM接口测试用例-v1.0.xls','用户管理模块','user_im_setting'))
# def test_user_im_setting(start_demo,inData, repsData):
#     token = start_demo
#     print(test_user_im_setting(token))