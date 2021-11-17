# -*- coding:utf-8 -*-
# @project : test_socket_user
# @author  : xj
# @file   : test_socket_user_sensitive.py
# @ide    : PyCharm
# @time    : 2021/04/06 15:56
from time import sleep
from random import choice

import pytest
import allure

from lib.im_api_lib.user import user_friend_list
from lib.im_socket_lib.sync_im_user import IMUser
from common.my_log import my_log
from config.conf import USER_INFO


@allure.feature('单聊敏感词测试')
class TestSingleSensitive:
    """
    单聊敏感词
    """
    def setup_class(self):
        sender = IMUser(USER_INFO[0])   # 初始化发送方
        receiver = IMUser(USER_INFO[1])   # 初始化接收方
        
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
        
    @allure.story('单聊敏感词测试场景')
    @allure.title('test_send_sensitive')
    # @pytest.mark.parametrize("msg", ['专业代理', '專業代理', 'SM', 'sm', '3P', '买卖64狗', 'GFW', 'GFw', 'GfW', 'Gfw', 'gFW', 'gFw', 'gfW', 'gfw', 'tnt炸药配方', 'www2.92ri.com', 'GaY片', 'GAy片', 'Gay片', 'GAY片', 'gaY片', 'gAy片', 'gay片', 'gAY片', '專业代理', '專業代理', '专业代理', '专業代理', '々﹟#﹩$﹠&﹪%*﹡﹢﹦全套', '￣¯―﹨ˆ˜﹍﹎+=<＿_-\ˇ~﹉﹊（sm', '信用卡提现ˆˇ﹕︰﹔﹖﹑•¨….¸;！', 'youxing•¨….¸;！´？！', '操（）〈〉‹›﹛﹜『』〖〗［］《》〔〕{}「」【】逼', 'bao?‘’“”〝〞ˆˇ﹕︰﹔﹖luan'])
    @pytest.mark.parametrize("msg", ['专业代理', '專業代理', 'SM', 'sm', '3P', '买卖64狗', 'GFW', 'GFw', 'GfW', 'Gfw', 'gFW', 'gFw', 'gfW', 'gfw', 'tnt炸药配方', 'www2.92ri.com', 'GaY片', 'GAy片', 'Gay片', 'GAY片', 'gaY片', 'gAy片', 'gay片', 'gAY片', '專业代理', '專業代理', '专业代理', '专業代理', '々﹟#﹩$﹠&﹪%*﹡﹢﹦全套', r'￣¯―﹨ˆ˜﹍﹎+=<＿_-\ˇ~﹉﹊（sm', '信用卡提现ˆˇ﹕︰﹔﹖﹑•¨….¸;！', 'youxing•¨….¸;！´？！', '操（）〈〉‹›﹛﹜『』〖〗［］《》〔〕{}「」【】逼', '流血?‘’“”〝〞ˆˇ﹕︰﹔﹖冲突'])
    def test_send_sensitive(self, msg):
        src_msg = self.sender.send_text_msg(self.communication_id, 1, msg, self.receiver_id)    # 返回发送方发送的原始消息
        my_log('test_send_sensitive', src_msg, '')
        reply_msg = self.sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        my_log('test_send_sensitive', '', reply_msg)
        assert 'resp' in reply_msg and 'ret' in reply_msg['resp'] and reply_msg['resp']['ret'] == 1509 and reply_msg['resp']['errorCode'] == '您发送的文本消息中可能包含敏感词汇，请重新发送', '发送敏感词服务端无提示!'
    
    @allure.story('单聊敏感词白名单测试场景')
    @allure.title('test_send_sensitive_normal')
    @pytest.mark.parametrize("msg", ['EARLY', 'small'])
    def test_send_sensitive_normal(self, msg):
        src_msg = self.sender.send_text_msg(self.communication_id, 1, msg, self.receiver_id)    # 返回发送方发送的原始消息
        my_log('test_send_sensitive_normal', src_msg, '')
        reply_msg = self.sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        my_log('test_send_sensitive_normal', '', reply_msg)
        assert 'resp' in reply_msg and reply_msg['resp'] == {}
        assert 'message_id' in reply_msg
        msg_id = reply_msg['message_id']
        dst_msg = self.receiver.find_communication_msg_by_id(self.communication_id, msg_id)   # 从receiver的communication_msg中找到发送方发送的消息
        my_log('test_send_sensitive_normal', '', dst_msg)
        assert dst_msg is not None
        assert dst_msg['content'] == msg
        assert 'msg_file' not in dst_msg or dst_msg['msg_file'] == {}
        assert dst_msg['from_user_id'] == self.sender_id
        assert dst_msg['to_user_id'] == self.receiver_id
        assert dst_msg['communication_id'] == self.communication_id
        assert dst_msg['tag'] == src_msg['tag']
        assert dst_msg['communication_type'] == src_msg['communication_type']
        assert dst_msg['message_type'] == src_msg['message_type']
        assert dst_msg['message_main_type'] == src_msg['message_main_type']
        assert dst_msg['other'] == src_msg['other']
        
        
@allure.feature('群聊敏感词测试')
class TestGroupSensitive:

    def setup_class(self):
        sender = IMUser(USER_INFO[0])   # 初始化发送方
        receiver1 = IMUser(USER_INFO[1])   # 初始化接收方
        receiver2 = IMUser(USER_INFO[2])   # 初始化接收方
        receiver3 = IMUser(USER_INFO[3])   # 初始化接收方
        
        sender_id = sender.user_id
        receiver1_id = receiver1.user_id
        receiver2_id = receiver2.user_id
        receiver3_id = receiver3.user_id
        
        sender.run()        # 后台线程运行
        receiver1.run()     # 后台线程运行
        receiver2.run()     # 后台线程运行
        receiver3.run()     # 后台线程运行
        
        sender.accept_friend_group()
        receiver1.accept_friend_group()
        receiver2.accept_friend_group()
        receiver3.accept_friend_group()
        
        for _id in (receiver1_id, receiver2_id, receiver3_id):
            sender.add_friend(_id)
        
        create_group_res = sender.create_group(','.join((receiver1_id, receiver2_id, receiver3_id)))
        assert 'code' in create_group_res and create_group_res['code'] == '0' and 'communicationId' in create_group_res['data']
        
        self.communication_id = create_group_res['data']['communicationId']
        
        my_log('TestGroupSensitive.setup_class', '', create_group_res)
        self.sender = sender
        self.receiver1 = receiver1
        self.receiver2 = receiver2
        self.receiver3 = receiver3
        
        self.sender_id = sender_id
        self.receiver1_id = receiver1_id
        self.receiver2_id = receiver2_id
        self.receiver3_id = receiver3_id
        
        sleep(2)
        self.sender.clean_msg()
        self.receiver1.clean_msg()
        self.receiver2.clean_msg()
        self.receiver3.clean_msg()
        
        group_user_list_res = sender.get_group_user_list(self.communication_id)
        my_log('TestGroupSensitive.setup_class', '', group_user_list_res)
        assert group_user_list_res['code'] == '0' and 'data' in group_user_list_res
        # group_user_list = group_user_list_res['data']
        group_user_ids = [i['userId'] for i in group_user_list_res['data']]
        assert self.sender_id in group_user_ids
        assert self.receiver1_id in group_user_ids
        assert self.receiver2_id in group_user_ids
        assert self.receiver3_id in group_user_ids
        
    def teardown_class(self):
        self.sender.logout()        # 关闭socket，结束后台线程
        self.receiver1.logout()     # 关闭socket，结束后台线程
        self.receiver2.logout()     # 关闭socket，结束后台线程
        self.receiver3.logout()     # 关闭socket，结束后台线程
    
    def teardown_method(self):
        self.sender.clean_msg()
        self.receiver1.clean_msg()
        self.receiver2.clean_msg()
        self.receiver3.clean_msg()

    @allure.story('群聊敏感词测试场景')
    @allure.title('test_send_group_sensitive')
    # @pytest.mark.parametrize("msg", ['代购', '代購', 'SM', 'sm', '3P', '买卖64狗', 'HJT', 'HJt', 'HjT', 'Hjt', 'hJT', 'hJt', 'hjT', 'hjt', 'TNT炸弹的制作', 'boutique-world.com', 'GaY片', 'GAy片', 'Gay片', 'GAY片', 'gaY片', 'gAy片', 'gay片', 'gAY片', '專业代理', '專業代理', '专业代理', '专業代理', '々﹟#﹩$﹠&﹪%*﹡﹢﹦本店', '￣¯―﹨ˆ˜﹍﹎+=<＿_-\ˇ~﹉﹊（本店', '中国复兴党ˆˇ﹕︰﹔﹖﹑•¨….¸;！', '中国复兴党•¨….¸;！´？！', '兼（）〈〉‹›﹛﹜『』〖〗［］《》〔〕{}「」【】职', '兼?‘’“”〝〞ˆˇ﹕︰﹔﹖职'])
    # @pytest.mark.parametrize("msg", ['专业代理', '專業代理', 'SM', 'sm', '3P', '买卖64狗', 'GFW', 'GFw', 'GfW', 'Gfw', 'gFW', 'gFw', 'gfW', 'gfw', 'tnt炸药配方', 'www2.92ri.com', 'GaY片', 'GAy片', 'Gay片', 'GAY片', 'gaY片', 'gAy片', 'gay片', 'gAY片', '專业代理', '專業代理', '专业代理', '专業代理', '々﹟#﹩$﹠&﹪%*﹡﹢﹦全套', '￣¯―﹨ˆ˜﹍﹎+=<＿_-\ˇ~﹉﹊（sm', '信用卡提现ˆˇ﹕︰﹔﹖﹑•¨….¸;！', 'youxing•¨….¸;！´？！', '操（）〈〉‹›﹛﹜『』〖〗［］《》〔〕{}「」【】逼', 'bao?‘’“”〝〞ˆˇ﹕︰﹔﹖luan'])
    @pytest.mark.parametrize("msg", ['专业代理', '專業代理', 'SM', 'sm', '3P', '买卖64狗', 'GFW', 'GFw', 'GfW', 'Gfw', 'gFW', 'gFw', 'gfW', 'gfw', 'tnt炸药配方', 'www2.92ri.com', 'GaY片', 'GAy片', 'Gay片', 'GAY片', 'gaY片', 'gAy片', 'gay片', 'gAY片', '專业代理', '專業代理', '专业代理', '专業代理', '々﹟#﹩$﹠&﹪%*﹡﹢﹦全套', r'￣¯―﹨ˆ˜﹍﹎+=<＿_-\ˇ~﹉﹊（sm', '信用卡提现ˆˇ﹕︰﹔﹖﹑•¨….¸;！', 'youxing•¨….¸;！´？！', '操（）〈〉‹›﹛﹜『』〖〗［］《》〔〕{}「」【】逼', '流血?‘’“”〝〞ˆˇ﹕︰﹔﹖冲突'])
    def test_send_group_sensitive(self, msg):
        src_msg = self.sender.send_text_msg(self.communication_id, 2, msg)    # 返回发送方发送的原始消息
        my_log('test_send_group_sensitive', src_msg, '')
        reply_msg = self.sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        my_log('test_send_group_sensitive', '', reply_msg)
        assert 'resp' in reply_msg and 'ret' in reply_msg['resp'] and reply_msg['resp']['ret'] == 1509 and reply_msg['resp']['errorCode'] == '您发送的文本消息中可能包含敏感词汇，请重新发送', '发送敏感词服务端无提示!'
    
    @allure.story('群聊敏感词白名单测试场景')
    @allure.title('test_send_group_sensitive_normal')
    @pytest.mark.parametrize("msg", ['EARLY', 'small'])
    def test_send_group_sensitive_normal(self, msg):
        src_msg = self.sender.send_text_msg(self.communication_id, 2, msg)    # 返回发送方发送的原始消息
        my_log('test_send_group_sensitive_normal', src_msg, '')
        reply_msg = self.sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        my_log('test_send_group_sensitive_normal', '', reply_msg)
        assert 'resp' in reply_msg and reply_msg['resp'] == {}
        assert 'message_id' in reply_msg
        msg_id = reply_msg['message_id']
        for receiver in (self.receiver1, self.receiver2, self.receiver3):
            dst_msg = receiver.find_communication_msg_by_id(self.communication_id, msg_id)   # 从receiver的communication_msg中找到发送方发送的消息
            my_log('test_send_group_sensitive_normal', '', dst_msg)
            assert dst_msg is not None
            assert dst_msg['content'] == msg
            assert 'msg_file' not in dst_msg or dst_msg['msg_file'] == {}
            assert dst_msg['from_user_id'] == self.sender_id
            # assert dst_msg['to_user_id'] == self.receiver_id
            assert dst_msg['communication_id'] == self.communication_id
            assert dst_msg['tag'] == src_msg['tag']
            assert dst_msg['communication_type'] == src_msg['communication_type']
            assert dst_msg['message_type'] == src_msg['message_type']
            assert dst_msg['message_main_type'] == src_msg['message_main_type']
            assert dst_msg['other'] == src_msg['other']


@allure.feature('聊天室敏感词测试')
class TestChatRoomSensitive:

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
    
        self.chat_room_owner = choice(self.user_id_list)
        im_user = self.users[self.chat_room_owner]
        self.sender = im_user
        res = im_user.create_chat_room()
        self.chat_room_id = res['data']['communicationId']
        for user_id in self.users:
            self.users[user_id].enter_chat_room(self.chat_room_id)  # 进入聊天室
        sleep(1)
        for user_id in self.users:
            self.users[user_id].clean_msg()  # 进入聊天室
            
    def teardown_class(self):
        for user_id in self.users:
            self.users[user_id].exit_chat_room(self.chat_room_id)  # 离开聊天室
        self.users[self.chat_room_owner].remove_chat_room(self.chat_room_id)    # 销毁聊天室
        for user_id in self.users:
            self.users[user_id].logout()

    @allure.story('聊天室敏感词测试场景')
    @allure.title('test_send_chat_room_sensitive_msg')
    # @pytest.mark.parametrize("msg", ['代购', '代購', 'SM', 'sm', '3P', '买卖64狗', 'HJT', 'HJt', 'HjT', 'Hjt', 'hJT', 'hJt', 'hjT', 'hjt', 'TNT炸弹的制作', 'boutique-world.com', 'GaY片', 'GAy片', 'Gay片', 'GAY片', 'gaY片', 'gAy片', 'gay片', 'gAY片', '專业代理', '專業代理', '专业代理', '专業代理', '々﹟#﹩$﹠&﹪%*﹡﹢﹦本店', '￣¯―﹨ˆ˜﹍﹎+=<＿_-\ˇ~﹉﹊（本店', '中国复兴党ˆˇ﹕︰﹔﹖﹑•¨….¸;！', '中国复兴党•¨….¸;！´？！', '兼（）〈〉‹›﹛﹜『』〖〗［］《》〔〕{}「」【】职', '兼?‘’“”〝〞ˆˇ﹕︰﹔﹖职'])
    @pytest.mark.parametrize("msg", ['专业代理', '專業代理', 'SM', 'sm', '3P', '买卖64狗', 'GFW', 'GFw', 'GfW', 'Gfw', 'gFW', 'gFw', 'gfW', 'gfw', 'tnt炸药配方', 'www2.92ri.com', 'GaY片', 'GAy片', 'Gay片', 'GAY片', 'gaY片', 'gAy片', 'gay片', 'gAY片', '專业代理', '專業代理', '专业代理', '专業代理', '々﹟#﹩$﹠&﹪%*﹡﹢﹦全套', r'￣¯―﹨ˆ˜﹍﹎+=<＿_-\ˇ~﹉﹊（sm', '信用卡提现ˆˇ﹕︰﹔﹖﹑•¨….¸;！', 'youxing•¨….¸;！´？！', '操（）〈〉‹›﹛﹜『』〖〗［］《》〔〕{}「」【】逼', '流血?‘’“”〝〞ˆˇ﹕︰﹔﹖冲突'])
    def test_send_chat_room_sensitive_msg(self, msg):
        src_msg = self.sender.send_text_msg(self.chat_room_id, 3, msg)    # 返回发送方发送的原始消息
        my_log('test_send_chat_room_sensitive_msg', src_msg, '')
        reply_msg = self.sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        my_log('test_send_chat_room_sensitive_msg', '', reply_msg)
        assert 'resp' in reply_msg and 'ret' in reply_msg['resp'] and reply_msg['resp']['ret'] == 1509 and reply_msg['resp']['errorCode'] == '您发送的文本消息中可能包含敏感词汇，请重新发送', '发送敏感词服务端无提示!'
    
    @allure.story('聊天室敏感词白名单测试场景')
    @allure.title('test_send_group_sensitive_msg_normal')
    @pytest.mark.parametrize("msg", ['EARLY', 'small'])
    def test_send_group_sensitive_msg_normal(self, msg):
        src_msg = self.sender.send_text_msg(self.chat_room_id, 3, msg)    # 返回发送方发送的原始消息
        my_log('test_send_group_sensitive_msg_normal', src_msg, '')
        reply_msg = self.sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        my_log('test_send_group_sensitive_msg_normal', '', reply_msg)
        assert 'resp' in reply_msg and reply_msg['resp'] == {}
        assert 'message_id' in reply_msg
        msg_id = reply_msg['message_id']
        for user_id in self.users:
            if user_id == self.chat_room_owner:
                continue
            receiver = self.users[user_id]
            dst_msg = receiver.find_communication_msg_by_id(self.chat_room_id, msg_id)   # 从receiver的communication_msg中找到发送方发送的消息
            my_log('test_send_group_sensitive_msg_normal', '', dst_msg)
            assert dst_msg is not None
            assert dst_msg['content'] == msg
            assert 'msg_file' not in dst_msg or dst_msg['msg_file'] == {}
            assert dst_msg['from_user_id'] == self.chat_room_owner
            # assert dst_msg['to_user_id'] == self.receiver_id
            assert dst_msg['communication_id'] == self.chat_room_id
            assert dst_msg['tag'] == src_msg['tag']
            assert dst_msg['communication_type'] == src_msg['communication_type']
            assert dst_msg['message_type'] == src_msg['message_type']
            assert dst_msg['message_main_type'] == src_msg['message_main_type']
            assert dst_msg['other'] == src_msg['other']
