# -*- coding:utf-8 -*-
# @author  : xj
# @ide    : PyCharm
# @time    : 2021/6/7 15:13
import json
from time import sleep
from random import choice

import pytest
import allure

from lib.im_socket_lib.sync_im_user import IMUser
from common.my_log import my_log
from config.conf import USER_INFO


@allure.feature("发送群聊消息")
class TestSendGroupMsg:
    def setup_class(self):
        self.users = {}
        self.user_id_list = []
        for _user_info in USER_INFO[:]:
            im_user = IMUser(_user_info)
            self.users[_user_info['user_id']] = im_user
            self.user_id_list.append(_user_info['user_id'])
        for user_id in self.users:
            self.users[user_id].run()
        sleep(3)
        for user_id in self.users:
            r1, r2 = self.users[user_id].accept_friend_group()   # 允许自动入群和自动加好友
            assert r1['code'] == '0' and r2['code'] == '0', '设置自动入群和自动加好友异常'
        for user_id in self.users:
            for _user_id in self.user_id_list:
                if _user_id == user_id:
                    continue
                self.users[user_id].add_friend(_user_id)
        sleep(3)
        for user_id in self.users:
            self.users[user_id].clean_msg()
    
    def setup_method(self):
        group_owner_id = choice(self.user_id_list)
        tmp_user_id_list = self.user_id_list[:]
        tmp_user_id_list.remove(group_owner_id)
        self.group_owner = self.users[group_owner_id]
        create_group_res = self.group_owner.create_group(','.join(tmp_user_id_list))
        assert create_group_res['code'] == '0', create_group_res

        self.group_id = create_group_res['data']['communicationId']
        sleep(2.5)
        group_member_res = self.group_owner.get_group_user_list(self.group_id)

        group_member_list = [i['userId'] for i in group_member_res['data']]
        assert sorted(self.user_id_list) == sorted(group_member_list)
    
    def teardown_method(self):
        self.group_owner.remove_group(self.group_id)
        for user_id in self.users:
            self.users[user_id].clean_msg()
        
    def teardown_class(self):
        for user_id in self.users:
            self.users[user_id].logout()
    
    @allure.story("文本消息")
    def test_send_text_msg(self):
        content = 'hello world'
        sender_id = choice(self.user_id_list)
        sender = self.users[sender_id]
        src_msg = sender.send_text_msg(self.group_id, 2, content)
        reply_msg = sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        assert reply_msg is not None
        my_log('test_send_text_msg', src_msg, reply_msg)
        msg_id = reply_msg['message_id']
        for user_id in self.user_id_list:
            if user_id == sender_id:
                continue
            receiver = self.users[user_id]
            dst_msg = receiver.find_communication_msg_by_id(self.group_id, msg_id)   # 从receiver的communication_msg中找到发送方发送的消息
            my_log('test_send_text_msg', '', dst_msg)
            assert dst_msg is not None
            assert dst_msg['app_id'] == src_msg['app_id']
            assert dst_msg['content'] == content
            assert 'msg_file' not in dst_msg or dst_msg['msg_file'] == {}
            assert dst_msg['from_user_id'] == sender_id
            assert dst_msg['communication_id'] == self.group_id
            assert dst_msg['tag'] == src_msg['tag']
            assert dst_msg['communication_type'] == src_msg['communication_type']
            assert dst_msg['message_type'] == src_msg['message_type']
            assert dst_msg['message_main_type'] == src_msg['message_main_type']
            assert dst_msg['other'] == src_msg['other']
            assert dst_msg['send_time'] == reply_msg['send_time']
            assert dst_msg['communication_show'] is True
            
    @allure.story("音频消息")
    def test_send_audio_msg(self):
        sender_id = choice(self.user_id_list)
        sender = self.users[sender_id]
        src_msg = sender.send_audio_msg(self.group_id, 2)
        reply_msg = sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        assert reply_msg is not None
        my_log('test_send_audio_msg', src_msg, reply_msg)
        msg_id = reply_msg['message_id']
        for user_id in self.user_id_list:
            if user_id == sender_id:
                continue
            receiver = self.users[user_id]
            dst_msg = receiver.find_communication_msg_by_id(self.group_id, msg_id)   # 从receiver的communication_msg中找到发送方发送的消息
            my_log('test_send_audio_msg', '', dst_msg)
            assert dst_msg is not None
            assert dst_msg['app_id'] == src_msg['app_id']
            assert dst_msg['msg_file'] == src_msg['msg_file']
            assert dst_msg['from_user_id'] == sender_id
            assert dst_msg['communication_id'] == self.group_id
            assert dst_msg['tag'] == src_msg['tag']
            assert dst_msg['communication_type'] == src_msg['communication_type']
            assert dst_msg['message_type'] == src_msg['message_type']
            assert dst_msg['message_main_type'] == src_msg['message_main_type']
            assert dst_msg['other'] == src_msg['other']
            assert dst_msg['send_time'] == reply_msg['send_time']
            assert dst_msg['communication_show'] is True
            
    @allure.story("文件消息")
    def test_send_file_msg(self):
        sender_id = choice(self.user_id_list)
        sender = self.users[sender_id]
        src_msg = sender.send_file_msg(self.group_id, 2)
        reply_msg = sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        assert reply_msg is not None
        my_log('test_send_file_msg', src_msg, reply_msg)
        msg_id = reply_msg['message_id']
        for user_id in self.user_id_list:
            if user_id == sender_id:
                continue
            receiver = self.users[user_id]
            dst_msg = receiver.find_communication_msg_by_id(self.group_id, msg_id)   # 从receiver的communication_msg中找到发送方发送的消息
            my_log('test_send_file_msg', '', dst_msg)
            assert dst_msg is not None
            assert dst_msg['app_id'] == src_msg['app_id']
            assert dst_msg['msg_file'] == src_msg['msg_file']
            assert dst_msg['from_user_id'] == sender_id
            assert dst_msg['communication_id'] == self.group_id
            assert dst_msg['tag'] == src_msg['tag']
            assert dst_msg['communication_type'] == src_msg['communication_type']
            assert dst_msg['message_type'] == src_msg['message_type']
            assert dst_msg['message_main_type'] == src_msg['message_main_type']
            assert dst_msg['other'] == src_msg['other']
            assert dst_msg['send_time'] == reply_msg['send_time']
            assert dst_msg['communication_show'] is True
            
    @allure.story("视频消息")
    def test_send_video_msg(self):
        sender_id = choice(self.user_id_list)
        sender = self.users[sender_id]
        src_msg = sender.send_file_msg(self.group_id, 2)
        reply_msg = sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        assert reply_msg is not None
        my_log('test_send_video_msg', src_msg, reply_msg)
        msg_id = reply_msg['message_id']
        for user_id in self.user_id_list:
            if user_id == sender_id:
                continue
            receiver = self.users[user_id]
            dst_msg = receiver.find_communication_msg_by_id(self.group_id, msg_id)   # 从receiver的communication_msg中找到发送方发送的消息
            my_log('test_send_video_msg', '', dst_msg)
            assert dst_msg is not None
            assert dst_msg['app_id'] == src_msg['app_id']
            assert dst_msg['msg_file'] == src_msg['msg_file']
            assert dst_msg['from_user_id'] == sender_id
            assert dst_msg['communication_id'] == self.group_id
            assert dst_msg['tag'] == src_msg['tag']
            assert dst_msg['communication_type'] == src_msg['communication_type']
            assert dst_msg['message_type'] == src_msg['message_type']
            assert dst_msg['message_main_type'] == src_msg['message_main_type']
            assert dst_msg['other'] == src_msg['other']
            assert dst_msg['send_time'] == reply_msg['send_time']
            assert dst_msg['communication_show'] is True
        
    @allure.story("图片消息")
    def test_send_image_msg(self):
        sender_id = choice(self.user_id_list)
        sender = self.users[sender_id]
        src_msg = sender.send_image_msg(self.group_id, 2)
        reply_msg = sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        my_log('test_send_image_msg', src_msg, reply_msg)
        assert reply_msg is not None
        msg_id = reply_msg['message_id']
        for user_id in self.user_id_list:
            if user_id == sender_id:
                continue
            receiver = self.users[user_id]
            dst_msg = receiver.find_communication_msg_by_id(self.group_id, msg_id)   # 从receiver的communication_msg中找到发送方发送的消息
            my_log('test_send_image_msg', '', dst_msg)
            assert dst_msg is not None
            assert dst_msg['app_id'] == src_msg['app_id']
            assert dst_msg['msg_file'] == src_msg['msg_file']
            assert dst_msg['from_user_id'] == sender_id
            assert dst_msg['communication_id'] == self.group_id
            assert dst_msg['tag'] == src_msg['tag']
            assert dst_msg['communication_type'] == src_msg['communication_type']
            assert dst_msg['message_type'] == src_msg['message_type']
            assert dst_msg['message_main_type'] == src_msg['message_main_type']
            assert dst_msg['other'] == src_msg['other']
            assert dst_msg['send_time'] == reply_msg['send_time']
            assert dst_msg['communication_show'] is True
            
    @allure.story("位置消息")
    def test_address_msg(self):
        sender_id = choice(self.user_id_list)
        sender = self.users[sender_id]
        src_msg = sender.send_address_msg(self.group_id, 2)
        reply_msg = sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        my_log('test_address_msg', src_msg, reply_msg)
        assert reply_msg is not None
        msg_id = reply_msg['message_id']
        for user_id in self.user_id_list:
            if user_id == sender_id:
                continue
            receiver = self.users[user_id]
            dst_msg = receiver.find_communication_msg_by_id(self.group_id, msg_id)   # 从receiver的communication_msg中找到发送方发送的消息
            my_log('test_address_msg', '', dst_msg)
            assert dst_msg is not None
            assert dst_msg['app_id'] == src_msg['app_id']
            assert 'msg_file' not in dst_msg or dst_msg['msg_file'] == {}
            assert dst_msg['from_user_id'] == sender_id
            assert dst_msg['communication_id'] == self.group_id
            assert dst_msg['tag'] == src_msg['tag']
            assert dst_msg['communication_type'] == src_msg['communication_type']
            assert dst_msg['message_type'] == src_msg['message_type']
            assert dst_msg['message_main_type'] == src_msg['message_main_type']
            assert dst_msg['other'] == src_msg['other']
            assert dst_msg['send_time'] == reply_msg['send_time']
            assert dst_msg['msg_location'] == src_msg['msg_location']
            assert dst_msg['communication_show'] is True
            
    @allure.story("阅后即焚消息")
    def test_read_destroy_msg(self):
        text_content = 'hello world python 123456'
        sender_id = choice(self.user_id_list)
        sender = self.users[sender_id]
        src_msg = sender.send_read_destroy_msg(self.group_id, 2, text_content)    # 返回发送方发送的原始消息
        reply_msg = sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        my_log('test_read_destroy_msg', src_msg, reply_msg)
        assert reply_msg is not None
        msg_id = reply_msg['message_id']
        for user_id in self.user_id_list:
            if user_id == sender_id:
                continue
            receiver = self.users[user_id]
            dst_msg = receiver.find_communication_msg_by_id(self.group_id, msg_id)   # 从receiver的communication_msg中找到发送方发送的消息
            my_log('test_read_destroy_msg', '', dst_msg)
            assert dst_msg is not None
            assert dst_msg['app_id'] == src_msg['app_id']
            assert dst_msg['content'] == text_content
            assert 'msg_file' not in dst_msg or dst_msg['msg_file'] == {}
            assert dst_msg['from_user_id'] == sender_id
            assert dst_msg['communication_id'] == self.group_id
            assert dst_msg['tag'] == src_msg['tag']
            assert dst_msg['communication_type'] == src_msg['communication_type']
            assert dst_msg['message_type'] == src_msg['message_type']
            assert dst_msg['message_main_type'] == src_msg['message_main_type']
            assert dst_msg['other'] == src_msg['other']
            assert dst_msg['send_time'] == reply_msg['send_time']
            assert dst_msg['communication_show'] is True

    @allure.story("撤回消息")
    def test_recall_msg(self):
        sender_id = choice(self.user_id_list)
        sender = self.users[sender_id]
        src_msg = sender.send_image_msg(self.group_id, 2)    # 返回发送方发送的原始消息
        
        reply_msg = sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        my_log('test_recall_msg', src_msg, reply_msg)
        assert reply_msg is not None
        msg_id = reply_msg['message_id']

        for user_id in self.user_id_list:
            if user_id == sender_id:
                continue
            receiver = self.users[user_id]
            dst_msg = receiver.find_communication_msg_by_id(self.group_id, msg_id)   # 从receiver的communication_msg中找到发送方发送的消息
            my_log('test_recall_msg', '', dst_msg)
            assert dst_msg is not None
            assert dst_msg['app_id'] == src_msg['app_id']
            assert dst_msg['msg_file'] == src_msg['msg_file']
            assert dst_msg['from_user_id'] == sender_id
            assert dst_msg['communication_id'] == self.group_id
            assert dst_msg['tag'] == src_msg['tag']
            assert dst_msg['communication_type'] == src_msg['communication_type']
            assert dst_msg['message_type'] == src_msg['message_type']
            assert dst_msg['message_main_type'] == src_msg['message_main_type']
            assert dst_msg['other'] == src_msg['other']
            assert dst_msg['send_time'] == reply_msg['send_time']
            assert dst_msg['communication_show'] is True
        
        for user_id in self.users:
            self.users[user_id].clean_msg()
        
        rtv = sender.recall_msg(self.group_id, msg_id)
        my_log('test_recall_msg', f'{sender.user_info["user_id"]}, {self.group_id}, {msg_id}', rtv)
        assert rtv['code'] == '0'
        
        for user_id in self.user_id_list:
            if user_id == sender_id:
                continue
            receiver = self.users[user_id]
            dst_msg = receiver.find_communication_msg_by_msg_main_type(self.group_id, 100)  # 根据消息类型找到消息
            my_log('test_recall_msg', '', dst_msg)
            assert dst_msg['app_id'] == src_msg['app_id']
            assert dst_msg['communication_id'] == self.group_id
            assert dst_msg['from_user_id'] == sender_id
            assert dst_msg['to_user_id'] == self.group_id
            assert dst_msg['communication_type'] == src_msg['communication_type']
            assert dst_msg['message_main_type'] == 100
            assert dst_msg['message_type'] == 701   # 撤回通知
            assert dst_msg['communication_show'] is True
            assert json.loads(dst_msg['content']) == {"conversationType": src_msg['communication_type'], "notifyDesc": "消息已被撤回", "conversationId": self.group_id, "nickname": sender.get_nickname(sender_id), "messageId": int(msg_id)}

    @allure.story('设置全员禁言然后发言')
    @pytest.mark.parametrize('user_identity, expect_result', ((0, True), (1, True), (2, False), (3, False), (4, True)))
    def test_set_all_mute(self, user_identity, expect_result):
        """
        设置全员禁言然后发言
        :param user_identity: 用户身份, 0:群主， 1：管理员， 2:普通成员, 3:禁言用户， 4：禁言白名单用户
        :param expect_result: 用户能否正常发言
        :return:
        """
        set_all_mute_res = self.group_owner.set_group_all_mute(self.group_id, True)
        assert set_all_mute_res['code'] == '0'

        if user_identity == 0:
            sender_id = self.group_owner.user_id
            sender = self.group_owner
        elif user_identity == 1:
            sender_id = choice(self.user_id_list)
            while sender_id == self.group_owner.user_id:
                sender_id = choice(self.user_id_list)
            sender = self.users[sender_id]
            set_manager_res = self.group_owner.set_group_manager(self.group_id, sender_id, 'add')
            assert set_manager_res['code'] == '0'
        elif user_identity == 2:
            sender_id = choice(self.user_id_list)
            while sender_id == self.group_owner.user_id:
                sender_id = choice(self.user_id_list)
            sender = self.users[sender_id]
        elif user_identity == 3:
            sender_id = choice(self.user_id_list)
            while sender_id == self.group_owner.user_id:
                sender_id = choice(self.user_id_list)
            sender = self.users[sender_id]
            set_mute_res = self.group_owner.set_group_mute(self.group_id, sender_id, 'add')
            assert set_mute_res['code'] == '0'
        elif user_identity == 4:
            sender_id = choice(self.user_id_list)
            while sender_id == self.group_owner.user_id:
                sender_id = choice(self.user_id_list)
            sender = self.users[sender_id]
            set_white_list_res = self.group_owner.set_group_white_list(self.group_id, sender_id, 'add')
            assert set_white_list_res['code'] == '0'
        else:
            raise Exception('unknow user identity')

        sleep(2)

        src_msg = sender.send_text_msg(self.group_id, 2, 'hello world')
        reply_msg = sender.find_reply_msg_by_tag(src_msg['tag'])
        my_log('', reply_msg)
        assert reply_msg is not None

        msg_id = reply_msg['message_id']
        if expect_result:
            for user_id in self.user_id_list:
                if user_id == sender_id:
                    continue
                receiver = self.users[user_id]
                dst_msg = receiver.find_communication_msg_by_id(self.group_id, msg_id)
                my_log(user_id, dst_msg)
                assert dst_msg is not None
                assert dst_msg['message_id'] == msg_id
        else:
            assert 'resp' in reply_msg and reply_msg['resp'] == {'ret': 1617, 'errorCode': '已被禁言'}
            for user_id in self.user_id_list:
                if user_id == sender_id:
                    continue
                receiver = self.users[user_id]
                dst_msg = receiver.find_communication_msg_by_id(self.group_id, msg_id)
                my_log(user_id, dst_msg)
                assert dst_msg is None
