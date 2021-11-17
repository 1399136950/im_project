# -*- coding:utf-8 -*-
# @author  : xj
# @ide    : PyCharm
# @time    : 2021/8/23 15:13
import json

from time import sleep
from random import choice

import allure

from lib.im_socket_lib.sync_im_user import IMUser
from common.my_log import my_log
from config.conf import USER_INFO


@allure.feature("发送聊天室消息")
class TestSendChatRoomMsg:
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
            self.users[user_id].clean_msg()
    
    def setup_method(self):
        chat_room_owner_id = choice(self.user_id_list)
        im_user = self.users[chat_room_owner_id]
        res = im_user.create_chat_room()
        self.chat_room_id = res['data']['communicationId']
        for user_id in self.users:
            self.users[user_id].enter_chat_room(self.chat_room_id)  # 进入聊天室
        sleep(1)
        self.chat_room_owner = im_user
        for user_id in self.users:
            self.users[user_id].clean_msg()  # 进入聊天室

    def teardown_method(self):
        for user_id in self.users:
            self.users[user_id].exit_chat_room(self.chat_room_id)  # 离开聊天室
        self.chat_room_owner.remove_chat_room(self.chat_room_id)    # 销毁聊天室
        
    def teardown_class(self):
        for user_id in self.users:
            self.users[user_id].logout()
    
    @allure.story("文本消息")
    def test_send_text_msg(self):
        content = 'hello world'
        sender_id = choice(self.user_id_list)
        sender = self.users[sender_id]
        src_msg = sender.send_text_msg(self.chat_room_id, 3, content)
        reply_msg = sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        assert reply_msg is not None
        my_log('test_send_text_msg', src_msg, reply_msg)
        msg_id = reply_msg['message_id']
        for user_id in self.user_id_list:
            if user_id == sender_id:
                continue
            receiver = self.users[user_id]
            dst_msg = receiver.find_communication_msg_by_id(self.chat_room_id, msg_id)   # 从receiver的communication_msg中找到发送方发送的消息
            my_log('test_send_text_msg', '', dst_msg)
            assert dst_msg is not None
            assert dst_msg['app_id'] == src_msg['app_id']
            assert dst_msg['content'] == content
            assert 'msg_file' not in dst_msg or dst_msg['msg_file'] == {}
            assert dst_msg['from_user_id'] == sender_id
            assert dst_msg['communication_id'] == self.chat_room_id
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
        src_msg = sender.send_audio_msg(self.chat_room_id, 3)
        reply_msg = sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        assert reply_msg is not None
        my_log('test_send_audio_msg', src_msg, reply_msg)
        msg_id = reply_msg['message_id']
        for user_id in self.user_id_list:
            if user_id == sender_id:
                continue
            receiver = self.users[user_id]
            dst_msg = receiver.find_communication_msg_by_id(self.chat_room_id, msg_id)   # 从receiver的communication_msg中找到发送方发送的消息
            my_log('test_send_audio_msg', '', dst_msg)
            assert dst_msg is not None
            assert dst_msg['app_id'] == src_msg['app_id']
            assert dst_msg['msg_file'] == src_msg['msg_file']
            assert dst_msg['from_user_id'] == sender_id
            assert dst_msg['communication_id'] == self.chat_room_id
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
        src_msg = sender.send_file_msg(self.chat_room_id, 3)
        reply_msg = sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        assert reply_msg is not None
        my_log('test_send_file_msg', src_msg, reply_msg)
        msg_id = reply_msg['message_id']
        for user_id in self.user_id_list:
            if user_id == sender_id:
                continue
            receiver = self.users[user_id]
            dst_msg = receiver.find_communication_msg_by_id(self.chat_room_id, msg_id)   # 从receiver的communication_msg中找到发送方发送的消息
            my_log('test_send_file_msg', '', dst_msg)
            assert dst_msg is not None
            assert dst_msg['app_id'] == src_msg['app_id']
            assert dst_msg['msg_file'] == src_msg['msg_file']
            assert dst_msg['from_user_id'] == sender_id
            assert dst_msg['communication_id'] == self.chat_room_id
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
        src_msg = sender.send_file_msg(self.chat_room_id, 3)
        reply_msg = sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        assert reply_msg is not None
        my_log('test_send_video_msg', src_msg, reply_msg)
        msg_id = reply_msg['message_id']
        for user_id in self.user_id_list:
            if user_id == sender_id:
                continue
            receiver = self.users[user_id]
            dst_msg = receiver.find_communication_msg_by_id(self.chat_room_id, msg_id)   # 从receiver的communication_msg中找到发送方发送的消息
            my_log('test_send_video_msg', '', dst_msg)
            assert dst_msg is not None
            assert dst_msg['app_id'] == src_msg['app_id']
            assert dst_msg['msg_file'] == src_msg['msg_file']
            assert dst_msg['from_user_id'] == sender_id
            assert dst_msg['communication_id'] == self.chat_room_id
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
        src_msg = sender.send_image_msg(self.chat_room_id, 3)
        reply_msg = sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        my_log('test_send_image_msg', src_msg, reply_msg)
        assert reply_msg is not None
        msg_id = reply_msg['message_id']
        for user_id in self.user_id_list:
            if user_id == sender_id:
                continue
            receiver = self.users[user_id]
            dst_msg = receiver.find_communication_msg_by_id(self.chat_room_id, msg_id)   # 从receiver的communication_msg中找到发送方发送的消息
            my_log('test_send_image_msg', '', dst_msg)
            assert dst_msg is not None
            assert dst_msg['app_id'] == src_msg['app_id']
            assert dst_msg['msg_file'] == src_msg['msg_file']
            assert dst_msg['from_user_id'] == sender_id
            assert dst_msg['communication_id'] == self.chat_room_id
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
        src_msg = sender.send_address_msg(self.chat_room_id, 3)
        reply_msg = sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        my_log('test_address_msg', src_msg, reply_msg)
        assert reply_msg is not None
        msg_id = reply_msg['message_id']
        for user_id in self.user_id_list:
            if user_id == sender_id:
                continue
            receiver = self.users[user_id]
            dst_msg = receiver.find_communication_msg_by_id(self.chat_room_id, msg_id)   # 从receiver的communication_msg中找到发送方发送的消息
            my_log('test_address_msg', '', dst_msg)
            assert dst_msg is not None
            assert dst_msg['app_id'] == src_msg['app_id']
            assert 'msg_file' not in dst_msg or dst_msg['msg_file'] == {}
            assert dst_msg['from_user_id'] == sender_id
            assert dst_msg['communication_id'] == self.chat_room_id
            assert dst_msg['tag'] == src_msg['tag']
            assert dst_msg['communication_type'] == src_msg['communication_type']
            assert dst_msg['message_type'] == src_msg['message_type']
            assert dst_msg['message_main_type'] == src_msg['message_main_type']
            assert dst_msg['other'] == src_msg['other']
            assert dst_msg['send_time'] == reply_msg['send_time']
            assert dst_msg['msg_location'] == src_msg['msg_location']
            assert dst_msg['communication_show'] is True
    '''
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
    '''
    
    @allure.story("撤回消息")
    def test_recall_msg(self):
        sender_id = choice(self.user_id_list)
        sender = self.users[sender_id]
        src_msg = sender.send_image_msg(self.chat_room_id, 3)    # 返回发送方发送的原始消息
        
        reply_msg = sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        my_log('test_recall_msg', src_msg, reply_msg)
        assert reply_msg is not None
        msg_id = reply_msg['message_id']

        for user_id in self.user_id_list:
            if user_id == sender_id:
                continue
            receiver = self.users[user_id]
            dst_msg = receiver.find_communication_msg_by_id(self.chat_room_id, msg_id)   # 从receiver的communication_msg中找到发送方发送的消息
            my_log('test_recall_msg', '', dst_msg)
            assert dst_msg is not None
            assert dst_msg['app_id'] == src_msg['app_id']
            assert dst_msg['msg_file'] == src_msg['msg_file']
            assert dst_msg['from_user_id'] == sender_id
            assert dst_msg['communication_id'] == self.chat_room_id
            assert dst_msg['tag'] == src_msg['tag']
            assert dst_msg['communication_type'] == src_msg['communication_type']
            assert dst_msg['message_type'] == src_msg['message_type']
            assert dst_msg['message_main_type'] == src_msg['message_main_type']
            assert dst_msg['other'] == src_msg['other']
            assert dst_msg['send_time'] == reply_msg['send_time']
            assert dst_msg['communication_show'] is True
        
        for user_id in self.users:
            self.users[user_id].clean_msg()
        
        rtv = sender.recall_msg(self.chat_room_id, msg_id)
        my_log('test_recall_msg', f'{sender.user_info["user_id"]}, {self.chat_room_id}, {msg_id}', rtv)
        assert rtv['code'] == '0'
        
        for user_id in self.user_id_list:
            if user_id == sender_id:
                continue
            receiver = self.users[user_id]
            dst_msg = receiver.find_communication_msg_by_msg_main_type(self.chat_room_id, 100)  # 根据消息类型找到消息
            my_log('test_recall_msg', '', dst_msg)
            assert dst_msg['app_id'] == src_msg['app_id']
            assert dst_msg['communication_id'] == self.chat_room_id
            assert dst_msg['from_user_id'] == sender_id
            assert dst_msg['to_user_id'] == self.chat_room_id
            assert dst_msg['communication_type'] == src_msg['communication_type']
            assert dst_msg['message_main_type'] == 100
            assert dst_msg['message_type'] == 701   # 撤回通知
            assert dst_msg['communication_show'] is True
            assert json.loads(dst_msg['content']) == {"conversationType": src_msg['communication_type'], "notifyDesc": "消息已被撤回", "conversationId": self.chat_room_id, "nickname": sender.get_nickname(sender_id), "messageId": int(msg_id)}

    @allure.story('聊天室设置全员禁言, 普通成员发言')
    def test_set_all_mute(self):
        set_all_mute_res = self.chat_room_owner.set_chat_room_all_mute(self.chat_room_id, True)
        assert set_all_mute_res['code'] == '0'

        sender_id = choice(self.user_id_list)
        while sender_id == self.chat_room_owner.user_id:
            sender_id = choice(self.user_id_list)
        sender = self.users[sender_id]
        src_msg = sender.send_text_msg(self.chat_room_id, 3, 'hello world')

        reply_msg = sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        my_log('test_set_all_mute', src_msg, reply_msg)
        assert reply_msg is not None
        assert 'resp' in reply_msg and reply_msg['resp'] == {'ret': 1617, 'errorCode': '已被禁言'}

        msg_id = reply_msg['message_id']

        for user_id in self.user_id_list:
            if user_id == sender_id:
                continue
            receiver = self.users[user_id]
            dst_msg = receiver.find_communication_msg_by_id(self.chat_room_id, msg_id)   # 从receiver的communication_msg中找到发送方发送的消息
            my_log('', dst_msg)
            assert dst_msg is None

    @allure.story('设置指定普通成员禁言, 然后普通成员发言')
    def test_set_user_mute(self):
        sender_id = choice(self.user_id_list)
        while sender_id == self.chat_room_owner.user_id:
            sender_id = choice(self.user_id_list)
        sender = self.users[sender_id]

        set_mute_res = self.chat_room_owner.set_chat_room_mute(self.chat_room_id, sender_id, 'add')
        assert set_mute_res['code'] == '0'

        src_msg = sender.send_text_msg(self.chat_room_id, 3, 'hello world')

        reply_msg = sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        my_log(src_msg, reply_msg)
        assert reply_msg is not None
        assert 'resp' in reply_msg and reply_msg['resp'] == {'ret': 1617, 'errorCode': '已被禁言'}

        msg_id = reply_msg['message_id']

        for user_id in self.user_id_list:
            if user_id == sender_id:
                continue
            receiver = self.users[user_id]
            dst_msg = receiver.find_communication_msg_by_id(self.chat_room_id, msg_id)   # 从receiver的communication_msg中找到发送方发送的消息
            my_log('', dst_msg)
            assert dst_msg is None

    @allure.story('将指定成员加入黑名单, 然后该成员发言')
    def test_set_black_list(self):
        sender_id = choice(self.user_id_list)
        while sender_id == self.chat_room_owner.user_id:
            sender_id = choice(self.user_id_list)
        sender = self.users[sender_id]

        set_black_res = self.chat_room_owner.set_chat_room_black_list(self.chat_room_id, sender_id, 'add')
        assert set_black_res['code'] == '0'

        src_msg = sender.send_text_msg(self.chat_room_id, 3, 'hello world')

        reply_msg = sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        my_log(src_msg, reply_msg)
        assert reply_msg is not None
        assert 'resp' in reply_msg and reply_msg['resp'] == {'ret': 1619, 'errorCode': '群成员被踢出群'}

        msg_id = reply_msg['message_id']

        for user_id in self.user_id_list:
            if user_id == sender_id:
                continue
            receiver = self.users[user_id]
            dst_msg = receiver.find_communication_msg_by_id(self.chat_room_id, msg_id)   # 从receiver的communication_msg中找到发送方发送的消息
            my_log('', dst_msg)
            assert dst_msg is None
