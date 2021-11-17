# -*- coding:utf-8 -*-
# @author  : xj
# @file   : test_sensitive.py
# @ide    : PyCharm
# @time    : 2021/5/26 09:19
import pytest
import allure

from lib.im_api_lib.user import friend_attr_set, user_detail
from lib.im_api_lib.user import user_friend_add_req
from lib.im_api_lib.user import user_friend_invite_auto_accept
from lib.im_api_lib.user import user_friend_del_all
from config.conf import user1_info, user2_info, user3_info, user4_info, user5_info
from lib.im_api_lib.login import login
from common.my_log import my_log


@allure.feature("好友备注敏感词过滤功能测试")
class TestSensitive:
    def setup_class(self):
        self.token_2 = login(user2_info)
        self.token_3 = login(user3_info)
        self.token_4 = login(user4_info)
        self.token_5 = login(user5_info)
        user_friend_invite_auto_accept(self.token_2, True)
        user_friend_invite_auto_accept(self.token_3, True)
        user_friend_invite_auto_accept(self.token_4, True)
        user_friend_invite_auto_accept(self.token_5, True)

    @pytest.fixture(scope="class", autouse=True)
    def before_class(self, start_demo):
        token_1 = start_demo
        user_friend_add_req(token_1, user_id=user2_info["user_id"])
        user_friend_add_req(token_1, user_id=user3_info["user_id"])
        user_friend_add_req(token_1, user_id=user4_info["user_id"])
        user_friend_add_req(token_1, user_id=user5_info["user_id"])
        yield
        user_friend_del_all(token_1)

    @allure.story("好友备注长度设置场景")
    def test_set_friend_remark_by_different_length(self, start_demo):
        token_1 = start_demo
        before_friend_info = user_detail(token_1, user2_info["user_id"])
        before_remark = before_friend_info['data']['remark']
        res = friend_attr_set(token_1, user2_info["user_id"], 'remark', '')
        my_log('test_set_friend_remark_by_different_length',
               {"friend_id": user2_info["user_id"],
                'key': 'remark', 'value': ''},
               res)
        assert res['code'] == '1' and res['msg'] == 'FAIL'
        assert res['error']['code'] == 1205 and res['error']['message'] == '参数不合法'
