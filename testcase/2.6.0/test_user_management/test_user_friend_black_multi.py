# -*- coding:utf-8 -*-
# @author  : ywt
# @file   : test_user_friend_black_multi.py
# @ide    : PyCharm
# @time    : 2021/3/30 19:41
import pytest
import allure

from lib.im_api_lib.user import user_friend_add_req  # 添加好友接口
from lib.im_api_lib.user import user_friend_black_multi  # 将好友拉入黑名单接口
from lib.im_api_lib.user import user_black_list  # 黑名单列表接口
from lib.im_api_lib.user import user_friend_del_all  # 删除所有好友接口
from lib.im_api_lib.user import user_friend_black_multi_remove_all  # 将所有人移除黑名单接口
from common.my_log import my_log
from config.conf import user2_info, user3_info, user4_info, user5_info
from lib.im_api_lib.login import login
from lib.im_api_lib.user import user_friend_invite_auto_accept


@allure.feature("好友加入黑名单接口")
class TestUserFriendBlackMulti:
    def setup_class(self):
        """
        类级别的初始化，user2和user3,user4设置自动添加好友
        :return:
        """
        self.remake = "群邀请备注说明"
        self.source = "SEARCH"
        self.error_user_id = "ddjtsshty4avjpkpqqyya"
        self.token_2 = login(user2_info)
        self.token_3 = login(user3_info)
        self.token_4 = login(user4_info)
        user_friend_invite_auto_accept(self.token_2, auto=True)
        user_friend_invite_auto_accept(self.token_3, auto=True)
        user_friend_invite_auto_accept(self.token_4, auto=True)

    @pytest.fixture(scope="class", autouse=True)
    def before_step_1(self, start_demo):
        """
        类级别的初始化
        1：user1删除全部好友
        2：user1将所有人都移除黑名单
        3：user1添加user2和user3,user4为好友
        类级别的清除
        1：user1删除所有的好友
        2：user1情况黑名单列表
        :param start_demo:
        :return:
        """
        token_1 = start_demo
        user_friend_del_all(token_1)
        user_friend_black_multi_remove_all(token_1)
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

    @allure.story("将单个好友加入黑名单场景")
    @allure.title("test_add_single_user_friend_black_multi")
    def test_add_single_user_friend_black_multi(self, start_demo):
        """
        1:user1把一个好友user2加入黑名单
        2:断言user1把user2加入黑名单成功code = 0
        3：断言user2的id在user1查询出来的黑名单列表里，断言black_lists黑名单列表长度 == 1
        :param start_demo:
        :return:
        """
        token_1 = start_demo
        res = user_friend_black_multi(token_1, user_ids=user2_info["user_id"])
        my_log('test_add_single_user_friend_black_multi',
               {"userIds": user2_info["user_id"]}, res)
        assert res['code'] == "0"
        black_lists = [i['userId'] for i in user_black_list(token_1)['data']]
        assert user2_info["user_id"] in black_lists and len(black_lists) == 1

    @allure.story("将多个好友加入黑名单场景")
    @allure.title("test_add_multiple_user_friend_black_multi")
    def test_add_multiple_user_friend_black_multi(self, start_demo):
        """
        1: user1将user2和user3，user4加入黑名单
        2:断言user1把user2,user3和user4加入黑名单成功code = 0
        3：断言user2,user3,user4的id在user1查询出来的黑名单列表里，
          断言black_lists黑名单列表长度 == 3
        :param start_demo:
        :return:
        """
        token_1 = start_demo
        res = user_friend_black_multi(token_1,
                                      user_ids=f"{user2_info['user_id']},{user3_info['user_id']},{user4_info['user_id']}")
        my_log('test_add_multiple_user_friend_black_multi',
               {"userIds": f"{user2_info['user_id']},{user3_info['user_id']},{user4_info['user_id']}"}, res)
        assert res['code'] == "0"
        black_lists = [i['userId'] for i in user_black_list(token_1)['data']]
        assert len(black_lists) == 3
        assert user2_info["user_id"] in black_lists
        assert user3_info["user_id"] in black_lists
        assert user4_info["user_id"] in black_lists

    @allure.story("将非好友加入黑名单场景")
    @allure.title("test_add_non_friends_friend_black_multi")
    def test_add_non_friends_friend_black_multi(self, start_demo):
        """
        1: user1将非好友user5加入黑名单
        2: 断言加入黑名单成功code = 0，断言非好友user5的id在user1的黑名单列表里
        :param start_demo:
        :return:
        """
        token_1 = start_demo
        res = user_friend_black_multi(token_1,
                                      user_ids=user5_info["user_id"])
        my_log("test_add_non_friends_friend_black_multi",
               {"userIds": user5_info["user_id"]}, res)
        assert res['code'] == "0"
        black_lists = [i['userId'] for i in user_black_list(token_1)['data']]
        assert user5_info["user_id"] in black_lists

    @allure.story("将随意的一串非用户id的字符加入黑名单场景")
    @allure.title("test_add_non_users_friend_black_multi")
    def test_add_non_users_friend_black_multi(self, start_demo):
        """
        1: user1将非用户加入黑名单
        2: user1将非用户加入黑名单失败返回code = 1，断言黑名单列表没有这个非用户id
        :param start_demo:
        :return:
        """
        token_1 = start_demo
        res = user_friend_black_multi(token_1,
                                      user_ids=self.error_user_id)
        my_log("test_add_non_users_friend_black_multi",
               {"userIds": self.error_user_id}, res)
        assert res["code"] == "1"
        black_lists = [i['userId'] for i in user_black_list(token_1)['data']]
        assert self.error_user_id not in black_lists

