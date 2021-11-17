# -*- coding:utf-8 -*-
# @author  : ywt
# @file   : test_chat_room_create.py
# @ide    : PyCharm
# @time    : 2021/6/7 11:29
import allure
import pytest

from common.my_log import my_log
from lib.im_api_lib.chat_room_management import chat_room_create        # 创建聊天室接口
from lib.im_api_lib.chat_room_management import chat_room_remove_all    # 解散当前用户所有的聊天室


@allure.feature("创建聊天室")
class TestChatRoomCreate:
    def setup_class(self):
        self.new_chat_room_name = "新建聊天室name"
        self.new_chat_description = "新建聊天室description"

    @pytest.fixture(scope="class")
    def before_test(self, start_demo):
        token_1 = start_demo
        chat_room_remove_all(token_1)

    @allure.story("不传递聊天室名称和聊天室描述创建聊天室场景")
    @allure.title("test_chat_room_create_without_name_and_description")
    def test_chat_room_create_without_name_and_description(self, start_demo):
        """
        1:不传递聊天室名称和聊天室描述创建聊天
        2:断言创建聊天室的返回值的code=0，断言聊天室的名称name等于默认的'anoyGroup'
          断言聊天室的描述description等于'该聊天室还未有签名描述'
        :param start_demo:
        :return:
        """
        token_1 = start_demo
        res = chat_room_create(token_1)
        my_log("不传递聊天室名称和聊天室描述创建聊天室场景", {}, res)
        assert res["code"] == "0"
        assert res["data"]['name'] == 'anoyGroup'
        assert res["data"]['description'] == '该聊天室还未有签名描述'

    @allure.story("传递聊天室名称和聊天室描述创建聊天室场景")
    @allure.title("test_chat_room_create_with_name_and_description")
    def test_chat_room_create_with_name_and_description(self, start_demo):
        """
        1:传递聊天室名称和聊天室描述创建聊天
        2:断言创建聊天室的返回值的code=0，断言聊天室的名称name等于传递的name'
          断言聊天室的描述description等于传递的description'
        :param start_demo:
        :return:
        """
        token_1 = start_demo
        try:
            res = chat_room_create(token_1,
                                   chat_room_name=self.new_chat_room_name,
                                   description=self.new_chat_description)
            my_log("传递聊天室名称和聊天室描述创建聊天室场景",
                   {"chatRoomName": self.new_chat_room_name, "description": self.new_chat_description}, res)
            assert res["code"] == "0"
            assert res["data"]['name'] == self.new_chat_room_name
            assert res["data"]['description'] == self.new_chat_description
            print(res)
        except Exception as e:
            my_log("传递聊天室名称和聊天室描述创建聊天室场景",
                   {"chatRoomName": self.new_chat_room_name, "description": self.new_chat_description},
                   "创建聊天室时间超时,创建失败")
            print("创建聊天室时间超时,创建失败")
            raise e
