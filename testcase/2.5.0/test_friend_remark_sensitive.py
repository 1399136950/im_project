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

    @allure.story("好友备注敏感词黑名单设置场景")
    @allure.title("test_friend_remark_sensitive")
    @pytest.mark.parametrize("msg", 
                            ['专业代理', '專業代理', 'SM', 'sm', '3P', '买卖64狗', 'GFW', 'GFw', 'GfW', 'Gfw', 'gFW', 'gFw', 'gfW', 
                            'gfw', 'tnt炸药配方', 'www2.92ri.com', 'GaY片', 'GAy片', 'Gay片', 'GAY片', 'gaY片', 'gAy片', 'gay片', 
                            'gAY片', '專业代理', '專業代理', '专业代理', '专業代理', '々﹟#﹩$﹠&﹪%*﹡﹢﹦全套', '￣¯―﹨ˆ˜﹍﹎+=<＿_-\ˇ~﹉﹊（sm', 
                            '信用卡提现ˆˇ﹕︰﹔﹖﹑•¨….¸;！', 'youxing•¨….¸;！´？！', '操（）〈〉‹›﹛﹜『』〖〗［］《》〔〕{}「」【】逼', 
                            '流血?‘’“”〝〞ˆˇ﹕︰﹔﹖冲突'])
    def test_friend_remark_sensitive(self, start_demo, msg):
        token_1 = start_demo
        before_friend_info = user_detail(token_1, user2_info["user_id"])
        before_remark = before_friend_info['data']['remark']
        res = friend_attr_set(token_1, user2_info["user_id"], 'remark', msg)
        my_log('test_friend_remark_sensitive',
               {"friend_id": user2_info["user_id"], 'key': 'remark', 'value': msg}, res)
        after_friend_info = user_detail(token_1, user2_info["user_id"])
        after_remark = after_friend_info['data']['remark']
        assert res['code'] == '1'
        assert res['error']['message'] == '好友备注包含敏感词汇，请重新设置'
        assert before_remark == after_remark

    @allure.story("好友备注敏感词白名单设置场景")
    @allure.title("test_friend_remark_sensitive_white_list")
    @pytest.mark.parametrize("msg", ['EARLY', 'small'])
    def test_friend_remark_sensitive_white_list(self, start_demo, msg):
        token_1 = start_demo
        before_friend_info = user_detail(token_1, user2_info["user_id"])
        before_remark = before_friend_info['data']['remark']
        res = friend_attr_set(token_1, user2_info["user_id"], 'remark', msg)
        my_log('test_friend_remark_sensitive_white_list',
               {"friend_id": user2_info["user_id"],
                'key': 'remark',
                'value': msg}, res)
        after_friend_info = user_detail(token_1, user2_info["user_id"])
        after_remark = after_friend_info['data']['remark']
        assert res['code'] == '0'
        assert after_remark == msg
