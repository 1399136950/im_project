from time import sleep, time

import pytest
import allure

from lib.im_api_lib.user import user_friend_list
from lib.im_socket_lib.sync_im_user import IMUser
from lib.paas_lib.paas_user import PaasUser
from common.my_log import my_log
from lib.mysql.mydb import set_resource_package_amount_max
from config.conf import ENV_MODE, USER_INFO, PAAS_USER


MINGANCI_RES_PACK = 3486
TEXT_RES_PACK = 3478
IMAGE_RES_PACK = 3480
FILE_RES_PACK = 3482


# ORG_ID = 25
INT_APP_ID = 56


MSG_TYPE_TO_RES_PACK_ID = {
    1: TEXT_RES_PACK,
    2: TEXT_RES_PACK,
    3: FILE_RES_PACK,
    4: IMAGE_RES_PACK,
    5: IMAGE_RES_PACK,
    6: IMAGE_RES_PACK,
    7: TEXT_RES_PACK
}


@allure.feature("发送单聊消息")
@pytest.mark.skipif(ENV_MODE == 'pro', reason='正式环境跳过测试')
class TestSendSingleMsg:
    
    def setup_class(self):
        self.money = 0
        sender = IMUser(USER_INFO[0])   # 初始化发送方
        receiver = IMUser(USER_INFO[1])   # 初始化接收方

        self.paas_user = PaasUser(*PAAS_USER)

        sender.DEBUG = True
        
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
        # self.money = self.get_money()
        # sleep(70)
    
    def get_money(self):
        return self.paas_user.get_account_balance()['data']['balance']
        
    @allure.story("无敏感词，和文本资源包，余额0，发送带敏感词的消息")
    def test_001(self):
        set_resource_package_amount_max(MINGANCI_RES_PACK)
        set_resource_package_amount_max(TEXT_RES_PACK)
        
        self.money = self.get_money()
        if self.money == 0:
            sleep(70)
        
        while self.money > 0 or self.money < 0:
            if self.money > 0:
                self.paas_user.custom_money(self.money)
            else:
                self.paas_user.deposit_money(self.money * -1)
            sleep(70)
            self.money = self.get_money()
        
        assert self.money == 0

        text_content = 'ly'
        self.sender.send_text_msg(self.communication_id, 1, text_content, self.receiver_id)    # 返回发送方发送的原始消息
        sleep(3)
        src_msg = self.sender.send_text_msg(self.communication_id, 1, text_content, self.receiver_id)    # 返回发送方发送的原始消息
        my_log('test_001', src_msg, '')
        reply_msg = self.sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        assert reply_msg is not None
        my_log('test_001', '', reply_msg)
        assert 'resp' in reply_msg and reply_msg['resp']['ret'] == 1509 and reply_msg['resp']['errorCode'] == '您发送的文本消息中可能包含敏感词汇，请重新发送'
        
    @allure.story("有敏感词和文本资源包，余额0，发送正常的消息")
    def test_002(self):
        res1 = self.paas_user.activate_resource_package(INT_APP_ID, TEXT_RES_PACK)
        print(res1)
        res2 = self.paas_user.activate_resource_package(INT_APP_ID, MINGANCI_RES_PACK)
        print(res2)
        
        self.money = self.get_money()
        if self.money == 0:
            sleep(70)
        
        while self.money > 0 or self.money < 0:
            if self.money > 0:
                self.paas_user.custom_money(self.money)
            else:
                self.paas_user.deposit_money(self.money * -1)
            sleep(70)
            self.money = self.get_money()
        
        assert self.money == 0
        
        text_content = 'test'
        src_msg = self.sender.send_text_msg(self.communication_id, 1, text_content, self.receiver_id)    # 返回发送方发送的原始消息
        # sleep(3)
        my_log('test_002', src_msg, '')
        reply_msg = self.sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        assert reply_msg is not None
        my_log('test_002', '', reply_msg)
        assert 'resp' not in reply_msg or reply_msg['resp'] == {}
        
    @allure.story("无敏感词，有文本资源包，余额小于0，发送正常的消息")
    def test_003(self):
        res1 = self.paas_user.activate_resource_package(INT_APP_ID, TEXT_RES_PACK)
        print(res1)
        set_resource_package_amount_max(MINGANCI_RES_PACK)
        
        self.money = self.get_money()
        
        if self.money < 0:
            sleep(70)
        
        while self.money >= 0:
            if self.money == 0:
                self.paas_user.custom_money(10)
            else:
                self.paas_user.custom_money(self.money+10)
            sleep(70)
            self.money = self.get_money()
        
        assert self.money < 0
        
        text_content = 'test'
        src_msg = self.sender.send_text_msg(self.communication_id, 1, text_content, self.receiver_id)    # 返回发送方发送的原始消息
        my_log('test_003', src_msg, '')
        reply_msg = self.sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        assert reply_msg is not None
        my_log('test_003', '', reply_msg)
        assert 'resp' not in reply_msg or reply_msg['resp'] == {}

    @allure.story("有敏感词，无文本资源包，余额小于0，发送敏感词消息")
    def test_004(self):
        res1 = self.paas_user.activate_resource_package(INT_APP_ID, MINGANCI_RES_PACK)
        print(res1)
        set_resource_package_amount_max(TEXT_RES_PACK)
        
        self.money = self.get_money()
        
        if self.money < 0:
            sleep(70)
        
        while self.money >= 0:
            if self.money == 0:
                self.paas_user.custom_money(10)
            else:
                self.paas_user.custom_money(self.money+10)
            sleep(70)
            self.money = self.get_money()
        
        assert self.money < 0
        
        text_content = 'test'
        self.sender.send_text_msg(self.communication_id, 1, text_content, self.receiver_id)    # 返回发送方发送的原始消息
        sleep(3)
        text_content = 'ly'
        src_msg = self.sender.send_text_msg(self.communication_id, 1, text_content, self.receiver_id)    # 返回发送方发送的原始消息
        
        my_log('test_004', src_msg, '')
        reply_msg = self.sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        assert reply_msg is not None
        my_log('test_004', '', reply_msg)
        assert 'resp' in reply_msg and 'ret' in reply_msg['resp'] and reply_msg['resp']['ret'] == 1210 and reply_msg['resp']['errorCode'] == '用户无权限做该操作, 请联系管理员处理'
        
    @allure.story("无敏感词，无文本资源包，余额大于0，发送正常消息")
    def test_005(self):
        set_resource_package_amount_max(TEXT_RES_PACK)
        set_resource_package_amount_max(MINGANCI_RES_PACK)
        
        if self.money > 0:
            sleep(70)
        
        while self.money <= 0:
            if self.money == 0:
                # add_money(ORG_ID, 10)
                self.paas_user.deposit_money(10)
            else:
                self.paas_user.deposit_money(self.money * -1 + 10)
                # add_money(ORG_ID, )
            sleep(70)
            self.money = self.get_money()
        
        assert self.money > 0
        
        text_content = 'test'
        self.sender.send_text_msg(self.communication_id, 1, text_content, self.receiver_id)    # 返回发送方发送的原始消息
        sleep(3)
        src_msg = self.sender.send_text_msg(self.communication_id, 1, text_content, self.receiver_id)    # 返回发送方发送的原始消息
        my_log('test_005', src_msg, '')
        reply_msg = self.sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        assert reply_msg is not None
        my_log('test_005', '', reply_msg)
        assert 'resp' not in reply_msg or reply_msg['resp'] == {}
        
    @allure.story("有敏感词，有文本资源包，余额大于0，发送敏感词消息")
    def test_006(self):
        res1 = self.paas_user.activate_resource_package(INT_APP_ID, MINGANCI_RES_PACK)

        print(res1)
        res2 = self.paas_user.activate_resource_package(INT_APP_ID, TEXT_RES_PACK)
        print(res2)
        
        self.money = self.get_money()
        
        if self.money > 0:
            sleep(70)

        while self.money <= 0:
            if self.money == 0:
                # add_money(ORG_ID, 10)
                self.paas_user.deposit_money(10)
            else:
                # add_money(ORG_ID, self.money * -1 + 10)
                self.paas_user.deposit_money(self.money * -1 + 10)
            sleep(70)
            self.money = self.get_money()
        
        assert self.money > 0
        
        text_content = 'ly'
        src_msg = self.sender.send_text_msg(self.communication_id, 1, text_content, self.receiver_id)    # 返回发送方发送的原始消息
        my_log('test_006', src_msg, '')
        reply_msg = self.sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        assert reply_msg is not None
        my_log('test_006', '', reply_msg)
        assert 'resp' in reply_msg and reply_msg['resp']['ret'] == 1509 and reply_msg['resp']['errorCode'] == '您发送的文本消息中可能包含敏感词汇，请重新发送'
        
    @allure.story("资源包和余额以及消息类型组合排列场景")
    @pytest.mark.parametrize("msg_type, money, resource_package_status", [
                                (1, 0, 0),
                                (2, 0, 0),
                                (3, 0, 0),
                                (4, 0, 0),
                                (5, 0, 0),
                                (6, 0, 0),
                                (7, 0, 0),
                                (1, 0, 1),
                                (2, 0, 1),
                                (3, 0, 1),
                                (4, 0, 1),
                                (5, 0, 1),
                                (6, 0, 1),
                                (7, 0, 1),
                                (1, 100, 0),
                                (2, 100, 0),
                                (3, 100, 0),
                                (4, 100, 0),
                                (5, 100, 0),
                                (6, 100, 0),
                                (7, 100, 0),
                                (1, 100, 1),
                                (2, 100, 1),
                                (3, 100, 1),
                                (4, 100, 1),
                                (5, 100, 1),
                                (6, 100, 1),
                                (7, 100, 1),
                                (1, -100, 0),
                                (2, -100, 0),
                                (3, -100, 0),
                                (4, -100, 0),
                                (5, -100, 0),
                                (6, -100, 0),
                                (7, -100, 0),
                                (1, -100, 1),
                                (2, -100, 1),
                                (3, -100, 1),
                                (4, -100, 1),
                                (5, -100, 1),
                                (6, -100, 1),
                                (7, -100, 1)
                            ])
    def test_money_and_resource_package(self, msg_type, money, resource_package_status):
        """
        @msg_type: 消息类型
        @money: 账户余额
        @resource_package_status: 资源包状态，1有资源包，0无资源包
        """
        res_pack_id = MSG_TYPE_TO_RES_PACK_ID[msg_type]
        if resource_package_status:
            self.paas_user.activate_resource_package(INT_APP_ID, res_pack_id)
        else:
            set_resource_package_amount_max(res_pack_id)
            
        self.money = self.get_money()
        
        if self.money == money:
            sleep(70)
        
        while self.money != money:
            if money > self.money:
                # add_money(ORG_ID, money-self.money)
                self.paas_user.deposit_money(money-self.money)
            else:
                # custom_money(ORG_ID, self.money-money)
                self.paas_user.custom_money(self.money-money)
            sleep(70)
            self.money = self.get_money()
        
        # my_log('test_money_and_resource_package', {'self.money':self.money, 'money':money}, '')
        assert self.money == money
        
        if msg_type == 1:
            text_content = 'hello world'
            src_msg = self.sender.send_text_msg(self.communication_id, 1, text_content, self.receiver_id)
        elif msg_type == 2:
            src_msg = self.sender.send_emoji_msg(self.communication_id, 1, self.receiver_id)
        elif msg_type == 3:
            src_msg = self.sender.send_file_msg(self.communication_id, 1, self.receiver_id)
        elif msg_type == 4:
            src_msg = self.sender.send_image_msg(self.communication_id, 1, self.receiver_id)
        elif msg_type == 5:
            src_msg = self.sender.send_audio_msg(self.communication_id, 1, self.receiver_id)    # 返回发送方发送的原始消息
        elif msg_type == 6:
            src_msg = self.sender.send_video_msg(self.communication_id, 1, self.receiver_id)
        elif msg_type == 7:
            src_msg = self.sender.send_address_msg(self.communication_id, 1, self.receiver_id)
        else:
            raise Exception('unknow msg type')
        
        my_log('test_money_and_resource_package: src_msg[0]', src_msg, '')
        
        sleep(2)
        self.money = self.get_money()
        while self.money != money:
            if money > self.money:
                # add_money(ORG_ID, money-self.money)
                self.paas_user.deposit_money(money-self.money)
            else:
                # custom_money(ORG_ID, self.money-money)
                self.paas_user.custom_money(self.money-money)
            sleep(70)
            self.money = self.get_money()
        
        my_log('test_money_and_resource_package', {'self.money': self.money, 'money': money}, '')
        assert self.money == money
        
        if msg_type == 1:
            text_content = 'hello world'
            src_msg = self.sender.send_text_msg(self.communication_id, 1, text_content, self.receiver_id)
        elif msg_type == 2:
            src_msg = self.sender.send_emoji_msg(self.communication_id, 1, self.receiver_id)
        elif msg_type == 3:
            src_msg = self.sender.send_file_msg(self.communication_id, 1, self.receiver_id)
        elif msg_type == 4:
            src_msg = self.sender.send_image_msg(self.communication_id, 1, self.receiver_id)
        elif msg_type == 5:
            src_msg = self.sender.send_audio_msg(self.communication_id, 1, self.receiver_id)    # 返回发送方发送的原始消息
        elif msg_type == 6:
            src_msg = self.sender.send_video_msg(self.communication_id, 1, self.receiver_id)
        elif msg_type == 7:
            src_msg = self.sender.send_address_msg(self.communication_id, 1, self.receiver_id)
        else:
            raise Exception('unknow msg type')
        my_log('test_money_and_resource_package: src_msg[1]', src_msg, '')
        # reply_msg = self.sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg    
        my_log('test_money_and_resource_package', {'msg_type': msg_type, 'money': money, 'resource_package_status': resource_package_status}, '')
        reply_msg = self.sender.find_reply_msg_by_tag(src_msg['tag'])    # 从sender的reply_command_send_msg_req中找到服务器返回的reply_msg
        assert reply_msg is not None
        my_log('test_money_and_resource_package', '', reply_msg)
        if money < 0 and resource_package_status == 0:
            assert 'resp' in reply_msg and 'ret' in reply_msg['resp'] and reply_msg['resp']['ret'] == 1210 and reply_msg['resp']['errorCode'] == '用户无权限做该操作, 请联系管理员处理' 
        else:
            assert 'resp' not in reply_msg or reply_msg['resp'] == {} 
    
    @pytest.mark.parametrize("money, resource_package_status, is_minganci", [
                                (-100, 0, 1),
                                (-100, 1, 1),
                                (-100, 1, 0),
                                (-100, 0, 0),
                                (100, 1, 1),
                                (100, 1, 0),
                                (100, 0, 1),
                                (100, 0, 0),
                                (0, 1, 1),
                                (0, 1, 0),
                                (0, 0, 1),
                                (0, 0, 0)
                            ])
    def test_mingan_api(self, money, resource_package_status, is_minganci):
        """
        @money: 账户余额
        @resource_package_status: 资源包状态，1有资源包，0无资源包
        @is_minganci: 是否携带敏感词
        """
        res_pack_id = MINGANCI_RES_PACK
        if resource_package_status:
            self.paas_user.activate_resource_package(INT_APP_ID, res_pack_id)
        else:
            set_resource_package_amount_max(res_pack_id)
            
        self.money = self.get_money()
        
        if self.money == money:
            sleep(70)
        
        while self.money != money:
            if money > self.money:
                # add_money(ORG_ID, money-self.money)
                self.paas_user.deposit_money(money-self.money)
            else:
                # custom_money(ORG_ID, self.money-money)
                self.paas_user.custom_money(self.money-money)
            sleep(70)
            self.money = self.get_money()
        
        my_log('test_mingan_api', {'self.money': self.money, 'money': money}, '')
        assert self.money == money
        
        self.sender.set_user_baseinfo(nickname='ly')
        
        sleep(2)
        
        if is_minganci:
            new_nickname = 'ly'
        else:
            new_nickname = str(int(time()))[0:20]
            
        res = self.sender.set_user_baseinfo(nickname=new_nickname)
        
        my_log('test_mingan_api', '', res)
        
        if is_minganci:
            if money < 0 and not resource_package_status:
                # 提示资源不足
                assert res['code'] == '1'
                assert res['error']['message'] == '用户无权限做该操作, 请联系管理员处理'
            else:
                # 提示敏感词
                assert res['code'] == '1'
                assert res['error']['message'] == '用户昵称包含敏感词汇，请重新设置'
        else:
            # 正常设置
            assert res['code'] == '0'
