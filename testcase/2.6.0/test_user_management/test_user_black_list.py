# -*- coding:utf-8 -*-
# @author  : ywt
# @file   : test_user_black_list.py
# @ide    : PyCharm
# @time    : 2021/3/31 13:59
import pytest
import allure

from lib.im_api_lib.user import user_friend_add_req                     # 添加好友接口
from lib.im_api_lib.user import user_friend_black_multi                 # 将好友拉入黑名单接口
from lib.im_api_lib.user import user_black_list                         # 黑名单列表接口
from lib.im_api_lib.user import user_friend_del_all                     # 删除所有好友接口
from lib.im_api_lib.user import user_friend_black_multi_remove_all      # 将所有人移除黑名单接口
from lib.im_api_lib.user import user_friend_invite_auto_accept          # 设置自动加好友接口
from lib.im_api_lib.login import login
from common.my_log import my_log
from config.conf import user2_info, user3_info, user4_info, user5_info


@allure.feature("黑名单列表接口")
class TestUserBlackList:
    def setup_class(self):
        """
        类测试用例的前置，user2,user3,user4设置自动添加好友
        :return:
        """
        self.token_2 = login(user2_info)
        self.token_3 = login(user3_info)
        self.token_4 = login(user4_info)
        self.remake = "群邀请备注说明"
        self.source = "SEARCH"
        self.error_user_id = "ddjtsshty4avjpkpqqyya"
        user_friend_invite_auto_accept(self.token_2, auto=True)
        user_friend_invite_auto_accept(self.token_3, auto=True)
        user_friend_invite_auto_accept(self.token_4, auto=True)

    @pytest.fixture(scope="class", autouse=True)
    def before_step_1(self, start_demo):
        """
        类级别的初始化
        1：user1删除所有的好友
        2：user1添加user2,user3,user4为好友
        类级别的清除
        1：user1删除所有的好友
        2：user1情况黑名单列表
        :param start_demo:
        :return:
        """
        token_1 = start_demo
        user_friend_del_all(token_1)
        user_friend_add_req(token_1,
                            user_id=user2_info["user_id"],
                            remark=self.remake,
                            source=self.source)
        user_friend_add_req(token_1,
                            user_id=user3_info["user_id"],
                            remark=self.remake,
                            source=self.source)
        user_friend_add_req(token_1,
                            user_id=user4_info["user_id"],
                            remark=self.remake,
                            source=self.source)
        yield
        user_friend_del_all(token_1)
        user_friend_black_multi_remove_all(token_1)

    @pytest.fixture(scope="function", autouse=True)
    def before_step_2(self, start_demo):
        """
        函数级别的初始化
        1:每个测试用例执行之前都把当前账户的将所有人都移除黑名单
        :param start_demo:
        :return:
        """
        token_1 = start_demo
        user_friend_black_multi_remove_all(token_1)

    @allure.story("将单个好友加入黑名单,查看黑名单列表场景")
    @allure.title("test_add_single_friend_user_black_list")
    def test_add_single_friend_user_black_list(self, start_demo):
        """
        1:user1将单个好友user2加入黑名单后查询黑名单列表
        2：断言user1查询黑名单列表成功返回code=0
        3：断言user1的黑名单列表里面有且仅有user2
        :param start_demo:
        :param before_test:
        :return:
        """
        token_1 = start_demo
        user_friend_black_multi(token_1, user_ids=user2_info["user_id"])
        reps = user_black_list(token_1)
        my_log("test_add_single_friend_user_black_list",
               token_1, reps)
        assert reps['code'] == "0"
        black_lists = [i['userId'] for i in reps['data']]
        assert [user2_info["user_id"]] == black_lists

    @allure.story("将多个好友加入黑名单,查看黑名单列表场景")
    @allure.title("test_add_multiple_friend_user_black_list")
    def test_add_multiple_friend_user_black_list(self, start_demo):
        """
        1:user1将多个好友user2,user3,user4加入黑名单后查询黑名单列表
        2:断言查询出来的黑名单列表的长度=3，断言user2,user3,user4四个用户的user_id都在黑名单列表里
        :param start_demo:
        :return:
        """
        token_1 = start_demo
        user_friend_black_multi(token_1,
                                user_ids=f"{user2_info['user_id']},{user3_info['user_id']},{user4_info['user_id']}")
        reps = user_black_list(token_1)
        my_log("test_add_multiple_friend_user_black_list",
               token_1, reps)
        black_lists = [i['userId'] for i in reps['data']]
        assert len(black_lists) == 3
        for user in [user2_info, user3_info, user4_info]:
            assert user['user_id'] in black_lists

    @allure.story("将非好友加入黑名单,查看黑名单列表")
    @allure.title("test_add_non_friend_user_black_list")
    def test_add_non_friend_user_black_list(self, start_demo):
        """
        1:user1把非好友user5加入黑名单后查询黑名单列表
        2:断言查询黑名单列表成功code = 0，断言user1的黑名单列表里有user5的id
        :param start_demo:
        :return:
        """
        token_1 = start_demo
        user_friend_black_multi(token_1,
                                user_ids=f"{user5_info['user_id']}")
        reps = user_black_list(token_1)
        my_log("test_add_non_friend_user_black_list",
               token_1, reps)
        black_lists = [i['userId'] for i in reps['data']]
        assert reps["code"] == "0"
        assert user5_info["user_id"] in black_lists

    @allure.story("将非用户id的字符加入黑名单，查看黑名单列表")
    @allure.title("test_add_non_users_user_black_list")
    def test_add_non_users_user_black_list(self, start_demo):
        """
        1:user1把随意的一串非用户id的字符加入黑名单，查看黑名单列表
        2:断言user1查询黑名单列表成功返回的code=0，断言user1当前的黑名单列表为空
        :param start_demo:
        :return:
        """
        token_1 = start_demo
        ret = user_friend_black_multi(token_1,
                                      user_ids=self.error_user_id)
        reps = user_black_list(token_1)
        my_log("test_add_non_users_user_black_list",
               token_1, reps)
        black_lists = [i['userId'] for i in reps['data']]
        assert reps['code'] == "0"
        assert black_lists == []
