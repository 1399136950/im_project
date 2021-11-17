# -*- coding:utf-8 -*-
# @author  : ywt
# @file   : test_user_search.py
# @ide    : PyCharm
# @time    : 2021/4/1 14:27
import json

import pytest
import allure

from lib.im_api_lib.user import user_base_info_set
from lib.im_api_lib.user import user_search
from lib.im_api_lib.user import user_detail
from common.read_excel_data import get_excel_data
from config.conf import user1_info, user2_info, user3_info, user4_info, user5_info
from lib.im_api_lib.login import login
from common.my_log import my_log


@allure.feature("搜索用户接口")
class TestUserSearch:
    def setup_class(self):
        """
        类级别的初始化动作，把user2和user3用户的昵称分别设置成user1的手机和user_id
        user4的昵称设置成  ”测试搜索用户接口专用昵称“
        :return:
        """
        self.token_2 = login(user2_info)
        self.token_3 = login(user3_info)
        self.token_4 = login(user4_info)
        self.token_5 = login(user5_info)
        self.error_search = "TUIasdb奥斯卡大奖__7_152626,异常搜索"
        user_base_info_set(self.token_4, nickname="测试搜索用户接口专用昵称")

    def teardown_class(self):
        """
        类级别的清除动作：把user2和user3用户的昵称设置为默认
        :return:
        """
        user_base_info_set(self.token_2, nickname="user2的默认昵称")
        user_base_info_set(self.token_3, nickname="user3的默认昵称")

    @allure.story("输入手机号码搜索用户场景")
    @allure.title("test_phone_user_search")
    @pytest.mark.parametrize("in_data,reps_data",
                             get_excel_data('../data/im/ZXIM接口测试用例-v1.0.xls',
                                            '用户管理模块',
                                            'test_phone_user_search'))
    def test_phone_user_search(self, start_demo, in_data, reps_data):
        """
        1:输入手机号码搜索用户场景，断言搜索的结果和预期相同，
        :param start_demo:
        :param in_data:
        :param reps_data:
        :return:
        """
        token_1 = start_demo
        res = user_search(token_1, keyword=in_data)
        my_log('test_phone_user_search', {"keyword": in_data}, res)
        assert res['msg'] == json.loads(reps_data)['msg']
        user_lists = [user['userId'] for user in res["data"]]
        expect_user_lists = [user['userId'] for user in json.loads(reps_data)["data"]]
        assert user_lists == expect_user_lists

    @allure.story("输入昵称字段搜索用户场景")
    @allure.title("test_nickname_user_search")
    @pytest.mark.parametrize("in_data,reps_data",
                             get_excel_data('../data/im/ZXIM接口测试用例-v1.0.xls',
                                            '用户管理模块',
                                            'test_nickname_user_search'))
    def test_nickname_user_search(self, start_demo, in_data, reps_data):
        """
        1:输入昵称搜索用户场景，断言搜索的结果和预期相同
        :param start_demo:
        :param in_data:
        :param reps_data:
        :return:
        """
        token_1 = start_demo
        res = user_search(token_1, keyword=in_data)
        my_log('test_nickname_user_search', {"keyword": in_data}, res)
        assert res['msg'] == json.loads(reps_data)['msg']
        user_lists = [user['userId'] for user in res["data"]]
        expect_user_lists = [user['userId'] for user in json.loads(reps_data)["data"]]
        assert user_lists == expect_user_lists

    @allure.story("输入userId搜索用户场景")
    @allure.title("test_user_id_user_search")
    @pytest.mark.parametrize("in_data,reps_data",
                             get_excel_data('../data/im/ZXIM接口测试用例-v1.0.xls',
                                            '用户管理模块',
                                            'test_user_id_user_search'))
    def test_user_id_user_search(self, start_demo, in_data, reps_data):
        """
        1:输入userId进行搜索场景，断言搜索的结果和预期相同
        :param start_demo:
        :param in_data:
        :param reps_data:
        :return:
        """
        token_1 = start_demo
        res = user_search(token_1, keyword=in_data)
        my_log('test_user_id_user_search', {"keyword": in_data}, res)
        assert res['msg'] == json.loads(reps_data)['msg']
        user_lists = [user['userId'] for user in res["data"]]
        expect_user_lists = [user['userId'] for user in json.loads(reps_data)["data"]]
        assert user_lists == expect_user_lists

    @allure.story("输入错误的数字,字母,下划线特殊字符组合的字段搜索用户场景")
    @allure.title("test_error_user_search")
    def test_error_user_search(self, start_demo):
        """
        1:输入错误的数字,字母,下划线特殊字符组合的字段进行搜索,
          断言搜索成功code = 0，断言搜索出来的是个空用户列表
        :param start_demo:
        :param in_data:
        :param reps_data:
        :return:
        """
        token_1 = start_demo
        res = user_search(token_1, keyword=self.error_search)
        my_log('test_error_user_search', {"keyword": self.error_search}, res)
        assert res['code'] == "0"
        user_lists = [user['userId'] for user in res["data"]]
        assert user_lists == []

    @allure.story("某账户手机号和另一个用户昵称相同搜索用户场景")
    @allure.title("test_phone_same_user_search")
    def test_phone_same_user_search(self, start_demo):
        """
        1:把user2的昵称设置和user1的phone一样.断言设置成功code=0
        2:账户手机号和另一个用户昵称相同搜索用户进行搜索,
          断言搜索成功code = 0，能搜索出多个用户信息
        :param start_demo:
        :return:
        """
        token_1 = start_demo
        ret = user_base_info_set(self.token_2, nickname=user1_info['phone_num'])
        assert ret["code"] == "1", "user2设置昵称和user1的phone相同设置失败"

    @allure.story("某账户userId和另一个用户昵称相同搜索用户场景")
    @allure.title("test_user_id_same_user_search")
    def test_user_id_same_user_search(self, start_demo):
        """
        1:把user3的昵称设置和user1的userid一样.断言设置成功code=0
        2:账户手机号和另一个用户昵称相同搜索用户进行搜索,
          断言搜索成功code = 0，能搜索出多个用户信息
        :param start_demo:
        :return:
        """
        token_1 = start_demo
        ret = user_base_info_set(self.token_3, nickname=user1_info['user_id'])
        assert ret["code"] == "1", "user2设置昵称和user1的user_id相同设置失败"
