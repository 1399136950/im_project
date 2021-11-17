# -*- coding:utf-8 -*-
# @author  : ywt
# @file   : test_group_list_mine.py
# @ide    : PyCharm
# @time    : 2021/4/29 9:12
import time

import pytest
import allure

from lib.im_api_lib.group_management import group_create_with_users  # 拉人创建群组接口
from lib.im_api_lib.group_management import group_remove_all  # 解散用户当前所有的群组
from lib.im_api_lib.group_management import group_member_exit_all  # 退出用户所有的群组
from lib.im_api_lib.group_management import group_member_list  # 成员列表接口
from lib.im_api_lib.group_management import group_list_mine  # 用户所有群列表接口
from lib.im_api_lib.user import user_group_invite_auto_accept  # 设置自动接受群邀请接口
from lib.im_api_lib.user import user_im_setting  # 用户设置信息接口
from lib.im_api_lib.group_management import group_invite_user_accept  # 用户接受群邀请接口
from lib.im_api_lib.group_management import group_invite_user_reject  # 用户拒绝群邀请接口
from lib.im_api_lib.group_management import group_member_add_multi  # 拉人入群接口
from lib.im_api_lib.login import login
from common.my_log import my_log
from config.conf import user1_info, user2_info, user3_info, user4_info


@allure.feature("用户所有群列表接口")
class TestGroupListMine:
    def setup_class(self):
        self.token_2 = login(user2_info)
        self.token_3 = login(user3_info)
        self.new_group_description = "修改后的群组描述"
        user_group_invite_auto_accept(self.token_2, True)  # 用户2设置自动加入群
        user_group_invite_auto_accept(self.token_3, True)  # 用户3设置自动加入群

    @pytest.fixture(scope="function")
    def before_step(self, start_demo):
        token = start_demo
        group_member_exit_all(token)
        group_remove_all(token)
        yield token

    @pytest.fixture(scope="class")
    def after_step(self, start_demo):
        token = start_demo
        yield
        group_member_exit_all(token)
        group_remove_all(token)
        # print("数据清除，类级别的")

    @allure.story("创建单个群查询用户所有群列表场景")
    @allure.title("test_create_single_group_list_mine")
    def test_create_single_group_list_mine(self, before_step):
        """
        1:新建一个三人群，群里有user1，user2，user3
        2:断言新建的群里三个成员都在
        3:断言用户刚新建的群在查询用户所有群列表里面,并且查询用户所有群列表长度为1
        :param before_step:
        :return:
        """
        token_1 = before_step
        res = group_create_with_users(token_1, user_ids=f"{user2_info['user_id']},{user3_info['user_id']}",
                                      group_name=f"新建三人群{int(time.time() * 100)}", )
        ret = group_member_list(token_1, group_id=res["data"]["communicationId"])
        assert user1_info["user_id"] in [i['userId'] for i in ret['data']]
        assert user2_info["user_id"] in [i['userId'] for i in ret['data']]
        assert user3_info["user_id"] in [i['userId'] for i in ret['data']]
        ref = group_list_mine(token_1)
        my_log("test_create_single_group_list_mine",
               "token", ref)
        assert res["data"]["communicationId"] in [i['communicationId'] for i in ref['data']]
        assert len(ref['data']) == 1

    @allure.story("用户自己创建10个群查询用户所有群列表场景")
    @allure.title("test_create_ten_group_list_mine")
    def test_create_ten_group_list_mine(self, before_step):
        """
        1:user1创建10个群
        2:然后查询当前用户所在的群，
        3：断言当前用户新创建的每个群的id都在查询出来的群列表接口里面并且断言用户查询出来的所有群列表长度为10
        :param before_step:
        :return:
        """
        token_1 = before_step
        new_group_ids = []                              # 存放十个新建群的群聊的id
        for i in range(1, 11):
            res = group_create_with_users(token_1,
                                          user_ids=f"{user2_info['user_id']},{user3_info['user_id']}",
                                          group_name=f"新建三人群名称{int(time.time() * 100)}")
            new_group_ids.append(res["data"]["communicationId"])
        ref = group_list_mine(token_1)
        search_group_ids = [i['communicationId'] for i in ref['data']]
        for group_id in new_group_ids:
            assert group_id in search_group_ids
        assert len(ref['data']) == 10

    @allure.story("不创建群不加入群查询用户所有群列表场景")
    @allure.title("test_user_non_create_non_join_group_list_mine")
    def test_user_non_create_non_join_group_list_mine(self, before_step):
        """
        1:用户没有加入一个群聊，没有创建一个群聊，断言用户查询出来的所有群列表长度为0
        :param before_step:
        :return:
        """
        token_1 = before_step
        ref = group_list_mine(token_1)
        assert len(ref['data']) == 0

    @allure.story("user1开启自动入群，user2建十个群拉user1入群场景")
    @allure.title("test_user_auto_join_ten_group_list_mine")
    def test_user_auto_join_ten_group_list_mine(self, before_step):
        """
        1:user1设置自动接受群邀请接口后断言user1用户当前是自动接受群邀请
        2:user2创建十个群聊并且每次都拉上user1
        3:断言用户user1查询出来的所有群列表长度为10,断言user2创建的十个群的id和user1用户查询出来的群列表相等
        :param before_step:
        :return:
        """
        token_1 = before_step
        user_group_invite_auto_accept(token_1, True)
        assert user_im_setting(token_1)['data']['user_setting']['autoAcceptGroupInvitation'] is True
        group_lists = []                    # user2创建的10个群聊会话id放这里面
        for i in range(1, 11):
            res = group_create_with_users(self.token_2,
                                          user_ids=f"{user1_info['user_id']},{user3_info['user_id']}",
                                          group_name=f"新建三人群{int(time.time() * 100)}")
            group_lists.append(res["data"]["communicationId"])
        res = group_list_mine(token_1)
        assert len(res['data']) == 10
        ret = [i['communicationId'] for i in res['data']]
        assert ret.sort() == group_lists.sort()

    @allure.story("user1关闭自动入群，user2新建十个群拉user1入群，user1同意十个群邀请的场景")
    @allure.title("test_user_accept_join_ten_group_list_mine")
    def test_user_accept_join_ten_group_list_mine(self, before_step):
        """
        1:user1设置关闭自动接受群邀请接口
        2:断言user1用户当前是关闭自动接受群邀请
        3:user2创建十个群聊并且每次都拉上user1
        4:断言user1未同意群邀请前查询出来的所有群列表长度为0
        5:断言user1同意10个群邀请后查询出来的所有群列表长度为10，
          断言user2创建的十个群的id和user1用户查询出来的群列表id相同
        :param before_step:
        :return:
        """
        token_1 = before_step
        user_group_invite_auto_accept(token_1, False)
        assert user_im_setting(token_1)['data']['user_setting']['autoAcceptGroupInvitation'] is False
        group_lists = []    # user2创建的10个群聊会话id放这里面
        for i in range(1, 11):
            res = group_create_with_users(self.token_2,
                                          user_ids=f"{user1_info['user_id']},{user3_info['user_id']}",
                                          group_name=f"新建三人群{int(time.time() * 100)}")
            group_lists.append(res["data"]["communicationId"])
        res = group_list_mine(token_1)
        assert len(res['data']) == 0
        for i in group_lists:
            group_invite_user_accept(token_1, group_id=i)
        ret = group_list_mine(token_1)
        assert len(ret['data']) == 10
        ref = [i['communicationId'] for i in ret['data']]
        assert ref.sort() == group_lists.sort()

    @allure.story("user1关闭自动入群，user2新建十个群拉user1入群，user1拒绝这十个群邀请的场景")
    @allure.title("test_user_refuse_join_group_list_mine")
    def test_user_refuse_join_group_list_mine(self, before_step):
        """
        1:user1设置关闭自动接受群邀请接口,断言user1用户当前是关闭自动接受群邀请
        2:user2创建十个群聊并且每次都拉上user1
        3:断言user1未同意群邀请前查询出来的所有群列表长度为0
        4:断言user1拒绝10个群邀请后查询出来的所有群列表长度为0，
        :param before_step:
        :return:
        """
        token = before_step
        user_group_invite_auto_accept(token, "false")
        assert user_im_setting(token)['data']['user_setting']['autoAcceptGroupInvitation'] is False
        token2 = login(user2_info)
        group_lists = []                # user2创建的10个群聊会话id放这里面
        for i in range(1, 11):
            res = group_create_with_users(token2,
                                          user_ids=f"{user1_info['user_id']},{user3_info['user_id']}",
                                          group_name=f"新建三人群{int(time.time() * 100)}")
            group_lists.append(res["data"]["communicationId"])
        res = group_list_mine(token)
        assert len(res['data']) == 0
        for i in group_lists:
            group_invite_user_reject(token, group_id=i)
        ret = group_list_mine(token)
        assert len(ret['data']) == 0

    @allure.story("user1新建10个群，user1开启自动入群，user2新建十个群拉user1入群，user1同意这十个群邀请的场景")
    @allure.title("test_user_create_and_join_group_list_mine")
    def test_user_create_and_join_group_list_mine(self, before_step):
        """
        1:user1设置自动接受群邀请接口
        2:user1创建10个群
        3:user2创建10个群,并且拉上user1
        4:断言user1查询出来的所有群列表长度为20
        5:断言新建的10个群和加入的10个群的id等于查询出来用户的所有群接口的id
        :param before_step:
        :return:
        """
        token_1 = before_step
        user_group_invite_auto_accept(token_1, True)
        group_lists = []                # user1和user2一起创建的20个群聊会话id放这里面
        for i in range(1, 11):
            res = group_create_with_users(token_1,
                                          user_ids=f"{user2_info['user_id']},{user3_info['user_id']}",
                                          group_name=f"新建三人群{int(time.time() * 100)}")
            group_lists.append(res["data"]["communicationId"])
        for i in range(1, 11):
            res = group_create_with_users(self.token_2,
                                          user_ids=f"{user1_info['user_id']},{user3_info['user_id']}",
                                          group_name=f"新建三人群{int(time.time() * 100)}")
            group_lists.append(res["data"]["communicationId"])
        ret = group_list_mine(token_1)
        assert len(ret['data']) == 20
        assert group_lists.sort() == [i['communicationId'] for i in ret['data']].sort()

    @allure.story("user1开启自动入群，user2创建10个群后面再拉user1入群")
    @allure.title("test_user_auto_invited_join_groups_list_mine")
    def test_user_auto_invited_join_groups_list_mine(self, before_step, after_step):
        """
        1:user1设置自动接受群邀请接口
        2:user2创建10个群,创建时候先不拉上user1,只拉上user3
        3：断言被邀请入群前查询user1的群组列表为空
        4：user2创建10个群后，才拉上user1入群
        5:断言user1被拉入群后，查询群组接口查询出来的data的长度为10,
          断言user2新建群的10个会话id和user1查询出来的群组列表相同
        :param after_step:
        :param before_step:
        :return:
        """
        token = before_step
        user_group_invite_auto_accept(token, True)
        group_lists = []                # user2创建的10个群聊会话id放这里面
        for i in range(1, 11):
            res = group_create_with_users(self.token_2,
                                          user_ids=f"{user3_info['user_id']},{user4_info['user_id']}",
                                          group_name=f"新建二人群{int(time.time() * 100)}")
            group_lists.append(res["data"]["communicationId"])
        ret = group_list_mine(token)
        assert len(ret['data']) == 0
        for i in group_lists:
            group_member_add_multi(self.token_2, group_id=i, user_ids=user1_info['user_id'])
        ref = group_list_mine(token)
        assert len(ref['data']) == 10
        assert group_lists.sort() == [i['communicationId'] for i in ref['data']].sort()

    # @allure.story("用户所有群列表接口_009")
    # @allure.title("user1关闭自动入群，user2创建10个群后面再拉user1入群，user1同意入群场景")
    # def test_user_auto_invited_join_groups(self, start_demo):
    #     pass
