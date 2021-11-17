# -*- coding:utf-8 -*-
# @author  : ywt
# @file   : test_group_info_description_update.py
# @ide    : PyCharm
# @time    : 2021/4/19 19:43
import json
import time

import pytest
import allure

from lib.im_api_lib.group_management import group_create_with_users         # 拉人创建群组接口
from lib.im_api_lib.group_management import group_info_description_update   # 修改群描述接口
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
    # 群主user1创建一个群组并且添加两个人，群组就有了user1，user2，user3 三个用户, 群描述为新建三人群+一个时间戳
    token_1 = start_demo
    res = group_create_with_users(token_1,
                                  user_ids=f"{user2_info['user_id']},{user3_info['user_id']}",
                                  description=f"新建三人群描述{int(time.time() * 100)}")
    yield token_1, res          # 函数级别的初始化和清除，把每次创建群聊的返回值的token1返回出去


@pytest.fixture(scope="class")
def after_class(start_demo):
    pass
    yield
    token_1 = start_demo
    group_member_exit_all(token_1)
    group_remove_all(token_1)


@allure.feature("修改群描述接口")
class TestGroupInfoDescriptionUpdate:
    def setup_class(self):
        self.token_2 = login(user2_info)
        self.token_3 = login(user3_info)
        self.token_4 = login(user4_info)
        self.new_group_description = "修改后的群组描述"
        user_group_invite_auto_accept(self.token_2, True)      # 用户2设置自动加入群
        user_group_invite_auto_accept(self.token_3, True)      # 用户3设置自动加入群

    def teardown_class(self):
        group_remove_all(self.token_2)
        group_member_exit_all(self.token_2)
        group_remove_all(self.token_3)
        group_member_exit_all(self.token_3)
        group_remove_all(self.token_4)
        group_member_exit_all(self.token_4)

    @allure.story("群主修改群描述场景")
    @allure.title("test_group_owner_set_group_description")
    @pytest.mark.parametrize("in_data,reps_data",
                             get_excel_data('../data/im/ZXIM接口测试用例-v1.0.xls',
                                            '群组管理模块',
                                            'test_group_owner_set_group_description'))
    def test_group_owner_set_group_description(self, before_func, in_data, reps_data, after_class):
        token_1, res = before_func          # 得到user1登录的token和每次初始化创建群聊的返回值
        # 群主use1修改群描述
        ret = group_info_description_update(token_1,
                                            group_id=res['data']['communicationId'],
                                            description=in_data)
        my_log("test_group_owner_set_group_description",
               {"description": in_data, "groupId": res['data']['communicationId']},
               ret)
        # 断言群主修改群描述成功，code返回等于预期值
        assert ret['code'] == json.loads(reps_data)["code"]
        if ret['code'] == "0":  # 如果修改群描述成功，那么继续断言群主设置的群描述等于群聊详细信息里面查询出来的群描述
            rep = group_detail(token_1, group_id=res['data']['communicationId'])
            assert rep['data']['description'] == in_data
        else:                   # 如果修改群描述失败，那么断言返回的error里面的msg等于预期
            assert ret["error"]["message"] == json.loads(reps_data)["error"]["message"]
        # 测试完后新增的群聊全部删除
        group_remove(token_1, group_id=res['data']['communicationId'])

    @allure.story("管理员修改群描述场景")
    @allure.title("test_group_manager_set_group_description")
    @pytest.mark.parametrize("in_data,reps_data",
                             get_excel_data('../data/im/ZXIM接口测试用例-v1.0.xls',
                                            '群组管理模块',
                                            'test_group_manager_set_group_description'))
    def test_group_manager_set_group_description(self, before_func, in_data, reps_data):
        token_1, res = before_func  # 得到user1登录的token和每次初始化创建群聊的返回值
        # 群主user1把user2设置成管理员
        group_manager_multi_add(token_1,
                                group_id=res['data']['communicationId'],
                                manager_ids=f"{user2_info['user_id']}")
        # 管理员user2去设置群描述
        ret = group_info_description_update(self.token_2,
                                            group_id=res['data']['communicationId'],
                                            description=in_data)
        my_log("test_group_manager_set_group_description",
               {"description": in_data, "groupId": res['data']['communicationId']},
               ret)
        # 断言管理员修改群描述的返回值等于预期
        assert ret['code'] == json.loads(reps_data)["code"]
        if ret['code'] == "0":  # 如果修改群描述成功，那么继续断言管理员设置的群描述等于群聊详细信息里面查询出来的群描述
            rep = group_detail(self.token_2, group_id=res['data']['communicationId'])
            assert rep['data']['description'] == in_data
        else:                   # 如果管理员修改群描述失败，那么断言返回的error里面的msg等于预期
            assert ret["error"]["message"] == json.loads(reps_data)["error"]["message"]
        # 测试完后新增的群聊全部删除
        group_remove(token_1, group_id=res['data']['communicationId'])

    @allure.story("普通群成员修改群描述场景")
    @allure.title("test_ordinary_group_members_modify_group_description")
    def test_ordinary_group_members_modify_group_description(self, before_func):
        token_1, res = before_func  # 得到user1登录的token和每次初始化创建群聊的返回值
        # 普通群成员user3修改群描述
        ret = group_info_description_update(self.token_3,
                                            group_id=res['data']['communicationId'],
                                            description=self.new_group_description)
        my_log("test_ordinary_group_members_modify_group_description",
               {"description": self.new_group_description, "groupId": res['data']['communicationId']},
               ret)
        # 断言普通群成员修改群描述失败，code返回"1",断言错误信息的返回值的message为'没有权限进行该操作'
        assert ret['code'] == "1"
        assert ret["error"]["message"] == '没有权限进行该操作'
        # 断言普通成员设置的群描述不等于群聊详细信息里面查询出来的群描述，
        rep = group_detail(self.token_3, group_id=res['data']['communicationId'])
        assert rep['data']['description'] != self.new_group_description
        # 测试完后新增的群聊全部删除
        group_remove(token_1, group_id=res['data']['communicationId'])

    @allure.story("非群成员修改群描述场景")
    @allure.title("test_non_group_members_modify_group_description")
    def test_non_group_members_modify_group_description(self, before_func):
        token_1, res = before_func  # 得到user1登录的token和每次初始化创建群聊的返回值
        # 非群成员user4修改群描述
        ret = group_info_description_update(self.token_4,
                                            group_id=res['data']['communicationId'],
                                            description=self.new_group_description)
        my_log("test_non_group_members_modify_group_description",
               {"description": self.new_group_description, "groupId": res['data']['communicationId']},
               ret)
        # 断言非群成员修改群描述失败，code返回"1",断言错误信息的返回值的message为'没有权限进行该操作'
        assert ret["code"] == "1"
        assert ret["error"]["message"] == '没有权限进行该操作'
        # 断言非群成员设置的群描述不等于群聊详细信息里面查询出来的群描述，
        rep = group_detail(self.token_3, group_id=res['data']['communicationId'])
        assert rep['data']['description'] != self.new_group_description
        # 测试完后新增的群聊全部删除
        group_remove(token_1, group_id=res['data']['communicationId'])

    @allure.story("群聊解散后群主修改群描述场景场景")
    @allure.title("test_group_delete_group_master_modifies_group_description")
    def test_group_delete_group_master_modifies_group_description(self, before_func):
        token_1, res = before_func  # 得到user1登录的token和每次初始化创建群聊的返回值
        # 群主use1解散刚刚创建的群
        group_remove(token_1, group_id=res['data']['communicationId'])
        #  解散群后，user1群主去修改已经被解散的群的群描述
        ret = group_info_description_update(token_1,
                                            group_id=res['data']['communicationId'],
                                            description=self.new_group_description)
        my_log("test_group_delete_group_master_modifies_group_description",
               {"description": self.new_group_description, "groupId": res['data']['communicationId']}, ret)
        # 断言解散群后，user1群主去修改已经被解散的群的群描述失败code = 1，断言返回的error的message = '群组不存在'
        assert ret["code"] == "1"
        assert ret["error"]['message'] == '群组不存在'
        group_remove(token_1, group_id=res['data']['communicationId'])

    @allure.story("群主踢了某个管理员后这个管理员修改群描述场景")
    @allure.title("test_master_delete_administrators_modifies_group_description")
    def test_master_delete_administrators_modifies_group_description(self, before_func):
        token_1, res = before_func      # 得到user1登录的token和每次初始化创建群聊的返回值
        # 把user2设置成管理员
        group_manager_multi_add(token_1,
                                group_id=res['data']['communicationId'],
                                manager_ids=user2_info["user_id"])
        # 把user2从群里踢了
        group_member_remove_multi(token_1,
                                  group_id=res['data']['communicationId'],
                                  user_ids=user2_info["user_id"])
        # user2去设置群描述
        ret = group_info_description_update(self.token_2,
                                            group_id=res['data']['communicationId'],
                                            description=self.new_group_description)
        my_log("test_master_delete_administrators_modifies_group_description",
               {"description": self.new_group_description,
                "groupId": res['data']['communicationId']}, ret)
        # 断言管理员被踢了后设置群描述失败，error的返回信息为'没有权限进行该操作'
        assert ret["code"] == "1"
        assert ret['error']['message'] == '没有权限进行该操作'
        group_remove(token_1, group_id=res['data']['communicationId'])

    @allure.story("群主转让群给新群主后新群主设置群名称场景")
    @allure.title("test_master_change_new_master_modifies_group_description")
    def test_master_change_new_master_modifies_group_description(self, before_func):
        token_1, res = before_func  # 得到user1登录的token和每次初始化创建群聊的返回值
        # 断言群主转让前，群主是use1
        assert res['data']['ownerId'] == user1_info['user_id']
        # use1 把群主转让给use2
        group_assignment(token_1,
                         group_id=res['data']['communicationId'],
                         owner_id=user2_info['user_id'])
        rep = group_detail(token_1, group_id=res['data']['communicationId'])
        # 断言群主转让后，群主是use2
        assert rep['data']['ownerId'] == user2_info['user_id']
        # use2 新群主设置群描述
        ret = group_info_description_update(self.token_2,
                                            group_id=res['data']['communicationId'],
                                            description=self.new_group_description)
        my_log("test_master_change_new_master_modifies_group_description",
               {"description": self.new_group_description, "groupId": res['data']['communicationId']}, ret)
        # 断言新群主设置群描述接成功返回的code=0,并且断言新群主设置的群描述等于查询接口查询到的群名称
        assert ret["code"] == "0"
        ref = group_detail(token_1, group_id=res['data']['communicationId'])
        assert ref['data']['description'] == self.new_group_description
        group_remove(token_1, group_id=res['data']['communicationId'])

    @allure.story("群主转让群给新群主后旧群主设置群名称场景")
    @allure.title("test_master_change_old_master_modifies_group_description")
    def test_master_change_old_master_modifies_group_description(self, before_func):
        token_1, res = before_func      # 得到user1登录的token和每次初始化创建群聊的返回值
        # 断言群主转让前，群主是use1
        assert res['data']['ownerId'] == user1_info['user_id']
        # use1 把群主转让给use2
        group_assignment(token_1,
                         group_id=res['data']['communicationId'],
                         owner_id=user2_info['user_id'])
        rep = group_detail(token_1, group_id=res['data']['communicationId'])
        # 断言群主转让后，群主是use2
        assert rep['data']['ownerId'] == user2_info['user_id']
        # use1 现在非群主了设置群描述
        ret = group_info_description_update(token_1,
                                            group_id=res['data']['communicationId'],
                                            description=self.new_group_description)
        my_log("test_master_change_old_master_modifies_group_description",
               {"description": self.new_group_description, "groupId": res['data']['communicationId']}, ret)
        # 断言use1现在非群主了设置群描述失败code = 1
        assert ret["code"] == "1"
        # 断言use1现在非群主了设置群描述的返回的message为预期的没有权限进行该操作
        assert ret['error']['message'] == "没有权限进行该操作"
        group_remove(token_1, group_id=res['data']['communicationId'])

    @allure.story("把一个已经退出群的用户设置成管理员这个退群的用户再修改群描述场景")
    @allure.title("test_exit_group_member_set_administrators_modifies_group_description")
    def test_exit_group_member_set_administrators_modifies_group_description(self, before_func):
        token_1, res = before_func  # 得到user1登录的token和每次初始化创建群聊的返回值
        # 断言退群前user3在群里
        ref = group_member_list(token_1, group_id=res['data']['communicationId'])
        assert ref["code"] == "0" and user3_info["user_id"] in [i["userId"] for i in ref["data"]]
        # user3退出刚创建的群组
        group_member_exit(self.token_3, group_id=res['data']['communicationId'])
        # 断言退群后user3不在群里
        reg = group_member_list(token_1, group_id=res['data']['communicationId'])
        assert reg["code"] == "0" and user3_info["user_id"] not in [i["userId"] for i in reg["data"]]
        # 群主user1把非群成员user3设置成管理员
        ret = group_manager_multi_add(token_1,
                                      group_id=res['data']['communicationId'],
                                      manager_ids=user3_info["user_id"])
        # 断言群主user1把非群成员user3设置成管理员接口返回是"FAIL"
        assert ret['msg'] == "FAIL", "设置不在群的用户为管理员也能成功"
        # 非群用户user3设置群描述
        reh = group_info_description_update(self.token_3,
                                            group_id=res['data']['communicationId'],
                                            description=self.new_group_description)
        my_log("test_exit_group_member_set_administrators_modifies_group_description",
               {"description": self.new_group_description, "groupId": res['data']['communicationId']}, reh)
        # 断言非群用户设置群描述失败，返回的code = 1,断言非群用户设置群描述返回值的错误信息的message等于预期的 "没有权限进行该操作"
        assert reh['code'] == "1"
        assert reh["error"]["message"] == "没有权限进行该操作"
        group_remove(token_1, group_id=res['data']['communicationId'])

    @allure.story("管理员主动退群后再修改群描述场景")
    @allure.title("test_administrators_exit_group_modifies_group_description")
    def test_administrators_exit_group_modifies_group_description(self, before_func):
        token_1, res = before_func      # 得到user1登录的token和每次初始化创建群聊的返回值
        # 断言user2退群前还在群里
        member_lists_before = group_member_list(token_1, group_id=res['data']['communicationId'])
        assert user2_info["user_id"] in [i['userId'] for i in member_lists_before['data']]
        # 把user2设置成管理员
        group_manager_multi_add(token_1,
                                group_id=res['data']['communicationId'],
                                manager_ids=user2_info["user_id"])
        # user2主动退群,断言user2没有在最新创建的群里面了
        group_member_exit(self.token_2, group_id=res['data']['communicationId'])
        member_lists_after = group_member_list(token_1, group_id=res['data']['communicationId'])
        assert user2_info["user_id"] not in [i['userId'] for i in member_lists_after['data']]
        # user2退群后修改群描述
        reh = group_info_description_update(self.token_2,
                                            group_id=res['data']['communicationId'],
                                            description=self.new_group_description)
        my_log("test_administrators_exit_group_modifies_group_description",
               {"description": self.new_group_description, "groupId": res['data']['communicationId']}, reh)
        # 断言user2退群后修改群描述失败返回的code=1,断言user2退群后修改群描述返回值的message等于'没有权限进行该操作'
        assert reh['code'] == "1"
        assert reh['error']['message'] == '没有权限进行该操作'
        group_remove(token_1, group_id=res['data']['communicationId'])

    @allure.story("某用户在a群是管理员在b群是普通成员，此用户修改b群群描述失败，修改a群群描述成功场景")
    @allure.title("test_user_group_a_normal_but_group_b_administrator_modifies_group_description")
    def test_user_group_a_normal_but_group_b_administrator_modifies_group_description(self, before_func, after_class):
        token_1, res = before_func  # 得到user1登录的token和每次初始化创建群聊的返回值
        # 又创建一个新的群组 res是群1,ret是群2,
        ret = group_create_with_users(token_1,
                                      description=f"新建三人群描述{int(time.time() * 100)}",
                                      group_name=f"新建三人群{int(time.time() * 100)}",
                                      user_ids=f"{user2_info['user_id']},{user3_info['user_id']}")
        # 把user2设置成res群1的管理员
        group_manager_multi_add(token_1,
                                group_id=res['data']['communicationId'],
                                manager_ids=user2_info["user_id"])
        # 断言user2在res群1的管理员列表里
        group_lists = group_detail(token_1, group_id=res['data']['communicationId'])
        assert user2_info["user_id"] in group_lists['data']['managerList']

        # user2 设置ret群2的群描述
        ref = group_info_description_update(self.token_2,
                                            group_id=ret['data']['communicationId'],
                                            description=self.new_group_description)
        my_log("test_user_group_a_normal_but_group_b_administrator_modifies_group_description",
               {"description": self.new_group_description, "groupId": ret['data']['communicationId']}, ref)
        # 断言user2 设置ret群2的群描述预失败返回code = 1并且error里面的message为"没有权限进行该操作"
        assert ref['code'] == "1"
        assert ref['error']['message'] == "没有权限进行该操作"

        # user2 设置res群1的群描述
        reg = group_info_description_update(self.token_2,
                                            group_id=res['data']['communicationId'],
                                            description=self.new_group_description)
        # 断言user2设置res群1的群描述成功code返回值=0，断言设置的群描述和查询的群描述相同
        group_info = group_detail(token_1,
                                  group_id=res['data']['communicationId'])
        assert reg['code'] == "0"
        assert self.new_group_description == group_info['data']['description']

