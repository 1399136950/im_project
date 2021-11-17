# -*- coding:utf-8 -*-
# @author  : ywt
# @file   : test_user_avatar_update.py
# @ide    : PyCharm
# @time    : 2021/3/30 14:41
import json

import pytest
import requests
import allure

from lib.im_api_lib.user import user_avatar_update
from common.read_excel_data import get_excel_data
from common.my_log import my_log
from common.get_md5 import get_file_md5


@allure.feature("修改用户头像接口")
class TestUserAvatarUpdate:
    @allure.story("修改用户头像场景")
    @allure.title("test_user_avatar_update")
    @pytest.mark.skip("网速的贼慢跳过 test_user_avatar_update")
    @pytest.mark.parametrize("in_data,reps_data",
                             get_excel_data('../data/im/ZXIM接口测试用例-v1.0.xls',
                                            '用户管理模块',
                                            'test_user_avatar_update'))
    def test_user_avatar_update(self, start_demo, in_data, reps_data):
        """
        1:user1修改头像,修改后断言返回值是不是和预期相同
        2：如果象修改头像成功会返回code = 0和fileUrl，
          断言返回的fileUrl下载的文件的md5和我们上传文件的md5是不是一样
        3:如果修改头像失败断言失败的message等于预期的message
        :param start_demo:
        :param in_data:
        :param reps_data:
        :return:
        """
        token = start_demo
        reps = user_avatar_update(token, file_path=json.loads(in_data)["file_path"])
        my_log('test_user_avatar_update', in_data, reps)
        assert reps['msg'] == json.loads(reps_data)['msg']
        if reps['code'] == "0":
            ret = requests.get(reps['data']["fileUrl"]).content
            assert get_file_md5(ret) == get_file_md5(json.loads(in_data)["file_path"])
        else:
            assert reps["error"]["message"] == json.loads(reps_data)["error"]["message"]


