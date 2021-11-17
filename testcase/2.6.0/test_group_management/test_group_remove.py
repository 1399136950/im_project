# -*- coding:utf-8 -*-
# @project : teacher_sq
# @author  : ywt
# @file   : test_group_remove.py
# @ide    : PyCharm
# @time    : 2021/4/20 18:16
import time

import pytest
import allure

from lib.im_api_lib.group_management import group_create_with_users     # 拉人创建群组接口
from lib.im_api_lib.group_management import group_remove                # 解散群组接口
from lib.im_api_lib.group_management import group_remove_all            # 解散群组接口
from lib.im_api_lib.group_management import group_detail                # 群组详情接口:查看单个接口
from lib.im_api_lib.group_management import group_manager_multi_add     # 新增管理员接口
from lib.im_api_lib.group_management import group_member_list           # 成员列表接口
from lib.im_api_lib.login import login
from common.my_log import my_log
from config.conf import user2_info
from config.conf import user3_info
from config.conf import user4_info


@allure.feature("解散群组接口")
class TestGroupRemove:
    def setup_class(self):
        self.token_2 = login(user2_info)
        self.token_3 = login(user3_info)
        self.token_4 = login(user4_info)

    @pytest.fixture(scope="class", autouse=True)
    def before_class(self, start_demo):
        pass
        yield
        token = start_demo
        group_remove_all(token)

    @pytest.fixture(scope="function")
    def before_case(self, start_demo):
        token_1 = start_demo
        # 前置条件创建一个群组并且添加两个人，群组就有了user1，user2，user3 三个用户，群名称为新建三人群+一个时间戳
        res = group_create_with_users(token_1,
                                      user_ids=f"{user2_info['user_id']},{user3_info['user_id']}",
                                      group_name=f"新建三人群名称{int(time.time() * 100)}")
        yield res, token_1

    @allure.story("群主解散一个群场景")
    @allure.title("test_group_owner_remove_group")
    def test_group_owner_remove_group(self, before_case):
        """
        1：断言删除这个群之前，查询这个群信息的 status状态等于0
        2：群主user1解散群组操作
        3:断言群主解散一个群的返回值的code = 0
        4：断言删除这个群之后 查询这个群信息的 status 状态等于 -1
        :param before_case:
        :return:
        """
        res, token = before_case
        reg = group_detail(token,  group_id=res["data"]["communicationId"])
        assert reg["data"]["status"] == 0
        ret = group_remove(token, group_id=res["data"]["communicationId"])
        my_log("test_group_owner_remove_group", {"groupId": res["data"]["communicationId"]}, ret)
        assert ret['code'] == "0"
        ref = group_detail(token,  group_id=res["data"]["communicationId"])
        assert ref["data"]["status"] == -1

    @allure.story("管理员解散一个群场景")
    @allure.title("test_group_manager_remove_group")
    def test_group_manager_remove_group(self, before_case):
        """
        1:断言删除这个群之前 查询这个群信息的 status 状态等于 0
        2:群主user1把user2设置成管理员
        3:断言user2在群的群管理员ID列表里面
        4:user2这个管理员去解散群
        5:断言管理员解散群返回 'FAIL'和'message': '没有权限进行该操作'
        6:断言管理员user2解散这个群之后 查询这个群信息的 status 状态等于 0，群状态正常
        :param before_case:
        :return:
        """
        res, token_1 = before_case
        reg = group_detail(token_1,  group_id=res["data"]["communicationId"])
        assert reg["data"]["status"] == 0
        group_manager_multi_add(token_1,
                                group_id=res['data']['communicationId'],
                                manager_ids=user2_info["user_id"])
        ref = group_detail(token_1, group_id=res["data"]["communicationId"])
        assert user2_info["user_id"] in ref['data']['managerList']
        ret = group_remove(self.token_2, group_id=res["data"]["communicationId"])
        my_log("test_group_manager_remove_group",
               {"groupId": res["data"]["communicationId"]}, ret)
        assert ret['msg'] == 'FAIL' and ret['error']['message'] == '没有权限进行该操作', "断言管理员解散群没有返回'FAIL'"
        reg = group_detail(token_1,  group_id=res["data"]["communicationId"])
        assert reg["data"]["status"] == 0

    @allure.story("群普通成员解散一个群场景")
    @allure.title("test_group_member_remove_group")
    def test_group_member_remove_group(self, before_case):
        """
        1:断言user3在新建的群组里面
        2:user3 这个普通成员去解散群,断言普通成员解散群的返回值等于'FAIL',返回message='没有权限进行该操作'
        3：断言普通成员user3解散这个群之后 查询这个群信息的 status 状态等于 0，群状态正常
        :param before_case:
        :return:
        """
        res, token_1 = before_case
        ret = group_member_list(token_1, group_id=res["data"]["communicationId"])
        assert user3_info['user_id'] in [i['userId'] for i in ret['data']]
        ref = group_remove(self.token_3, group_id=res["data"]["communicationId"])
        my_log("test_group_member_remove_group",
               {"groupId": res["data"]["communicationId"]}, ref)
        assert ref['msg'] == 'FAIL' and ref['error']['message'] == '没有权限进行该操作'
        reg = group_detail(token_1,  group_id=res["data"]["communicationId"])
        assert reg["data"]["status"] == 0

    @allure.story("非群成员解散一个群场景")
    @allure.title("test_non_group_member_remove_group")
    def test_non_group_member_remove_group(self, before_case):
        """
        1:断言user4不在新建的群组里面
        2:user4 这个非群成员去解散群,断言非群成员解散群的返回值等于'FAIL'返回的message='没有权限进行该操作'
        3：断言非群成员user4解散这个群之后 查询这个群信息的 status 状态等于 0，群状态正常
        :param before_case:
        :return:
        """
        res, token = before_case
        ret = group_member_list(token, group_id=res["data"]["communicationId"])
        assert user4_info['user_id'] not in [i['userId'] for i in ret['data']]
        ref = group_remove(self.token_4, res["data"]["communicationId"])
        my_log("test_non_group_member_remove_group",
               {"groupId": res["data"]["communicationId"]}, ref)
        assert ref['msg'] == 'FAIL' and ref['error']['message'] == '没有权限进行该操作'
        reg = group_detail(token, res["data"]["communicationId"])
        assert reg["data"]["status"] == 0

