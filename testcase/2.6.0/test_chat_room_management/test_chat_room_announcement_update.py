# -*- coding:utf-8 -*-
# @author  : ywt
# @file   : test_chat_room_announcement_update.py
# @ide    : PyCharm
# @time    : 2021/6/7 14:21
import time

import allure
import pytest

from common.my_log import my_log
from lib.im_api_lib.login import login
from config.conf import user2_info, user3_info, user4_info
from lib.im_api_lib.chat_room_management import chat_room_create  # 创建聊天室接口
from lib.im_api_lib.chat_room_management import chat_room_announcement_update  # 设置公告接口
from lib.im_api_lib.chat_room_management import chat_room_detail  # 查询聊天室详情接口
from lib.im_api_lib.chat_room_management import chat_room_remove  # 解散聊天室（删除聊天室）接口
from lib.im_api_lib.chat_room_management import chat_room_manager_multi_add  # 新增管理员，多人接口
from lib.im_api_lib.chat_room_management import chat_room_enter  # 进入聊天室接口
from lib.im_api_lib.chat_room_management import chat_room_manager_list  # 管理员列表接口
from lib.im_api_lib.chat_room_management import chat_room_member_list  # 分页获取聊天室成员列表接口
from lib.im_api_lib.chat_room_management import chat_room_exit  # 用户离开聊天室接口


@pytest.fixture(scope="function")
def before_func(start_demo):
    # user1创建聊天室
    token_1 = start_demo
    res = chat_room_create(token_1,
                           chat_room_name=f"新建聊天室名称{int(time.time() * 1000)}",
                           description=f"新建聊天室描述{int(time.time() * 1000)}")
    yield token_1, res


@allure.feature("设置聊天室公告")
class TestChatRoomAnnouncementUpdate:
    def setup_class(self):
        self.token_2 = login(user2_info)
        self.token_3 = login(user3_info)
        self.token_4 = login(user4_info)
        self.new_chat_room_announcement = "新建聊天室公告"

    @allure.story("聊天室拥有者设置聊天室公告场景")
    @allure.title("test_chat_room_owner_set_announcement")
    def test_chat_room_owner_set_announcement(self, before_func):
        """
        1:聊天室拥有者user1设置新建聊天室的公告
        2：断言设置聊天室公告的接口返回的code=0，断言设置聊天室的公告和查询聊天室详情查询出来的公告一样
        :param before_func:
        :return:
        """
        token_1, res = before_func
        ret = chat_room_announcement_update(token_1,
                                            chat_room_id=res["data"]["communicationId"],
                                            announcement=self.new_chat_room_announcement)
        my_log("聊天室拥有者设置聊天室公告场景",
               {"chatRoomId": res["data"]["communicationId"], "announcement": self.new_chat_room_announcement},
               ret)
        assert ret["code"] == "0"
        ree = chat_room_detail(token_1, chat_room_id=res["data"]["communicationId"])
        assert ree["data"]["announcement"] == self.new_chat_room_announcement
        chat_room_remove(token_1, chat_room_id=res["data"]["communicationId"])

    @allure.story("聊天室管理员设置聊天室公告场景")
    @allure.title("test_chat_room_manager_set_announcement")
    def test_chat_room_manager_set_announcement(self, before_func):
        """
        1:user2主动进入user1创建的聊天室
        2:user1把user2设置成管理员
        3:断言user2在聊天室的管理员列表里
        4:user2管理员去设置聊天室公告
        5:断言user2管理员去设置聊天室公告成功返回值code=0，断言设置的聊天室公告和查询出来的聊天室详情的公告一致
        :param before_func:
        :return:
        """
        token_1, res = before_func
        chat_room_enter(self.token_2, chat_room_id=res["data"]["communicationId"])
        chat_room_manager_multi_add(token_1,
                                    chat_room_id=res["data"]["communicationId"],
                                    manager_ids=f"{user2_info['user_id']}")
        manager_lists = chat_room_manager_list(token_1, chat_room_id=res["data"]["communicationId"])
        assert user2_info['user_id'] in [i['userId'] for i in manager_lists['data']]
        ret = chat_room_announcement_update(self.token_2,
                                            chat_room_id=res["data"]["communicationId"],
                                            announcement=self.new_chat_room_announcement)
        my_log("聊天室管理员设置聊天室公告场景",
               {"chatRoomId": res["data"]["communicationId"], "announcement": self.new_chat_room_announcement},
               ret)
        assert ret['code'] == "0"
        ree = chat_room_detail(token_1, chat_room_id=res["data"]["communicationId"])
        assert ree["data"]["announcement"] == self.new_chat_room_announcement
        chat_room_remove(token_1, chat_room_id=res["data"]["communicationId"])

    @allure.story("聊天室普通成员设置聊天室公告场景")
    @allure.title("test_chat_room_member_set_announcement")
    def test_chat_room_member_set_announcement(self, before_func):
        """
        1:user3进入user1创建的聊天室
        2:断言user3在聊天室成员列表接口
        3:user3普通成员去设置聊天室公告
        4:断言普通用户设置聊天室公告接口失败返回值的code=1，断言返回的信息的error里面的message='没有权限进行该操作'
        :param before_func:
        :return:
        """
        token_1, res = before_func
        chat_room_enter(self.token_3, chat_room_id=res["data"]["communicationId"])
        ret = chat_room_member_list(token_1,
                                    chat_room_id=res["data"]["communicationId"])
        assert user3_info['user_id'] in [i['userId'] for i in ret['data']['userList']]
        ree = chat_room_announcement_update(self.token_3,
                                            chat_room_id=res["data"]["communicationId"],
                                            announcement=self.new_chat_room_announcement)
        my_log("聊天室普通成员设置聊天室公告场景",
               {"chatRoomId": res["data"]["communicationId"], "announcement": self.new_chat_room_announcement},
               ree)
        assert ree['code'] == "1"
        assert ree['error']['message'] == '没有权限进行该操作'
        chat_room_remove(token_1, chat_room_id=res["data"]["communicationId"])

    @allure.story("非聊天室成员设置聊天室公告场景")
    @allure.title("test_non_chat_room_member_set_announcement")
    def test_non_chat_room_member_set_announcement(self, before_func):
        """
        1:user4非聊天室成员设置聊天室公告场景
        2：断言user4非聊天室成员设置聊天室公告失败，断言返回的信息的error里面的message='没有权限进行该操作'
        :param before_func:
        :return:
        """
        token_1, res = before_func
        ree = chat_room_announcement_update(self.token_3,
                                            chat_room_id=res["data"]["communicationId"],
                                            announcement=self.new_chat_room_announcement)
        my_log("非聊天室成员设置聊天室公告场景",
               {"chatRoomId": res["data"]["communicationId"], "announcement": self.new_chat_room_announcement},
               ree)
        assert ree["code"] == "1"
        assert ree["error"]["message"] == '没有权限进行该操作'

    @allure.story("聊天室拥有者退出聊天室设置聊天室公告场景")
    @allure.title("test_chat_room_owner_exited_set_announcement")
    def test_chat_room_owner_exited_set_announcement(self, before_func):
        """
        1:聊天室拥有者退出聊天室
        2：断言聊天室拥有者退出聊天室失败，失败的message = '聊天室拥有者不能退出聊天室'
        :param before_func:
        :return:
        """
        token_1, res = before_func
        ret = chat_room_exit(token_1, chat_room_id=res["data"]["communicationId"])
        assert ret["code"] == "1"
        assert ret["error"]["message"] == '聊天室拥有者不能退出聊天室'

    @allure.story("聊天室管理员退出聊天室设置聊天室公告场景")
    @allure.title("test_chat_room_manager_exited_set_announcement")
    def test_chat_room_manager_exited_set_announcement(self, before_func):
        """
        1:user2主动进入user1创建的聊天室
        2:user1把user2设置成管理员
        3:断言user2在聊天室的管理员列表里
        4:user2聊天室管理员退出聊天室
        5:断言user2不在聊天室成员列表里面
        6:user2退出聊天室的管理员设置聊天室公告场景
        7:断言user2退出群聊的管理员设置聊天室公告等于查询聊天室详情查询出来的聊天室公告
        :param before_func:
        :return:
        """
        token_1, res = before_func
        chat_room_enter(self.token_2, chat_room_id=res["data"]["communicationId"])
        chat_room_manager_multi_add(token_1,
                                    chat_room_id=res["data"]["communicationId"],
                                    manager_ids=f"{user2_info['user_id']}")
        manager_lists = chat_room_manager_list(token_1, chat_room_id=res["data"]["communicationId"])
        assert user2_info['user_id'] in [i['userId'] for i in manager_lists['data']]
        chat_room_exit(self.token_2, chat_room_id=res["data"]["communicationId"])
        ret = chat_room_member_list(token_1,
                                    chat_room_id=res["data"]["communicationId"])
        assert user2_info['user_id'] not in [i['userId'] for i in ret['data']['userList']]
        ree = chat_room_announcement_update(self.token_2,
                                            chat_room_id=res["data"]["communicationId"],
                                            announcement=self.new_chat_room_announcement)
        assert ree["code"] == "0"
        ref = chat_room_detail(token_1, chat_room_id=res["data"]["communicationId"])
        assert ref['data']['announcement'] == self.new_chat_room_announcement
