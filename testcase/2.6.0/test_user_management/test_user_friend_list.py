# -*- coding:utf-8 -*-
# @author  : ywt
# @file   : test_user_friend_list.py
# @ide    : PyCharm
# @time    : 2021/4/1 9:09
import pytest
import allure

from lib.im_api_lib.user import user_friend_del_all
from lib.im_api_lib.user import user_friend_add_req
from lib.im_api_lib.user import user_friend_list
from lib.im_api_lib.login import login
from common.my_log import my_log
from lib.im_api_lib.user import user_friend_invite_auto_accept
from config.conf import user2_info, user3_info, user4_info, user5_info


@allure.feature("好友列表接口")
class TestUserFriendList:
    def setup_class(self):
        """
        类级别的初始化，user2，user3，user4，user5设置自动添加好友
        :return:
        """
        self.token_2 = login(user2_info)
        self.token_3 = login(user3_info)
        self.token_4 = login(user4_info)
        self.token_5 = login(user5_info)
        self.error_user_id = "asjkdakjdwkajdajda"
        user_friend_invite_auto_accept(self.token_2, True)
        user_friend_invite_auto_accept(self.token_3, True)
        user_friend_invite_auto_accept(self.token_4, True)
        user_friend_invite_auto_accept(self.token_5, True)

    @pytest.fixture(scope="function", autouse=True)
    def before_func(self, start_demo):
        token_1 = start_demo
        user_friend_del_all(token_1)
        yield
        user_friend_del_all(token_1)

    @allure.story("添加一个用户好友列表查询场景")
    @allure.title("test_add_single_users_user_friend_list")
    def test_add_single_users_user_friend_list(self, start_demo):
        """
        1:user1添加user2为好友，然后查询user1的好友列表接口，断言查询成功code = "0"
        2:断言user2在在user1好友列表里面
        :param start_demo:
        :return:
        """
        token_1 = start_demo
        user_friend_add_req(token_1, user_id=user2_info["user_id"])
        res = user_friend_list(token_1)
        my_log('test_add_single_users_user_friend_list', "token1", res)
        assert res["code"] == "0"
        friends_lists = [i['userId'] for i in res['data']]
        assert user2_info["user_id"] in friends_lists

    @allure.story("用户好友为空查询好友列表场景")
    @allure.title("test_empty_friends_users_user_friend_list")
    def test_empty_friends_users_user_friend_list(self, start_demo):
        """
        1:用户好友为空查询好友列表场景,断言查询好友成功code=0，断言好友列表为空
        :param start_demo:
        :return:
        """
        token_1 = start_demo
        res = user_friend_list(token_1)
        my_log('test_empty_friends_users_user_friend_list', "token1", res)
        assert res["code"] == "0"
        friends_lists = [i['userId'] for i in res['data']]
        assert friends_lists == []

    @allure.story("添加多个用户好友列表查询场景")
    @allure.title("test_add_multiple_users_user_friend_list")
    def test_add_multiple_users_user_friend_list(self, start_demo):
        """
        1:user1添加user2，user3，user4，user5为好友
        2：断言user1查询好友列表成功code = 0，
          断言user2，user3，user4，user5的userid在user1查询好友列表里面
        :param start_demo:
        :return:
        """
        token_1 = start_demo
        user_friend_add_req(token_1, user_id=user2_info["user_id"])
        user_friend_add_req(token_1, user_id=user3_info["user_id"])
        user_friend_add_req(token_1, user_id=user4_info["user_id"])
        user_friend_add_req(token_1, user_id=user5_info["user_id"])
        res = user_friend_list(token_1)
        my_log('test_add_multiple_users_user_friend_list', "token1", res)
        assert res["code"] == "0"
        friends_lists = [i['userId'] for i in res['data']]
        assert user2_info["user_id"] in friends_lists
        assert user3_info["user_id"] in friends_lists
        assert user4_info["user_id"] in friends_lists
        assert user5_info["user_id"] in friends_lists

    @allure.story("添加不存在的用户好友列表查询场景")
    @allure.title("test_add_non_users_user_friend_list")
    def test_add_non_users_user_friend_list(self, start_demo):
        """
        1:添加不存在的用户查询好友列表场景,断言查询好友成功code=0，
          断言不存在的好友的id没有在user1好友列表里
        :param start_demo:
        :return:
        """
        token_1 = start_demo
        user_friend_add_req(token_1, user_id=self.error_user_id)
        res = user_friend_list(token_1)
        my_log('test_add_non_users_user_friend_list', "token1", res)
        assert res["code"] == "0"
        friends_lists = [i['userId'] for i in res['data']]
        assert self.error_user_id not in friends_lists
