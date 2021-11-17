# -*- coding:utf-8 -*-
# @author  : ywt
# @file   : test_user_setting_dontdisturb.py
# @ide    : PyCharm
# @time    : 2021/4/1 13:34
import allure

from lib.im_api_lib.user import user_setting_dont_disturb_detail
from lib.im_api_lib.user import user_im_setting
from common.my_log import my_log


@allure.feature("用户免打扰接口")
class TestUserSettingDontDisturb:
    @allure.story("用户免打扰状态从false设置成true场景")
    @allure.title("test_user_setting_dont_disturb_false_to_true")
    def test_user_setting_dont_disturb_false_to_true(self, start_demo):
        """
        1:user1设置默认的用户免打扰状态为False，断言user1当前的用户免打扰状态为False
        2:user1用户免打扰状态False设置成True，断言设置成功code=0，
          断言设置后查询用户设置信息的dontDisturb = True
        :param start_demo:
        :return:
        """
        token = start_demo
        user_setting_dont_disturb_detail(token, False)
        res = user_im_setting(token)['data']['user_setting']['dontDisturb']
        assert res is False
        ret = user_setting_dont_disturb_detail(token, True)
        assert ret['code'] == "0"
        my_log('test_user_setting_dont_disturb_false_to_true',
               {"dontDisturb": True}, ret)
        ree = user_im_setting(token)['data']['user_setting']["dontDisturb"]
        assert ree is True

    @allure.story("用户免打扰状态从false设置成false场景")
    @allure.title("test_user_setting_dont_disturb_false_to_false")
    def test_user_setting_dont_disturb_false_to_false(self, start_demo):
        """
        1:user1设置默认的用户免打扰状态为False，断言user1当前的用户免打扰状态为False
        2:user1用户免打扰状态为False设置成False，断言设置成功code=0，
          断言设置后查询用户设置信息的dontDisturb = False
        :param start_demo:
        :return:
        """
        token = start_demo
        user_setting_dont_disturb_detail(token, False)
        res = user_im_setting(token)['data']['user_setting']["dontDisturb"]
        assert res is False
        ret = user_setting_dont_disturb_detail(token, False)
        assert ret['code'] == "0"
        my_log('test_user_setting_dont_disturb_false_to_false',
               {"dontDisturb": False}, ret)
        ret = user_im_setting(token)['data']['user_setting']["dontDisturb"]
        assert ret is False

    @allure.story("用户免打扰状态从true设置成false场景")
    @allure.title("test_user_setting_dont_disturb_true_to_false")
    def test_user_setting_dont_disturb_true_to_false(self, start_demo):
        """
        1:user1设置默认的用户免打扰状态为True，断言user1当前的用户免打扰状态为True
        2:user1用户免打扰状态从True设置成False，断言设置成功code=0，
          断言设置后查询用户设置信息的dontDisturb = False
        :param start_demo:
        :return:
        """
        token = start_demo
        user_setting_dont_disturb_detail(token, True)
        res = user_im_setting(token)['data']['user_setting']["dontDisturb"]
        assert res is True
        ret = user_setting_dont_disturb_detail(token, False)
        assert ret['code'] == "0"
        my_log('est_user_setting_dont_disturb_true_to_false',
               {"dontDisturb": False}, ret)
        ret = user_im_setting(token)['data']['user_setting']["dontDisturb"]
        assert ret is False

    @allure.story("用户免打扰状态状态从true设置成true场景")
    @allure.title("test_user_setting_dont_disturb_true_to_true")
    def test_user_setting_dont_disturb_true_to_true(self, start_demo):
        """
        1:user1设置默认的用户免打扰状态为True，断言user1当前的用户免打扰状态为True
        2:user1自动用户免打扰状态从True设置成True，断言设置成功code=0，
          断言设置后查询用户设置信息的dontDisturb = True
        :param start_demo:
        :return:
        """
        token = start_demo
        user_setting_dont_disturb_detail(token, True)
        res = user_im_setting(token)['data']['user_setting']["dontDisturb"]
        assert res is True
        ret = user_setting_dont_disturb_detail(token, True)
        assert ret['code'] == "0"
        my_log('test_user_setting_dont_disturb_true_to_true',
               {"dontDisturb": True}, ret)
        ret = user_im_setting(token)['data']['user_setting']["dontDisturb"]
        assert ret is True

