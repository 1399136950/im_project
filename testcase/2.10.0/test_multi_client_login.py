import time

import allure

from lib.im_socket_lib.sync_im_user import IMUser
from config.conf import USER_INFO


@allure.feature('多端登陆测试用例')
class TestMultiClientLogin:

    def test_001(self):
        user_ios = IMUser(USER_INFO[0], 'ios')
        user_pc = IMUser(USER_INFO[1], 'pc')
        user_ios.DEBUG = True
        user_pc.DEBUG = True
        user_ios.run()
        user_pc.run()

        time.sleep(10)

        user_ios.logout()
        user_pc.logout()
