# -*- coding:utf-8 -*-
# @author  : ywt
# @file   : test_user_friend_search.py
# @ide    : PyCharm
# @time    : 2021/4/1 11:51
import pytest
import allure

from lib.im_api_lib.user import user_friend_search              # 查询好友接口
from lib.im_api_lib.user import user_friend_del_all             # 删除所有的好友
from lib.im_api_lib.user import user_friend_list                # 好友列表接口
from lib.im_api_lib.user import user_friend_add_req             # 添加好友接口
from lib.im_api_lib.user import user_friend_invite_auto_accept  # 设置自动加好友接口
from lib.im_api_lib.login import login
from config.conf import user1_info, user2_info, user3_info, user4_info, user5_info
from common.my_log import my_log


@allure.feature("查找好友接口")
class TestUserFriendSearch:
    def setup_class(self):
        """
        类级别的初始化，user2，user3，user4设置自动添加好友
        :return:
        """
        self.token_2 = login(user2_info)
        self.token_3 = login(user3_info)
        self.token_4 = login(user4_info)
        self.error_user_id = "asjkdakjdwkajdajda"
        user_friend_invite_auto_accept(self.token_2, True)
        user_friend_invite_auto_accept(self.token_3, True)
        user_friend_invite_auto_accept(self.token_4, True)

    @pytest.fixture(scope="class", autouse=True)
    def before_step_class(self, start_demo):
        """
        类级别的初始化：user1删除所有的好友，然后添加user2和user3，user4为好友
        类级别的清除：user1删除所有的好友
        :param start_demo:
        :return:
        """
        token = start_demo
        user_friend_del_all(token)
        user_friend_add_req(token,
                            user_id=user2_info["user_id"])
        user_friend_add_req(token,
                            user_id=user3_info["user_id"])
        user_friend_add_req(token,
                            user_id=user4_info["user_id"])
        yield token
        user_friend_del_all(token)

    @allure.story("使用好友的id字段进行查询场景")
    @allure.title("test_normal_friends_user_friend_search")
    def test_normal_friends_user_friend_search(self, start_demo):
        """
        1:传入user1的好友user2进行查询，断言查询正常code=0
          断言查询出来的结果的userid等于查询的，断言user2在user1的好友列表里
        :param start_demo:
        :return:
        """
        token = start_demo
        res = user_friend_search(token, user2_info["user_id"])
        my_log('test_normal_friends_user_friend_search',
               {"userId": user2_info["user_id"]}, res)
        assert res["code"] == "0"
        assert res['data']['userId'] == user2_info["user_id"]
        friend_lists = [i['userId'] for i in user_friend_list(token)["data"]]
        assert user2_info["user_id"] in friend_lists

    @allure.story("使用用户本人的id字段进行查询场景")
    @allure.title("test_oneself_friends_user_friend_search")
    def test_oneself_friends_user_friend_search(self, start_demo):
        """
        1:使用用户本人的id字段进行查询,断言查询失败返回code=1
          断言返回的结果的message='用户不存在'
        :param start_demo:
        :return:
        """
        token = start_demo
        res = user_friend_search(token, user1_info["user_id"])
        my_log('test_oneself_friends_user_friend_search',
               {"userId": user1_info["user_id"]}, res)
        assert res["code"] == "1"
        assert res["error"]["message"] == '用户不存在'

    @allure.story("使用不在好友列表的用户id进行查询场景")
    @allure.title("test_not_friends_user_friend_search")
    def test_not_friends_user_friend_search(self, start_demo):
        """
        1:使用不在好友列表的用户id字段进行查询,断言查询失败返回code=1
          断言返回的结果的message='用户不存在'
        :param start_demo:
        :return:
        """
        token = start_demo
        res = user_friend_search(token, user5_info["user_id"])
        my_log('test_not_friends_user_friend_search',
               {"userId": user5_info["user_id"]}, res)
        assert res["code"] == "1"
        assert res["error"]["message"] == '用户不存在'

    @allure.story("传入不存在的用户的id字段进行查询场景")
    @allure.title("test_not_user_user_friend_search")
    def test_not_user_user_friend_search(self, start_demo):
        token = start_demo
        res = user_friend_search(token, self.error_user_id)
        my_log('test_not_user_user_friend_search',
               {"userId": self.error_user_id}, res)
        assert res["code"] == "1"
        assert res["error"]["message"] == '用户不存在'
