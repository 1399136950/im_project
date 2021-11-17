# -*- coding:utf-8 -*-
# @project : teacher_sq
# @author  : xj
# @file   : test_socket_user.py
# @ide    : PyCharm
# @time    : 2021/3/30 15:13
import json
from time import sleep

import allure

from lib.im_api_lib.user import user_friend_list
from lib.im_socket_lib.sync_im_user import IMUser
from common.my_log import my_log
from config.conf import USER_INFO


@allure.feature("发送单聊消息")
class TestSendSingleMsg:
    
    def setup_class(self):
        sender = IMUser(USER_INFO[2])   # 初始化发送方
        receiver = IMUser(USER_INFO[3])   # 初始化接收方
        
        sender_id = sender.user_id
        receiver_id = receiver.user_id
        
        sender.run()    # 后台线程运行
        receiver.run()  # 后台线程运行
        
        sender.accept_friend_group()
        receiver.accept_friend_group()
        
        sender.add_friend(receiver_id)
        receiver.add_friend(sender_id)
        
        self.sender = sender
        self.receiver = receiver
        
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        
        friend_lists_res = user_friend_list(self.sender.token)    # 发送方获取好友列表，找到与接收方的会话id
        self.communication_id = [i['conversationId'] for i in friend_lists_res['data'] if i['userId'] == self.receiver_id][0]  # 找到会话id
        
        sleep(2)
        self.sender.clean_msg()
        self.receiver.clean_msg()

    def teardown_class(self):
        self.sender.logout()    # 关闭socket，结束后台线程
        self.receiver.logout()  # 关闭socket，结束后台线程
    
    def teardown_method(self):
        self.sender.clean_msg()
        self.receiver.clean_msg()
    
    @allure.story("音频消息")
    def test_send_audio_msg(self):
        src_msg = self.sender.send_audio_msg(self.communication_id, 1, self.receiver_id)    # 返回发送方发送的原始消息
        my_log('test_send_audio_msg', src_msg, '')
        reply_msg = self.sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        assert reply_msg is not None
        my_log('test_send_audio_msg', '', reply_msg)
        msg_id = reply_msg['message_id']
        
        dst_msg = self.receiver.find_communication_msg_by_id(self.communication_id, msg_id)   # 从receiver的communication_msg中找到发送方发送的消息
        my_log('test_send_audio_msg', '', dst_msg)
        
        assert dst_msg is not None
        assert dst_msg['msg_file'] == src_msg['msg_file']
        assert dst_msg['from_user_id'] == self.sender_id
        assert dst_msg['to_user_id'] == self.receiver_id
        assert dst_msg['communication_id'] == self.communication_id
        assert dst_msg['tag'] == src_msg['tag']
        assert dst_msg['communication_type'] == src_msg['communication_type']
        assert dst_msg['message_type'] == src_msg['message_type']
        assert dst_msg['message_main_type'] == src_msg['message_main_type']
        assert dst_msg['send_time'] == reply_msg['send_time']
        assert dst_msg['app_id'] == src_msg['app_id']
        assert dst_msg['communication_show'] is True
        
    @allure.story("文件消息")
    def test_send_file_msg(self):
        
        src_msg = self.sender.send_file_msg(self.communication_id, 1, self.receiver_id)    # 返回发送方发送的原始消息
        my_log('test_send_file_msg', src_msg, '')
        reply_msg = self.sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        assert reply_msg is not None
        my_log('test_send_file_msg', '', reply_msg)
        msg_id = reply_msg['message_id']
        
        dst_msg = self.receiver.find_communication_msg_by_id(self.communication_id, msg_id)   # 从receiver的communication_msg中找到发送方发送的消息
        my_log('test_send_file_msg', '', dst_msg)
        assert dst_msg is not None
        assert dst_msg['msg_file'] == src_msg['msg_file']
        assert dst_msg['from_user_id'] == self.sender_id
        assert dst_msg['to_user_id'] == self.receiver_id
        assert dst_msg['communication_id'] == self.communication_id
        assert dst_msg['tag'] == src_msg['tag']
        assert dst_msg['communication_type'] == src_msg['communication_type']
        assert dst_msg['message_type'] == src_msg['message_type']
        assert dst_msg['message_main_type'] == src_msg['message_main_type']
        assert dst_msg['send_time'] == reply_msg['send_time']
        assert dst_msg['app_id'] == src_msg['app_id']
        assert dst_msg['communication_show'] is True

    @allure.story("视频消息")
    def test_send_video_msg(self):
        
        src_msg = self.sender.send_video_msg(self.communication_id, 1, self.receiver_id)    # 返回发送方发送的原始消息
        my_log('test_send_video_msg', src_msg, '')
        reply_msg = self.sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        assert reply_msg is not None
        my_log('test_send_video_msg', '', reply_msg)
        msg_id = reply_msg['message_id']
        
        dst_msg = self.receiver.find_communication_msg_by_id(self.communication_id, msg_id)   # 从receiver的communication_msg中找到发送方发送的消息
        my_log('test_send_video_msg', '', dst_msg)
        assert dst_msg is not None
        assert dst_msg['msg_file'] == src_msg['msg_file']
        assert dst_msg['from_user_id'] == self.sender_id
        assert dst_msg['to_user_id'] == self.receiver_id
        assert dst_msg['communication_id'] == self.communication_id
        assert dst_msg['tag'] == src_msg['tag']
        assert dst_msg['communication_type'] == src_msg['communication_type']
        assert dst_msg['message_type'] == src_msg['message_type']
        assert dst_msg['message_main_type'] == src_msg['message_main_type']
        assert dst_msg['send_time'] == reply_msg['send_time']
        assert dst_msg['app_id'] == src_msg['app_id']
        assert dst_msg['communication_show'] is True
        
    @allure.story("图片消息")
    def test_send_image_msg(self):
        src_msg = self.sender.send_image_msg(self.communication_id, 1, self.receiver_id)    # 返回发送方发送的原始消息
        my_log('test_send_image_msg', src_msg, '')
        reply_msg = self.sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        assert reply_msg is not None
        my_log('test_send_image_msg', '', reply_msg)
        msg_id = reply_msg['message_id']
        
        dst_msg = self.receiver.find_communication_msg_by_id(self.communication_id, msg_id)   # 从receiver的communication_msg中找到发送方发送的消息
        my_log('test_send_image_msg', '', dst_msg)
        assert dst_msg is not None
        assert dst_msg['msg_file'] == src_msg['msg_file']
        assert dst_msg['from_user_id'] == self.sender_id
        assert dst_msg['to_user_id'] == self.receiver_id
        assert dst_msg['communication_id'] == self.communication_id
        assert dst_msg['tag'] == src_msg['tag']
        assert dst_msg['communication_type'] == src_msg['communication_type']
        assert dst_msg['message_type'] == src_msg['message_type']
        assert dst_msg['message_main_type'] == src_msg['message_main_type']
        assert dst_msg['send_time'] == reply_msg['send_time']
        assert dst_msg['app_id'] == src_msg['app_id']
        assert dst_msg['communication_show'] is True
    
    @allure.story("文本消息")
    def test_send_text_msg(self):
        text_content = 'hello world python 123456'
        src_msg = self.sender.send_text_msg(self.communication_id, 1, text_content, self.receiver_id)    # 返回发送方发送的原始消息
        my_log('test_send_text_msg', src_msg, '')
        reply_msg = self.sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        assert reply_msg is not None
        my_log('test_send_text_msg', '', reply_msg)
        msg_id = reply_msg['message_id']
        
        dst_msg = self.receiver.find_communication_msg_by_id(self.communication_id, msg_id)   # 从receiver的communication_msg中找到发送方发送的消息
        my_log('test_send_text_msg', '', dst_msg)
        assert dst_msg is not None
        assert dst_msg['content'] == text_content
        assert 'msg_file' not in dst_msg or dst_msg['msg_file'] == {}
        assert dst_msg['from_user_id'] == self.sender_id
        assert dst_msg['to_user_id'] == self.receiver_id
        assert dst_msg['communication_id'] == self.communication_id
        assert dst_msg['tag'] == src_msg['tag']
        assert dst_msg['communication_type'] == src_msg['communication_type']
        assert dst_msg['message_type'] == src_msg['message_type']
        assert dst_msg['message_main_type'] == src_msg['message_main_type']
        assert dst_msg['send_time'] == reply_msg['send_time']
        assert dst_msg['app_id'] == src_msg['app_id']
        assert dst_msg['communication_show'] is True
    
    @allure.story("撤回消息")
    def test_recall_msg(self):
        src_msg = self.sender.send_image_msg(self.communication_id, 1, self.receiver_id)    # 返回发送方发送的原始消息
        my_log('test_recall_msg', src_msg, '')
        reply_msg = self.sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        assert reply_msg is not None
        my_log('test_recall_msg', reply_msg, '')
        msg_id = reply_msg['message_id']

        dst_msg = self.receiver.find_communication_msg_by_id(self.communication_id, msg_id)   # 从receiver的communication_msg中找到发送方发送的消息
        my_log('test_recall_msg', '', dst_msg)
        assert dst_msg is not None
        assert dst_msg['msg_file'] == src_msg['msg_file']
        assert dst_msg['from_user_id'] == self.sender_id
        assert dst_msg['to_user_id'] == self.receiver_id
        assert dst_msg['communication_id'] == self.communication_id
        assert dst_msg['tag'] == src_msg['tag']
        assert dst_msg['communication_type'] == src_msg['communication_type']
        assert dst_msg['message_type'] == src_msg['message_type']
        assert dst_msg['message_main_type'] == src_msg['message_main_type']
        assert dst_msg['send_time'] == reply_msg['send_time']
        assert dst_msg['app_id'] == src_msg['app_id']
        assert dst_msg['communication_show'] is True
        
        rtv = self.sender.recall_msg(self.communication_id, msg_id)
        my_log('test_recall_msg', '', rtv)
        assert rtv['code'] == '0'
    
        dst_msg = self.receiver.find_communication_msg_by_msg_main_type(self.communication_id, 100)  # 根据消息类型找到消息

        my_log('test_recall_msg', '', dst_msg)
        assert dst_msg['communication_id'] == self.communication_id
        assert dst_msg['from_user_id'] == self.sender_id
        assert dst_msg['to_user_id'] == self.receiver_id
        assert dst_msg['communication_type'] == src_msg['communication_type']
        assert dst_msg['message_main_type'] == 100
        assert dst_msg['message_type'] == 701   # 撤回通知
        assert dst_msg['app_id'] == src_msg['app_id']
        assert dst_msg['communication_show'] is True
        my_log('content', dst_msg['content'])
        assert json.loads(dst_msg['content']) == {"conversationType": src_msg['communication_type'], "notifyDesc": "消息已被撤回", "conversationId": self.communication_id, "nickname": self.sender.get_nickname(self.sender.user_info['user_id']), "messageId": int(msg_id), 'toUserId': self.receiver.user_id}

    @allure.story("位置消息")
    def test_address_msg(self):
        src_msg = self.sender.send_address_msg(self.communication_id, 1, self.receiver_id)    # 返回发送方发送的原始消息
        my_log('test_address_msg', src_msg, '')
        reply_msg = self.sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        assert reply_msg is not None
        my_log('test_address_msg', '', reply_msg)
        msg_id = reply_msg['message_id']
        
        dst_msg = self.receiver.find_communication_msg_by_id(self.communication_id, msg_id)   # 从receiver的communication_msg中找到发送方发送的消息
        my_log('test_address_msg', '', dst_msg)
        assert dst_msg is not None
        assert dst_msg['content'] == src_msg['content']
        assert dst_msg['from_user_id'] == self.sender_id
        assert dst_msg['to_user_id'] == self.receiver_id
        assert dst_msg['communication_id'] == self.communication_id
        assert dst_msg['tag'] == src_msg['tag']
        assert dst_msg['communication_type'] == src_msg['communication_type']
        assert dst_msg['message_type'] == src_msg['message_type']
        assert dst_msg['message_main_type'] == src_msg['message_main_type']
        assert dst_msg['msg_location'] == src_msg['msg_location']
        assert dst_msg['send_time'] == reply_msg['send_time']
        assert dst_msg['app_id'] == src_msg['app_id']
        assert dst_msg['communication_show'] is True
    
    @allure.story("阅后即焚消息")
    def test_read_destroy_msg(self):
        text_content = 'hello world python 123456'
        src_msg = self.sender.send_read_destroy_msg(self.communication_id, 1, text_content, self.receiver_id)    # 返回发送方发送的原始消息
        my_log('test_read_destroy_msg', src_msg, '')
        reply_msg = self.sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        assert reply_msg is not None
        my_log('test_read_destroy_msg', '', reply_msg)
        msg_id = reply_msg['message_id']
        
        dst_msg = self.receiver.find_communication_msg_by_id(self.communication_id, msg_id)   # 从receiver的communication_msg中找到发送方发送的消息
        my_log('test_read_destroy_msg', '', dst_msg)
        assert dst_msg is not None
        assert dst_msg['content'] == text_content
        assert 'msg_file' not in dst_msg or dst_msg['msg_file'] == {}
        assert dst_msg['from_user_id'] == self.sender_id
        assert dst_msg['to_user_id'] == self.receiver_id
        assert dst_msg['communication_id'] == self.communication_id
        assert dst_msg['tag'] == src_msg['tag']
        assert dst_msg['communication_type'] == src_msg['communication_type']
        assert dst_msg['message_type'] == src_msg['message_type']
        assert dst_msg['message_main_type'] == src_msg['message_main_type']
        assert dst_msg['other'] == src_msg['other']
        assert dst_msg['send_time'] == reply_msg['send_time']
        assert dst_msg['app_id'] == src_msg['app_id']
        assert dst_msg['communication_show'] is True
