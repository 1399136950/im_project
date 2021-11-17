# -*- coding:utf-8 -*-
# @author  : ywt
# @file   : test_user_list.py
# @ide    : PyCharm
# @time    : 2021/4/1 19:55
import allure

from lib.im_api_lib.user import user_list
from common.my_log import my_log
from config.conf import user1_info, user2_info, user3_info, user4_info


@allure.feature("多用户信息接口")
class TestUserList:
    def setup_class(self):
        self.error_user_id = "123asdawdadadad"

    @allure.story("查询一个用户的信息场景")
    @allure.title("")
    def test_search_one_user_list(self, start_demo):
        """
        1:传入一个用户的信息进程查询，断言查询成功code=0，断言查询出来的结果的userid等于查询的userid
        :param start_demo:
        :return:
        """
        token_1 = start_demo
        res = user_list(token_1, user_ids=user2_info["user_id"])
        my_log('test_search_one_user_list',
               {"userIds": user2_info["user_id"]}, res)
        assert res["code"] == "0"
        assert res["data"][0]["userId"] == user2_info["user_id"]

    @allure.story("查询多个用户的信息场景")
    @allure.title("test_search_multiple_user_list")
    def test_search_multiple_user_list(self, start_demo):
        """
        1:传入三个用户的信息进行查询，断言查询成功code=0，
          断言查询出来的结果的用户列表里面包含传入的多个用户的id，断言查询出来的用户列表长度=3
        :param start_demo:
        :return:
        """
        token_1 = start_demo
        res = user_list(token_1,
                        user_ids=f'{user2_info["user_id"]},{user3_info["user_id"]},{user4_info["user_id"]}')
        my_log('test_search_multiple_user_list',
               {"userIds": f'{user2_info["user_id"]},{user3_info["user_id"]},{user4_info["user_id"]}'}, res)
        assert res["code"] == "0"
        user_lists = [user['userId'] for user in res['data']]
        assert len(user_lists) == 3
        assert user2_info["user_id"] in user_lists
        assert user3_info["user_id"] in user_lists
        assert user4_info["user_id"] in user_lists

    @allure.story("userIds传入为空查询用户信息场景")
    @allure.title("test_search_empty_user_list")
    def test_search_empty_user_list(self, start_demo):
        """
        1:传入userIds传入为空去查询用户信息
          断言查询失败code=1，断言查询失败的返回的message = '参数不合法'
        :param start_demo:
        :return:
        """
        token_1 = start_demo
        res = user_list(token_1, user_ids="")
        my_log('test_search_empty_user_list',
               {"userIds": ""}, res)
        assert res["code"] == "1"
        assert res["error"]["message"] == '参数不合法'

    @allure.story("传入userIds不存在的用户查询用户信息场景")
    @allure.title("test_search_error_user_list")
    def test_search_error_user_list(self, start_demo):
        """
        1:传入userIds不存在的用户去查询用户信息
          断言查询成功code=0，断言查询到的结果的data=[]
        :param start_demo:
        :return:
        """
        token_1 = start_demo
        res = user_list(token_1, user_ids=self.error_user_id)
        my_log('test_search_error_user_list',
               {"userIds": self.error_user_id}, res)
        assert res["code"] == "0"
        assert res["data"] == []

    @allure.story("user_ids传入不存在用户和存在的用户一起查询用户信息场景")
    @allure.title("test_search_normal_and_abnormal_user_list")
    def test_search_normal_and_abnormal_user_list(self, start_demo):
        """
        1:user_ids传入不存在用户和存在的用户一起查询用户信息
          断言查询成功code=0，断言查询到的结果的里包含存在的用户的id但是不包含不存在的用户的id
        :param start_demo:
        :return:
        """
        token_1 = start_demo
        res = user_list(token_1,
                        user_ids=f'{user2_info["user_id"]},{user3_info["user_id"]},{self.error_user_id}')
        my_log('test_search_normal_and_abnormal_user_list',
               {"userIds": f'{user2_info["user_id"]},{user3_info["user_id"]},{self.error_user_id}'}, res)
        assert res["code"] == "0"
        user_lists = [user['userId'] for user in res['data']]
        assert user2_info["user_id"] in user_lists
        assert user3_info["user_id"] in user_lists
        assert self.error_user_id not in user_lists

    @allure.story("传入当前用户自己的user_id查询用户信息场景")
    @allure.title("test_search_oneself_user_list")
    def test_search_oneself_user_list(self, start_demo):
        """
        1:传入当前用户自己的user_id查询用户信息
          断言查询成功code=0，断言查询出来的user_lists包含user1的id
        :param start_demo:
        :return:
        """
        token_1 = start_demo
        res = user_list(token_1, user_ids=user1_info["user_id"])
        my_log('test_search_oneself_user_list',
               {"userIds": self.error_user_id}, res)
        assert res["code"] == "0"
        user_lists = [user['userId'] for user in res['data']]
        assert user1_info["user_id"] in user_lists