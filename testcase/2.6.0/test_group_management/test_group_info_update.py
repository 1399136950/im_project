# -*- coding:utf-8 -*-
# @author  : ywt
# @file   : test_group_info_update.py
# @ide    : PyCharm
# @time    : 2021/4/19 15:07
import json
import time

import pytest
import allure

from lib.im_api_lib.group_management import group_create_with_users         # 拉人创建群组接口
from lib.im_api_lib.group_management import group_info_update               # 修改群名称接口
from lib.im_api_lib.user import user_group_invite_auto_accept               # 设置自动接受群邀请接口
from lib.im_api_lib.group_management import group_manager_multi_add         # 新增管理员接口
from lib.im_api_lib.group_management import group_detail                    # 群组详情接口
from lib.im_api_lib.group_management import group_remove                    # 解散群组接口
from lib.im_api_lib.group_management import group_member_remove_multi       # 踢出群成员接口
from lib.im_api_lib.group_management import group_assignment                # 群组转让接口
from lib.im_api_lib.group_management import group_member_list               # 成员列表接口
from lib.im_api_lib.group_management import group_member_exit               # 退出群组接口
from lib.im_api_lib.group_management import group_remove_all                # 解散用户当前所有的群组接口
from lib.im_api_lib.group_management import group_member_exit_all           # 退出所有的群组接口
from lib.im_api_lib.login import login
from common.read_excel_data import get_excel_data
from config.conf import user1_info
from config.conf import user2_info
from config.conf import user3_info
from config.conf import user4_info
from common.my_log import my_log


@pytest.fixture(scope="function")
def before_func(start_demo):
    # 群主user1创建一个群组并且添加两个人,群组就有了user1，user2，user3 三个用户, 群名称为新建三人群+一个时间戳
    token_1 = start_demo
    res = group_create_with_users(token_1,
                                  user_ids=f"{user2_info['user_id']},{user3_info['user_id']}",
                                  group_name=f"新建三人群名称{int(time.time() * 100)}")
    yield token_1, res            # 函数级别的初始化和清除，把每次创建群聊的返回值的token1返回出去


@pytest.fixture(scope="class")
def after_class(start_demo):
    pass
    yield
    token_1 = start_demo
    group_member_exit_all(token_1)
    group_remove_all(token_1)


@allure.feature("设置群组名称接口")
class TestGroupInfoUpdate:
    def setup_class(self):
        self.token_2 = login(user2_info)
        self.token_3 = login(user3_info)
        self.token_4 = login(user4_info)
        self.new_group_name = "修改后的群组名称"
        user_group_invite_auto_accept(self.token_2, True)      # 用户2设置自动加入群
        user_group_invite_auto_accept(self.token_3, True)      # 用户3设置自动加入群

    def teardown_class(self):
        group_remove_all(self.token_2)
        group_member_exit_all(self.token_2)
        group_remove_all(self.token_3)
        group_member_exit_all(self.token_3)
        group_remove_all(self.token_4)
        group_member_exit_all(self.token_4)

    @allure.story("群主修改群名称场景")
    @allure.title("test_group_owner_set_group_name")
    @pytest.mark.parametrize("in_data,reps_data",
                             get_excel_data('../data/im/ZXIM接口测试用例-v1.0.xls',
                                            '群组管理模块',
                                            'test_group_owner_set_group_name'))
    def test_group_owner_set_group_name(self, before_func, in_data, reps_data, after_class):
        """
        1:群主use1修改群名称
        2:断言群主修改群名称的返回值的code等于预期值
        3:如果修改群名称成功，那么继续断言群主设置的群名称等于群聊详细信息里面查询出来的群名称
        4:如果修改群名称失败，那么断言返回的error里面的msg等于预期
        :param before_func:         得到user1登录的token和每次初始化创建群聊的返回值
        :param in_data:             数据驱动参数，传递的是修改的name
        :param reps_data:           数据驱动参数，传递的是预期的返回结果
        :param after_class:
        :return:                    None
        """
        token_1, res = before_func
        ret = group_info_update(token_1,
                                group_id=res['data']['communicationId'],
                                group_name=in_data)
        my_log("test_group_owner_set_group_name",
               {"groupName": in_data, "groupId": res['data']['communicationId']}, ret)
        assert ret['code'] == json.loads(reps_data)["code"]
        if ret['code'] == "0":
            rep = group_detail(token_1, group_id=res['data']['communicationId'])
            assert rep['data']['name'] == in_data
        else:
            assert ret["error"]["message"] == json.loads(reps_data)["error"]["message"]
        group_remove(token_1, group_id=res['data']['communicationId'])

    @allure.story("管理员修改群名称场景")
    @allure.title("test_group_manager_set_group_name")
    @pytest.mark.parametrize("in_data,reps_data",
                             get_excel_data('../data/im/ZXIM接口测试用例-v1.0.xls',
                                            '群组管理模块',
                                            'test_group_manager_set_group_name'))
    def test_group_manager_set_group_name(self, before_func, in_data, reps_data):
        """
        1:群主user1把user2设置成管理员
        2:管理员user2去设置群名称
        3:断言管理员修改群名称的返回值等于预期
        4:如果修改群名称成功，那么继续断言管理员设置的群名称等于群聊详细信息里面查询出来的群名称
        5:如果管理员修改群名称失败，那么断言返回的error里面的msg等于预期
        :param before_func:     user1登录的token和每次初始化创建群聊的返回值res
        :param in_data:
        :param reps_data:
        :return:
        """
        token_1, res = before_func
        group_manager_multi_add(token_1,
                                group_id=res['data']['communicationId'],
                                manager_ids=f"{user2_info['user_id']}")
        ret = group_info_update(self.token_2,
                                group_id=res['data']['communicationId'],
                                group_name=in_data)
        my_log("test_group_manager_set_group_name",
               {"groupName": in_data, "groupId": res['data']['communicationId']}, ret)
        assert ret['code'] == json.loads(reps_data)["code"]
        if ret['code'] == "0":
            rep = group_detail(self.token_2, group_id=res['data']['communicationId'])
            assert rep['data']['name'] == in_data
        else:
            assert ret["error"]["message"] == json.loads(reps_data)["error"]["message"]
        group_remove(token_1, group_id=res['data']['communicationId'])

    @allure.story("普通群成员修改群名称场景")
    @allure.title("test_group_members_set_group_name")
    def test_group_members_set_group_name(self, before_func):
        token_1, res = before_func  # 得到user1登录的token和每次初始化创建群聊的返回值
        # 普通群成员user3修改群名称
        ret = group_info_update(self.token_3,
                                group_id=res['data']['communicationId'],
                                group_name=self.new_group_name)
        my_log("test_group_members_set_group_name",
               {"groupName": self.new_group_name, "groupId": res['data']['communicationId']}, ret)
        # 断言普通群成员修改群名称失败，code返回"1",断言错误信息的返回值的message为'没有权限进行该操作'
        assert ret['code'] == "1"
        assert ret["error"]["message"] == '没有权限进行该操作'
        # 断言普通成员设置的群名称不等于群聊详细信息里面查询出来的群名称，
        rep = group_detail(self.token_3, group_id=res['data']['communicationId'])
        assert rep['data']['name'] != self.new_group_name
        # 测试完后新增的群聊全部删除
        group_remove(token_1, group_id=res['data']['communicationId'])

    @allure.story("非群成员修改群名称场景")
    @allure.title("test_non_group_members_set_group_name")
    def test_non_group_members_set_group_name(self, before_func):
        token_1, res = before_func  # 得到user1登录的token和每次初始化创建群聊的返回值
        # 非群成员user4修改群名称
        ret = group_info_update(self.token_4,
                                group_id=res['data']['communicationId'],
                                group_name=self.new_group_name)
        my_log("test_non_group_members_set_group_name",
               {"groupName": self.new_group_name, "groupId": res['data']['communicationId']}, ret)
        # 断言非群成员修改群名称失败，code返回"1",断言错误信息的返回值的message为'没有权限进行该操作'
        assert ret["code"] == "1"
        assert ret["error"]["message"] == '没有权限进行该操作'
        # 断言非群成员设置的群名称不等于群聊详细信息里面查询出来的群名称，
        rep = group_detail(self.token_3, group_id=res['data']['communicationId'])
        assert rep['data']['name'] != self.new_group_name
        # 测试完后新增的群聊全部删除
        group_remove(token_1, group_id=res['data']['communicationId'])

    @allure.story("群聊解散后群主修改群名称场景场景")
    @allure.title("test_remove_group_then_owner_set_group_name")
    def test_remove_group_then_owner_set_group_name(self, before_func):
        """
        1:群主use1解散创建的群
        2:解散群后，user1群主去修改已经被解散的群的群名称
        3：断言解散群后，user1群主去修改已经被解散的群的群名称失败code = 1，断言返回的error的message = '群组不存在'
        :param before_func:     user1登录的token和每次初始化动作创建群的返回值
        :return:                None
        """
        token_1, res = before_func
        group_remove(token_1, group_id=res['data']['communicationId'])
        ret = group_info_update(token_1,
                                group_id=res['data']['communicationId'],
                                group_name=self.new_group_name)
        my_log("test_remove_group_then_owner_set_group_name",
               {"groupName": self.new_group_name, "groupId": res['data']['communicationId']}, ret)
        assert ret["code"] == "1"
        assert ret["error"]['message'] == '群组不存在'
        group_remove(token_1, group_id=res['data']['communicationId'])

    @allure.story("群主踢了某个管理员后这个管理员修改群名称场景")
    @allure.title("test_manager_been_removed_then_set_group_name")
    def test_manager_been_removed_then_set_group_name(self, before_func):
        """
        1:群主use1把user2设置成管理员
        2:把user2从群里踢了
        3:user2去设置群名称
        4:断言管理员被踢了后设置群名称失败，error的返回信息为'没有权限进行该操作'
        :param before_func:         user1登录的token和每次初始化动作创建群的返回值
        :return:                    None
        """
        token_1, res = before_func
        group_manager_multi_add(token_1,
                                group_id=res['data']['communicationId'],
                                manager_ids=user2_info["user_id"])
        group_member_remove_multi(token_1,
                                  group_id=res['data']['communicationId'],
                                  user_ids=user2_info["user_id"])
        ret = group_info_update(self.token_2,
                                group_id=res['data']['communicationId'],
                                group_name=self.new_group_name)
        my_log("test_manager_been_removed_then_set_group_name",
               {"groupName": self.new_group_name, "groupId": res['data']['communicationId']}, ret)
        assert ret["code"] == "1"
        assert ret['error']['message'] == '没有权限进行该操作'
        group_remove(token_1, group_id=res['data']['communicationId'])

    @allure.story("群主转让群给新群主后新群主设置群名称场景")
    @allure.title("test_new_master_set_group_name")
    def test_new_master_set_group_name(self, before_func):
        """
        1:断言群主转让前，群主是user1
        2:user1 把群主转让给user2
        3:断言群主转让后，群主是user2
        4:user2新群主设置群名称
        5:断言新群主user2设置群名称接成功返回的code=0,并且断言新群主设置的群名称等于查询接口查询到的群名称
        :param before_func:      user1登录的token和每次初始化动作创建群的返回值
        :return:                 None
        """
        token_1, res = before_func
        assert res['data']['ownerId'] == user1_info['user_id']
        group_assignment(token_1,
                         group_id=res['data']['communicationId'],
                         owner_id=user2_info['user_id'])
        rep = group_detail(token_1, group_id=res['data']['communicationId'])
        assert rep['data']['ownerId'] == user2_info['user_id']
        ret = group_info_update(self.token_2,
                                group_id=res['data']['communicationId'],
                                group_name=self.new_group_name)
        my_log("test_new_master_set_group_name",
               {"groupName": self.new_group_name, "groupId": res['data']['communicationId']}, ret)
        assert ret["code"] == "0"
        ref = group_detail(token_1, group_id=res['data']['communicationId'])
        assert ref['data']['name'] == self.new_group_name
        group_remove(token_1, group_id=res['data']['communicationId'])

    @allure.story("群主转让群给新群主后旧群主设置群名称场景")
    @allure.title("test_old_master_set_group_name")
    def test_old_master_set_group_name(self, before_func):
        """
        1:断言群主转让前，群主是user1
        2:user1 把群主转让给user2
        3:断言群主转让后，群主是user2
        4:user1非群主了设置群名称
        5:断言use1非群主设置群名称失败code = 1,设置群名称的返回的message为预期的没有权限进行该操作
        :param before_func:         user1登录的token和每次初始化动作创建群的返回值
        :return:                    None
        """
        token_1, res = before_func
        assert res['data']['ownerId'] == user1_info['user_id']
        group_assignment(token_1,
                         group_id=res['data']['communicationId'],
                         owner_id=user2_info['user_id'])
        rep = group_detail(token_1, group_id=res['data']['communicationId'])
        assert rep['data']['ownerId'] == user2_info['user_id']
        ret = group_info_update(token_1,
                                group_id=res['data']['communicationId'],
                                group_name=self.new_group_name)
        my_log("test_old_master_set_group_name",
               {"groupName": self.new_group_name, "groupId": res['data']['communicationId']}, ret)
        assert ret["code"] == "1"
        assert ret['error']['message'] == "没有权限进行该操作"
        group_remove(token_1, group_id=res['data']['communicationId'])

    @allure.story("把一个已经退出群的用户设置成管理员这个退群的用户再修改群名称场景")
    @allure.title("test_exited_member_become_manager_then_set_group_name")
    def test_exited_member_become_manager_then_set_group_name(self, before_func):
        """
        1:断言退群前user3在群里
        2:user3主动退出刚创建的群组
        3:断言退群后user3不在群里
        4:群主user1把非群成员user3设置成管理员
        5:断言群主user1把非群成员user3设置成管理员接口返回是"FAIL"
        6:非群用户user3设置群名称
        7:断言非群用户设置群名称失败返回的code = 1,非群用户设置群名称返回值的错误信息的message="没有权限进行该操作"
        :param before_func:         user1登录的token和每次初始化动作创建群的返回值
        :return:
        """
        token_1, res = before_func
        ref = group_member_list(token_1, group_id=res['data']['communicationId'])
        assert ref["code"] == "0" and user3_info["user_id"] in [i["userId"] for i in ref["data"]]
        group_member_exit(self.token_3, group_id=res['data']['communicationId'])
        reg = group_member_list(token_1, group_id=res['data']['communicationId'])
        assert reg["code"] == "0" and user3_info["user_id"] not in [i["userId"] for i in reg["data"]]
        ret = group_manager_multi_add(token_1,
                                      group_id=res['data']['communicationId'],
                                      manager_ids=user3_info["user_id"])
        assert ret['msg'] == "FAIL", "设置不在群的用户为管理员也能成功"
        # 非群用户user3设置群名称
        reh = group_info_update(self.token_3,
                                group_id=res['data']['communicationId'],
                                group_name=self.new_group_name)
        my_log("test_exited_member_become_manager_then_set_group_name",
               {"groupName": self.new_group_name, "groupId": res['data']['communicationId']}, reh)
        assert reh['code'] == "1"
        assert reh["error"]["message"] == "没有权限进行该操作"
        group_remove(token_1, group_id=res['data']['communicationId'])

    @allure.story("管理员主动退群后再修改群名称场景")
    @allure.title("test_manager_exit_group_set_group_name")
    def test_manager_exit_group_set_group_name(self, before_func):
        """
        1:断言user2退群前还在群里
        2:把user2设置成管理员
        3:user2主动退群,断言user2没有在最新创建的群里面了
        4:user2退群后修改群名称
        5:断言user2退群后修改群名称失败返回的code=1,修改群名称返回值的message='没有权限进行该操作'
        :param before_func:     user1登录的token和每次初始化动作创建群的返回值
        :return:                None
        """
        token_1, res = before_func
        member_lists_before = group_member_list(token_1, group_id=res['data']['communicationId'])
        assert user2_info["user_id"] in [i['userId'] for i in member_lists_before['data']]
        group_manager_multi_add(token_1,
                                group_id=res['data']['communicationId'],
                                manager_ids=user2_info["user_id"])
        group_member_exit(self.token_2, group_id=res['data']['communicationId'])
        member_lists_after = group_member_list(token_1, group_id=res['data']['communicationId'])
        assert user2_info["user_id"] not in [i['userId'] for i in member_lists_after['data']]
        reh = group_info_update(self.token_2,
                                group_id=res['data']['communicationId'],
                                group_name=self.new_group_name)
        my_log("test_manager_exit_group_set_group_name",
               {"groupName": self.new_group_name, "groupId": res['data']['communicationId']}, reh)
        assert reh['code'] == "1"
        assert reh['error']['message'] == '没有权限进行该操作'
        group_remove(token_1, group_id=res['data']['communicationId'])

    @allure.story("某用户在a群是管理员在b群是普通成员，此用户修改b群群名称失败，修改a群群名称成功场景")
    @allure.title("test_normal_identity_and_manage_identity_set_group_name")
    def test_normal_identity_and_manage_identity_set_group_name(self, before_func, after_class):
        """
        1:创建一个新的群组 res是群1,ret是群2,
        2:把user2设置成res群1的管理员
        3:断言user2在res群1的管理员列表里
        4:user2 设置ret群2的群名称
        5:断言user2 设置ret群2的群名称预失败返回code = 1并且error里面的message="没有权限进行该操作"
        6:user2设置res群1的群名称
        7:断言user2设置res群1的群名称成功code返回值=0，断言设置的群名称和查询的群名称相同
        :param before_func:     user1登录的token和每次初始化动作创建群的返回值
        :param after_class:     test_case类的清除函数
        :return:
        """
        token_1, res = before_func
        ret = group_create_with_users(token_1,
                                      description=f"新建三人群名称{int(time.time() * 100)}",
                                      group_name=f"新建三人群{int(time.time() * 100)}",
                                      user_ids=f"{user2_info['user_id']},{user3_info['user_id']}")
        group_manager_multi_add(token_1,
                                group_id=res['data']['communicationId'],
                                manager_ids=user2_info["user_id"])
        group_lists = group_detail(token_1, group_id=res['data']['communicationId'])
        assert user2_info["user_id"] in group_lists['data']['managerList']
        ref = group_info_update(self.token_2,
                                group_id=ret['data']['communicationId'],
                                group_name=self.new_group_name)
        my_log("test_normal_identity_and_manage_identity_set_group_name",
               {"groupName": self.new_group_name, "groupId": ret['data']['communicationId']}, ref)
        assert ref['code'] == "1"
        assert ref['error']['message'] == "没有权限进行该操作"
        reg = group_info_update(self.token_2,
                                group_id=res['data']['communicationId'],
                                group_name=self.new_group_name)
        group_info = group_detail(token_1,
                                  group_id=res['data']['communicationId'])
        assert reg['code'] == "0"
        assert self.new_group_name == group_info['data']['name']