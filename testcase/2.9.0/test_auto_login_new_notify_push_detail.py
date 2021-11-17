from random import choice

import time

import pytest
import allure

from lib.im_socket_lib.sync_im_user import IMUser
from common.my_log import my_log


from config.conf import USER_INFO


class TestAutoLoginNewNotifyPushDetail:

    def setup_class(self):
        self.all_user_info = USER_INFO[:]

    def setup_method(self):
        self.user_info = choice(self.all_user_info)

    @allure.title('设置用户各种模式')
    @pytest.mark.parametrize('push_status, auto_login_status, ring_status, shake_status',
                             [[i, j, k, _l] for i in (True, False) for j in (True, False) for k in (True, False) for _l in (True, False)])
    def test_001(self, push_status, auto_login_status, ring_status, shake_status):
        """
        设置用户各种模式
        :param push_status:
        :param auto_login_status:
        :param ring_status:
        :param shake_status:
        :return:
        """
        test_user = IMUser(self.user_info)
        test_user.run()

        set_push_status_res = test_user.set_user_show_push_detail(push_status)
        my_log('test_001[设置推送状态]', push_status, set_push_status_res)
        assert set_push_status_res['code'] == '0'

        set_auto_login_status_res = test_user.set_user_auto_login(auto_login_status)
        my_log('test_001[设置自动登录状态]', auto_login_status, set_auto_login_status_res)
        assert set_auto_login_status_res['code'] == '0'

        set_ring_status_res = test_user.set_user_new_notify(ring_status, 0)
        my_log('test_001[设置响铃]', ring_status, set_ring_status_res)
        assert set_ring_status_res['code'] == '0'

        set_shake_status_res = test_user.set_user_new_notify(shake_status, 1)
        my_log('test_001[设置震动]', shake_status, set_shake_status_res)
        assert set_shake_status_res['code'] == '0'

        test_user.logout()
        time.sleep(10)

        test_user = IMUser(self.user_info)
        login_res = test_user.login()
        my_log('test_001[用户登录结果]', '', login_res)
        assert login_res['code'] == '0'

        user_setting = login_res['data']['im_module']['user_setting']

        assert user_setting['showPushDetail'] is push_status
        assert user_setting['autoLogin'] is auto_login_status
        assert user_setting['ring_down'] is ring_status
        assert user_setting['vibrate'] is shake_status
