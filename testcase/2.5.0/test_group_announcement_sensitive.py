# -*- coding:utf-8 -*-
# @author  : xj
# @file   : test_sensitive.py
# @ide    : PyCharm
# @time    : 2021/5/26 09:19
from time import sleep
from random import choice

import pytest
import allure

from lib.im_api_lib.login import login
from lib.im_api_lib.group_management import group_create_with_users, set_group_announcement, get_group_announcement, group_member_list, group_remove, group_manager_multi_add
from lib.im_api_lib.user import friend_attr_set, user_detail, user_friend_list, user_group_invite_auto_accept
from lib.im_api_lib.user import user_friend_invite_auto_accept
from lib.im_api_lib.user import user_group_invite_auto_accept
from lib.im_api_lib.user import user_friend_add_req
from lib.im_api_lib.user import user_friend_del_all
from common.my_log import my_log
from config.conf import user1_info, user2_info, user3_info, user4_info, user5_info


@pytest.fixture(scope="module", autouse=True)
def before_class(start_demo):
    token_1 = start_demo
    yield
    user_friend_del_all(token_1)


@allure.feature("设置群公告敏感词测试用例")
class TestSetDifferentAnnouncement:
    def setup_class(self):
        self.tokens = {}
        for user in (user1_info, user2_info, user3_info, user4_info, user5_info):
            user_id = user['user_id']
            token = login(user)
            self.tokens[user_id] = token
            user_friend_invite_auto_accept(token, True)
            user_group_invite_auto_accept(token, True)
        
        self.user_id = user1_info['user_id']
        self.token = self.tokens[self.user_id]
        
        for _id in self.tokens:
            if _id == self.user_id:
                continue
            user_friend_add_req(self.token, _id)    # 加好友
            
        friend_list_res = user_friend_list(self.token)
        friend_list = [i['userId'] for i in friend_list_res['data']]
        
        create_group_res = group_create_with_users(self.token, user_ids=','.join(friend_list))
        self.group_id = create_group_res['data']['communicationId']
        group_member_list_res = group_member_list(self.token, self.group_id)
        real_group_member_id = [i['userId'] for i in group_member_list_res['data']]
        real_group_member_id.remove(self.user_id)
        assert sorted(friend_list) == sorted(real_group_member_id)

    def teardown_class(self):
        group_remove(self.token, self.group_id)
        user1_info['user_id'] = self.user_id

    @allure.story("群公告敏感词黑名单设置")
    @allure.title("test_group_announcement_sensitive")
    @pytest.mark.parametrize("msg", 
                            ['专业代理', '專業代理', 'SM', 'sm', '3P', '买卖64狗', 'GFW', 'GFw', 'GfW', 'Gfw', 'gFW', 'gFw', 'gfW', 
                            'gfw', 'tnt炸药配方', 'www2.92ri.com', 'GaY片', 'GAy片', 'Gay片', 'GAY片', 'gaY片', 'gAy片', 'gay片', 
                            'gAY片', '專业代理', '專業代理', '专业代理', '专業代理', '々﹟#﹩$﹠&﹪%*﹡﹢﹦全套', '￣¯―﹨ˆ˜﹍﹎+=<＿_-\ˇ~﹉﹊（sm', 
                            '信用卡提现ˆˇ﹕︰﹔﹖﹑•¨….¸;！', 'youxing•¨….¸;！´？！', '操（）〈〉‹›﹛﹜『』〖〗［］《》〔〕{}「」【】逼', 
                            '流血?‘’“”〝〞ˆˇ﹕︰﹔﹖冲突'])
    def test_group_announcement_sensitive(self, msg):
        before_announcement_res = get_group_announcement(self.token, self.group_id)
        set_group_announcement_res = set_group_announcement(self.token, self.group_id, msg)
        my_log('test_group_announcement_sensitive', {"group_id": self.group_id, 'announcement': msg}, set_group_announcement_res)
        assert set_group_announcement_res['code'] == '1'
        assert set_group_announcement_res['error']['message'] == '群公告内容包含敏感词汇，请重新设置'
        after_announcement_res = get_group_announcement(self.token, self.group_id)
        assert before_announcement_res['data'] == after_announcement_res['data']  # 确定设置前后群公告没有变更

    @allure.story("群公告敏感词白名单设置")
    @allure.title("test_group_announcement_sensitive_white_list")
    @pytest.mark.parametrize("msg", ['EARLY', 'small'])
    def test_group_announcement_sensitive_white_list(self, msg):
        set_group_announcement_res = set_group_announcement(self.token, self.group_id, msg)
        my_log('test_group_announcement_sensitive', {"group_id":self.group_id, 'announcement': msg}, set_group_announcement_res)
        assert set_group_announcement_res['code'] == '0'
        after_announcement_res = get_group_announcement(self.token, self.group_id)
        assert after_announcement_res['data']['announcement'] == msg  # 确定设置成功
