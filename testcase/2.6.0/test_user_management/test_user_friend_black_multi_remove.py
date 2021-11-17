# -*- coding:utf-8 -*-
# @author  : ywt
# @file   : test_user_friend_black_multi_remove.py
# @ide    : PyCharm
# @time    : 2021/3/31 14:51
import pytest
import allure

from lib.im_api_lib.user import user_friend_black_multi                 # 将好友拉入黑名单接口
from lib.im_api_lib.user import user_black_list                         # 黑名单列表接口
from lib.im_api_lib.user import user_friend_black_multi_remove_all      # 将所有人移除黑名单接口
from lib.im_api_lib.user import user_friend_black_multi_remove
from common.my_log import my_log
from config.conf import user2_info, user3_info, user4_info, user5_info


@allure.feature("好友移出黑名单接口")
class TestUserFriendBlackMultiRemove:
    @pytest.fixture(scope="function", autouse=True)
    def before_func_01(self, start_demo):
        """
        函数级别的初始化
        1：user1账户删除当前账户所有的黑名单
        2：user1账户将user2和user3，user4三个账户加入黑名单
        函数基本的清除
        1：user1账户删除当前账户所有的黑名单
        :param start_demo:
        :return:
        """
        token_1 = start_demo
        user_friend_black_multi_remove_all(token_1)
        user_friend_black_multi(token_1,
                                user_ids=f'{user2_info["user_id"]},{user3_info["user_id"]},{user4_info["user_id"]}')
        yield
        user_friend_black_multi_remove_all(token_1)

    @allure.story("将一个黑名单中的人员移出黑名单场景")
    @allure.title("test_user_friend_black_multi_remove_single")
    def test_user_friend_black_multi_remove_single(self, start_demo):
        """
        1:初始情况下断言user1默认的黑名单的列表有user2，user3，user4
        2:user1把user2从黑名单列表删除,断言删除黑名单成功code = 0
        3:断言删除黑名单成功后，user2的id没有在user1的黑名单列表里了
        :param start_demo:
        :return:
        """
        token_1 = start_demo
        before_black_lists = [i['userId'] for i in user_black_list(token_1)['data']]
        assert user2_info["user_id"] in before_black_lists
        assert user3_info["user_id"] in before_black_lists
        assert user4_info["user_id"] in before_black_lists
        res = user_friend_black_multi_remove(token_1, user_ids=user2_info["user_id"])
        assert res["code"] == "0"
        my_log('test_user_friend_black_multi_remove_single',
               {"userIds": user2_info["user_id"]}, res)
        after_black_lists = [i['userId'] for i in user_black_list(token_1)['data']]
        assert user2_info["user_id"] not in after_black_lists

    @allure.story("将多个黑名单中的人员移出黑名单场景")
    @allure.title("test_user_friend_black_multi_remove_multiple")
    def test_user_friend_black_multi_remove_multiple(self, start_demo):
        """
        1:初始情况下断言user1默认的黑名单的列表有user2，user3，user4
        2:user1把user2,user3,user4从黑名单列表删除,断言删除黑名单成功code = 0
        3:删除多个后断言user2,user3,user4的user_id不在user1的黑名单列表里
        :param start_demo:
        :return:
        """
        token_1 = start_demo
        before_black_lists = [i['userId'] for i in user_black_list(token_1)['data']]
        assert user2_info["user_id"] in before_black_lists
        assert user3_info["user_id"] in before_black_lists
        assert user4_info["user_id"] in before_black_lists
        res = user_friend_black_multi_remove(token_1,
                                             user_ids=f'{user2_info["user_id"]},{user3_info["user_id"]},{user4_info["user_id"]}')
        assert res["code"] == "0"
        my_log('test_user_friend_black_multi_remove_multiple',
               {"userIds": f'{user2_info["user_id"]},{user3_info["user_id"]},{user4_info["user_id"]}'}, res)
        after_black_lists = [i['userId'] for i in user_black_list(token_1)['data']]
        assert user2_info["user_id"] not in after_black_lists
        assert user3_info["user_id"] not in after_black_lists
        assert user4_info["user_id"] not in after_black_lists

    @allure.story("将单个非黑名单中的人员移出黑名单")
    @allure.title("test_user_friend_black_multi_remove_single_non_black")
    def test_user_friend_black_multi_remove_single_non_black(self, start_demo):
        """
        1：将非黑名单中的人员移出黑名单，断言移除失败code=1
        :param start_demo:
        :return:
        """
        token_1 = start_demo
        res = user_friend_black_multi_remove(token_1,
                                             user_ids=user5_info["user_id"])
        my_log('test_user_friend_black_multi_remove_single_non_black',
               {"userIds": user5_info["user_id"]}, res)
        assert res["code"] == "1", "将非黑名单移出黑名单"




