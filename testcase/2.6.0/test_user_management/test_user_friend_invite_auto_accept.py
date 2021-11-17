# -*- coding:utf-8 -*-
# @author  : ywt
# @file   : test_user_friend_invite_auto_accept.py
# @ide    : PyCharm
# @time    : 2021/3/31 17:36
import allure

from lib.im_api_lib.user import user_friend_invite_auto_accept
from lib.im_api_lib.user import user_im_setting
from common.my_log import my_log


@allure.feature("设置自动加好友接口")
class TestUserFriendInviteAutoAccept:
    @allure.story("自动添加好友状态从false设置成true场景")
    @allure.title("test_user_friend_invite_auto_accept_false_to_true")
    def test_user_friend_invite_auto_accept_false_to_true(self, start_demo):
        """
        1:user1设置默认的添加好友状态为False，断言user1当前的添加好友状态为False
        2:user1添加好友状态为False设置成True，断言设置成功code=0，
          断言设置后查询用户设置信息的autoAcceptFriendInvitation = True
        :param start_demo:
        :return:
        """
        token = start_demo
        user_friend_invite_auto_accept(token, False)
        res = user_im_setting(token)['data']['user_setting']["autoAcceptFriendInvitation"]
        assert res is False
        ret = user_friend_invite_auto_accept(token, True)
        assert ret['code'] == "0"
        my_log('test_user_friend_invite_auto_accept_false_to_true',
               {"auto": True}, ret)
        ret = user_im_setting(token)['data']['user_setting']["autoAcceptFriendInvitation"]
        assert ret is True

    @allure.story("自动添加好友状态从false设置成false场景")
    @allure.title("test_user_friend_invite_auto_accept_false_to_false")
    def test_user_friend_invite_auto_accept_false_to_false(self, start_demo):
        """
        1:user1设置默认的添加好友状态为False，断言user1当前的添加好友状态为False
        2:user1添加好友状态为False设置成False，断言设置成功code=0，
          断言设置后查询用户设置信息的autoAcceptFriendInvitation = False
        :param start_demo:
        :return:
        """
        token = start_demo
        user_friend_invite_auto_accept(token, False)
        res = user_im_setting(token)['data']['user_setting']["autoAcceptFriendInvitation"]
        assert res is False
        ret = user_friend_invite_auto_accept(token, False)
        assert ret['code'] == "0"
        my_log('test_user_friend_invite_auto_accept_false_to_false',
               {"auto": False}, ret)
        ret = user_im_setting(token)['data']['user_setting']["autoAcceptFriendInvitation"]
        assert ret is False

    @allure.story("自动添加好友状态从true设置成false场景")
    @allure.title("test_user_friend_invite_auto_accept_true_to_false")
    def test_user_friend_invite_auto_accept_true_to_false(self, start_demo):
        """
        1:user1设置默认的添加好友状态为True，断言user1当前的添加好友状态为True
        2:user1自动添加好友状态从True设置成False，断言设置成功code=0，
          断言设置后查询用户设置信息的autoAcceptFriendInvitation = False
        :param start_demo:
        :return:
        """
        token = start_demo
        user_friend_invite_auto_accept(token, True)
        res = user_im_setting(token)['data']['user_setting']["autoAcceptFriendInvitation"]
        assert res is True
        ret = user_friend_invite_auto_accept(token, False)
        assert ret['code'] == "0"
        my_log('test_user_friend_invite_auto_accept_true_to_false',
               {"auto": False}, ret)
        ret = user_im_setting(token)['data']['user_setting']["autoAcceptFriendInvitation"]
        assert ret is False

    @allure.story("自动添加好友状态从true设置成true场景")
    @allure.title("test_user_friend_invite_auto_accept_true_to_true")
    def test_user_friend_invite_auto_accept_true_to_true(self, start_demo):
        """
        1:user1设置默认的添加好友状态为True，断言user1当前的添加好友状态为True
        2:user1自动添加好友状态从True设置成True，断言设置成功code=0，
          断言设置后查询用户设置信息的autoAcceptFriendInvitation = True
        :param start_demo:
        :return:
        """
        token = start_demo
        user_friend_invite_auto_accept(token, True)
        res = user_im_setting(token)['data']['user_setting']["autoAcceptFriendInvitation"]
        assert res is True
        ret = user_friend_invite_auto_accept(token, True)
        assert ret['code'] == "0"
        my_log('test_user_friend_invite_auto_accept_true_to_true',
               {"auto": True}, ret)
        ret = user_im_setting(token)['data']['user_setting']["autoAcceptFriendInvitation"]
        assert ret is True




