import time

import allure

from lib.paas_lib.paas_user import PaasUser
from lib.im_socket_lib.sync_im_user import IMUser
from common.my_log import my_log

from config.conf import USER_INFO, PAAS_USER, APP_NAME


@allure.feature('paas平台敏感词相关功能测试')
class TestSensitiveSwitch:

    def setup_class(self):
        self.paas_user = PaasUser(*PAAS_USER)
        self.im_user = IMUser(USER_INFO[0])
        self.friend = IMUser(USER_INFO[1])
        self.im_user.run()
        self.friend.run()
        self.friend.accept_friend_group()
        self.im_user.add_friend(self.friend.user_id)
        friend_info_res = self.im_user.get_user_detail(self.friend.user_id)
        self.communication_id = friend_info_res['data']['conversationId']
        app_info = self.paas_user.get_app_info_by_name(APP_NAME)
        self.app_id = app_info['id']
        self.before_app_cfg_res = self.paas_user.get_app_ext_info(self.app_id)
        self.before_user_detail = self.im_user.get_user_detail()
        my_log('before_app_cfg_res', self.before_app_cfg_res)
        my_log('before_user_detail', self.before_user_detail)
        self.word = None
        self.wait_time = 150    # 更改敏感词相关设置后的生效间隔时间

    @allure.story('关闭敏感词功能，然后发送敏感词')
    def test_001(self):
        set_app_service_ext_res = self.paas_user.set_app_service_ext(self.app_id, False, 17)
        my_log('set_app_func_res', set_app_service_ext_res)
        assert set_app_service_ext_res['code'] == '0'

        time.sleep(self.wait_time)
        sensitive_word = '兼职'

        src_msg = self.im_user.send_text_msg(self.communication_id, 1, sensitive_word, self.friend.user_id)
        reply_msg = self.im_user.find_reply_msg_by_tag(src_msg['tag'])
        message_id = reply_msg['message_id']
        my_log('reply_msg', reply_msg)

        message = self.friend.find_communication_msg_by_id(self.communication_id, message_id)
        my_log('message', message)
        assert message is not None

        set_name_res = self.im_user.set_user_baseinfo(nickname=sensitive_word)
        my_log('set_name_res', set_name_res)
        assert set_name_res['code'] == '0'

        set_app_service_ext_res = self.paas_user.set_app_service_ext(self.app_id, True, 17)  # 再开启敏感词
        time.sleep(self.wait_time)
        my_log('set_app_func_res', set_app_service_ext_res)
        assert set_app_service_ext_res['code'] == '0'

        src_msg = self.im_user.send_text_msg(self.communication_id, 1, sensitive_word, self.friend.user_id)
        reply_msg = self.im_user.find_reply_msg_by_tag(src_msg['tag'])
        message_id = reply_msg['message_id']
        my_log('reply_msg', reply_msg)

        message = self.friend.find_communication_msg_by_id(self.communication_id, message_id)
        my_log('message', message)
        assert message is None

        set_name_res = self.im_user.set_user_baseinfo(nickname=sensitive_word)
        my_log('set_name_res', set_name_res)
        assert set_name_res['code'] == '1' and set_name_res['error']['message'] == '用户昵称包含敏感词汇，请重新设置'

    @allure.story('开启敏感词功能，并添加自定义黑名单敏感词')
    def test_002(self):
        set_app_service_ext_res = self.paas_user.set_app_service_ext(self.app_id, True, 17)
        my_log('set_app_func_res', set_app_service_ext_res)
        assert set_app_service_ext_res['code'] == '0'

        self.word = '故事'
        add_sensitive_word_res = self.paas_user.add_sensitive_word(self.app_id, 1, self.word)
        my_log('add_sensitive_word_res', add_sensitive_word_res)
        assert add_sensitive_word_res['code'] == '0'

        time.sleep(self.wait_time)

        src_msg = self.im_user.send_text_msg(self.communication_id, 1, self.word, self.friend.user_id)
        reply_msg = self.im_user.find_reply_msg_by_tag(src_msg['tag'])
        my_log('reply_msg', reply_msg)
        assert 'resp' in reply_msg and 'ret' in reply_msg['resp'] and reply_msg['resp']['ret'] == 1509 and reply_msg['resp']['errorCode'] == '您发送的文本消息中可能包含敏感词汇，请重新发送', '发送敏感词服务端无提示!'

        set_name_res = self.im_user.set_user_baseinfo(nickname=self.word)
        my_log('set_name_res', set_name_res)
        assert set_name_res['code'] == '1' and set_name_res['error']['message'] == '用户昵称包含敏感词汇，请重新设置'

        del_sen_res = self.paas_user.del_sensitive_word_by_word(self.app_id, self.word)  # 将敏感词删除，再重复上面两个操作
        time.sleep(self.wait_time)
        my_log('del_sen_res', del_sen_res)
        assert del_sen_res['code'] == '0'

        set_name_res = self.im_user.set_user_baseinfo(nickname=self.word)
        my_log('set_name_res', set_name_res)
        assert set_name_res['code'] == '0'

        src_msg = self.im_user.send_text_msg(self.communication_id, 1, self.word, self.friend.user_id)
        reply_msg = self.im_user.find_reply_msg_by_tag(src_msg['tag'])
        message_id = reply_msg['message_id']
        my_log('reply_msg', reply_msg)

        message = self.friend.find_communication_msg_by_id(self.communication_id, message_id)
        my_log('message', message)
        assert message is not None

    @allure.story('开启敏感词功能，并添加自定义白名单敏感词')
    def test_003(self):
        set_app_service_ext_res = self.paas_user.set_app_service_ext(self.app_id, True, 17)
        my_log('set_app_func_res', set_app_service_ext_res)
        assert set_app_service_ext_res['code'] == '0'

        self.word = '兼职'
        add_sensitive_word_res = self.paas_user.add_sensitive_word(self.app_id, 2, self.word)
        my_log('add_sensitive_word_res', add_sensitive_word_res)
        assert add_sensitive_word_res['code'] == '0'

        time.sleep(self.wait_time)

        src_msg = self.im_user.send_text_msg(self.communication_id, 1, self.word, self.friend.user_id)
        reply_msg = self.im_user.find_reply_msg_by_tag(src_msg['tag'])
        message_id = reply_msg['message_id']
        my_log('reply_msg', reply_msg)

        msg = self.friend.find_communication_msg_by_id(self.communication_id, message_id)
        assert msg is not None

        set_name_res = self.im_user.set_user_baseinfo(nickname=self.word)
        my_log('set_name_res', set_name_res)
        assert set_name_res['code'] == '0'

        del_sen_res = self.paas_user.del_sensitive_word_by_word(self.app_id, self.word)  # 将敏感词删除，再重复上面两个操作
        my_log('del_sen_res', del_sen_res)
        assert del_sen_res['code'] == '0'

        time.sleep(self.wait_time)

        set_name_res = self.im_user.set_user_baseinfo(nickname=self.word)
        my_log('set_name_res', set_name_res)
        assert set_name_res['code'] == '1' and set_name_res['error']['message'] == '用户昵称包含敏感词汇，请重新设置'

        src_msg = self.im_user.send_text_msg(self.communication_id, 1, self.word, self.friend.user_id)
        reply_msg = self.im_user.find_reply_msg_by_tag(src_msg['tag'])
        message_id = reply_msg['message_id']
        assert reply_msg['resp'] == {'ret': 1509, 'errorCode': '您发送的文本消息中可能包含敏感词汇，请重新发送'}
        my_log('reply_msg', reply_msg)

        msg = self.friend.find_communication_msg_by_id(self.communication_id, message_id)
        assert msg is None

    def teardown_class(self):
        self.im_user.set_user_baseinfo(nickname=self.before_user_detail['data']['nickname'])
        self.im_user.logout()
        self.friend.logout()
        self.paas_user.set_app_service_ext(self.app_id, self.before_app_cfg_res['data']['sensitiveWordFilterEnabled'], 17)

    def teardown_method(self):
        self.im_user.clean_msg()
        self.friend.clean_msg()
        if self.word is not None:
            self.paas_user.del_sensitive_word_by_word(self.app_id, self.word)
