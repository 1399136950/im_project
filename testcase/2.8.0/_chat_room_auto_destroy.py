# -*- coding:utf-8 -*-
# @author  : xj
# @ide    : PyCharm
# @time    : 2021/6/24 15:13
from threading import Thread
from time import sleep, localtime, strftime

import allure

from lib.im_socket_lib.sync_im_user import IMUser
from common.my_log import my_log
from config.conf import USER_INFO


class TestChatRoomAutoDestroy:

    def setup_class(self):
        self.im_user = IMUser(USER_INFO[0])
        self.normal_user = IMUser(USER_INFO[1])
        self.im_user.run()
        self.normal_user.run()
    
    def setup_method(self):
        res = self.im_user.create_chat_room()
        my_log('[setup_method] [创建聊天室]', '', res)
        if 'code' in res and res['code'] == '0':
            print(res)
            self.chat_room_id = res['data']['communicationId']
            self.create_time = res['data']['createTime']    # 创建时间
            
    def teardown_class(self):
        # self.im_user.remove_chat_room(self.chat_room_id)
        self.im_user.logout()
        self.normal_user.logout()
    
    def delay_exit_chat_room(self, chat_room_id, delay_time):
        def test():
            sleep(delay_time)
            res = self.im_user.exit_chat_room(chat_room_id)
            my_log('[delay_exit_chat_room]', '', res)
        Thread(target=test).start()
        
    def delay_enter_chat_room(self, im_user, chat_room_id, delay_time):
        def test():
            sleep(delay_time)
            res = im_user.enter_chat_room(chat_room_id)
            my_log('[delay_enter_chat_room]', '', res)
        Thread(target=test).start()
    
    def delay_enter_chat_room_and_send_msg(self, im_user, chat_room_id, delay_time):
        def test():
            sleep(delay_time)
            res = im_user.enter_chat_room(chat_room_id)
            my_log('[delay_enter_chat_room]', '', res)
            im_user.send_text_msg(chat_room_id, 3, 'hello world')
        Thread(target=test).start()
        
    @allure.story("创建聊天室后，不作任何操作")
    def test_auto_destroy_01(self):
        while 1:
            res = self.im_user.get_chat_room_detail(self.chat_room_id)
            my_log('[test_auto_destroy_01] [聊天室详情查询结果]', '', res)
            if res['code'] != '0':
                break
            sleep(60)
        destroy_time = strftime('%Y-%m-%d %H:%M:%S')
        create_time = strftime('%Y-%m-%d %H:%M:%S', localtime(self.create_time/1000))
        my_log('[test_auto_destroy_01] [聊天室创建时间]', create_time, '')
        my_log('[test_auto_destroy_01] [聊天室销毁时间]', destroy_time, '')
        chat_room_msg_list = self.im_user.communication_msg[self.chat_room_id]
        for msg in chat_room_msg_list:
            my_log('[test_auto_destroy_01] [聊天室消息]', msg, '')
            
    @allure.story("创建聊天室后，创建者进入聊天室")
    def test_auto_destroy_02(self):
        self.im_user.enter_chat_room(self.chat_room_id)
        # self.delay_enter_chat_room(self.normal_user, self.chat_room_id, 1200)  # 延迟1200秒后进入房间
        # self.delay_enter_chat_room_and_send_msg(self.normal_user, self.chat_room_id, 56*60)  # 延迟1200秒后进入房间
        while 1:
            res = self.im_user.get_chat_room_detail(self.chat_room_id)
            my_log('[test_auto_destroy_01] [聊天室详情查询结果]', '', res)
            if res['code'] != '0':
                break
            sleep(60)
        destroy_time = strftime('%Y-%m-%d %H:%M:%S')
        create_time = strftime('%Y-%m-%d %H:%M:%S', localtime(self.create_time/1000))
        my_log('[test_auto_destroy_01] [聊天室创建时间]', create_time, '')
        my_log('[test_auto_destroy_01] [聊天室销毁时间]', destroy_time, '')
        chat_room_msg_list = self.im_user.communication_msg[self.chat_room_id]
        for msg in chat_room_msg_list:
            my_log('[test_auto_destroy_01] [聊天室消息]', msg, '')
            
    @allure.story("创建聊天室后，其他人1200秒后进入聊天室")
    def test_auto_destroy_03(self):
        # self.im_user.enter_chat_room(self.chat_room_id)
        self.delay_enter_chat_room(self.normal_user, self.chat_room_id, 1200)  # 延迟1200秒后进入房间
        # self.delay_enter_chat_room_and_send_msg(self.normal_user, self.chat_room_id, 56*60)  # 延迟1200秒后进入房间
        while 1:
            res = self.im_user.get_chat_room_detail(self.chat_room_id)
            my_log('[test_auto_destroy_01] [聊天室详情查询结果]', '', res)
            if res['code'] != '0':
                break
            sleep(60)
        destroy_time = strftime('%Y-%m-%d %H:%M:%S')
        create_time = strftime('%Y-%m-%d %H:%M:%S', localtime(self.create_time/1000))
        my_log('[test_auto_destroy_01] [聊天室创建时间]', create_time, '')
        my_log('[test_auto_destroy_01] [聊天室销毁时间]', destroy_time, '')
        chat_room_msg_list = self.im_user.communication_msg[self.chat_room_id]
        for msg in chat_room_msg_list:
            my_log('[test_auto_destroy_01] [聊天室消息]', msg, '')
    
    @allure.story("创建聊天室后，其他人56分钟后进入聊天室并发送一条消息")
    def test_auto_destroy_04(self):
        # self.im_user.enter_chat_room(self.chat_room_id)
        # self.delay_enter_chat_room(self.normal_user, self.chat_room_id, 1200)  # 延迟1200秒后进入房间
        self.delay_enter_chat_room_and_send_msg(self.normal_user, self.chat_room_id, 56*60)  # 延迟56分钟后进入房间并发送消息
        while 1:
            res = self.im_user.get_chat_room_detail(self.chat_room_id)
            my_log('[test_auto_destroy_01] [聊天室详情查询结果]', '', res)
            if res['code'] != '0':
                break
            sleep(60)
        destroy_time = strftime('%Y-%m-%d %H:%M:%S')
        create_time = strftime('%Y-%m-%d %H:%M:%S', localtime(self.create_time/1000))
        my_log('[test_auto_destroy_01] [聊天室创建时间]', create_time, '')
        my_log('[test_auto_destroy_01] [聊天室销毁时间]', destroy_time, '')
        chat_room_msg_list = self.im_user.communication_msg[self.chat_room_id]
        for msg in chat_room_msg_list:
            my_log('[test_auto_destroy_01] [聊天室消息]', msg, '')
