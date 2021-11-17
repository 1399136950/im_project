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


@allure.feature("不同身份设置群公告测试用例")
class TestSetAnnouncement:
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
        
        self.group_manager = []
        self.normal_member = []
        _friend_list = friend_list[:]
        for i in range(int(len(friend_list)/2)):
            _id = choice(_friend_list)
            _friend_list.remove(_id)
            self.group_manager.append(_id)
        self.normal_member = _friend_list[:]
        self.friend_list = friend_list
    
    def setup_method(self):
        create_group_res = group_create_with_users(self.token, user_ids=','.join(self.friend_list))
        self.group_id = create_group_res['data']['communicationId']
        group_member_list_res = group_member_list(self.token, self.group_id)
        real_group_member_id = [i['userId'] for i in group_member_list_res['data']]
        real_group_member_id.remove(self.user_id)
        assert sorted(self.friend_list) == sorted(real_group_member_id)
        
    def teardown_method(self):
        group_remove(self.token, self.group_id)

    @allure.story("群主设置群公告")
    def test_group_owner_set_announcement(self):
        announcement = 'hello world222'
        setter_user_info_res = user_detail(self.token, self.user_id)
        set_group_announcement_res = set_group_announcement(self.token, self.group_id, announcement)
        my_log('test_group_owner_set_announcement', {"group_id":self.group_id, "announcement": announcement}, set_group_announcement_res)
        assert set_group_announcement_res['code'] == '0'
        get_group_announcement_res = get_group_announcement(self.token, self.group_id)
        
        my_log('test_group_owner_set_announcement', {"group_id":self.group_id}, get_group_announcement_res)
        assert get_group_announcement_res['data']['announcement'] == announcement
        assert self.diff_announcement_info(get_group_announcement_res['data'], setter_user_info_res['data'])
        
        normal_member_id = choice(self.normal_member)  # 随机普通成员
        get_group_announcement_res = get_group_announcement(self.tokens[normal_member_id], self.group_id)
        assert get_group_announcement_res['data']['announcement'] == announcement
        assert self.diff_announcement_info(get_group_announcement_res['data'], setter_user_info_res['data'])
    
    def diff_announcement_info(self, announcement_info, user_info):
        assert user_info['nickname'] == announcement_info['publisherName']
        assert user_info['avatar'] == announcement_info['avatar']
        return True
    
    @allure.story("管理员设置群公告")
    def test_group_manager_set_announcement(self):
        announcement = 'hello world111'

        mamager_id = choice(self.group_manager)  # 随机管理员

        set_manager_res = group_manager_multi_add(self.token, self.group_id, mamager_id)
        assert set_manager_res['code'] == '0'

        manager_token = self.tokens[mamager_id]
        setter_user_info_res = user_detail(manager_token, mamager_id)

        set_group_announcement_res = set_group_announcement(manager_token, self.group_id, announcement)
        my_log('test_group_manager_set_announcement', {"group_id":self.group_id, "announcement": announcement}, set_group_announcement_res)
        assert set_group_announcement_res['code'] == '0'
        get_group_announcement_res = get_group_announcement(self.token, self.group_id)

        assert get_group_announcement_res['data']['announcement'] == announcement
        assert self.diff_announcement_info(get_group_announcement_res['data'], setter_user_info_res['data'])

        get_group_announcement_res = get_group_announcement(manager_token, self.group_id)

        assert get_group_announcement_res['data']['announcement'] == announcement
        assert self.diff_announcement_info(get_group_announcement_res['data'], setter_user_info_res['data'])

        normal_member_id = choice(self.normal_member)  # 随机普通成员
        get_group_announcement_res = get_group_announcement(self.tokens[normal_member_id], self.group_id)

        assert get_group_announcement_res['data']['announcement'] == announcement
        assert self.diff_announcement_info(get_group_announcement_res['data'], setter_user_info_res['data'])

    @allure.story("普通成员设置群公告")
    def test_group_normal_member_set_announcement(self):
        announcement = 'hello world333'
        normal_member_id = choice(self.normal_member)  # 随机普通成员
        before_announcement_res = get_group_announcement(self.token, self.group_id)
        set_group_announcement_res = set_group_announcement(self.tokens[normal_member_id], self.group_id, announcement)
        my_log('test_group_normal_member_set_announcement', {"group_id":self.group_id, "announcement": announcement}, set_group_announcement_res)
        assert set_group_announcement_res['code'] == '1'
        assert set_group_announcement_res['msg'] == 'FAIL'
        assert set_group_announcement_res['error']['code'] == 1604 and set_group_announcement_res['error']['message'] == '没有权限进行该操作'
        after_announcement_res = get_group_announcement(self.token, self.group_id)
        assert before_announcement_res['data'] == after_announcement_res['data']  # 确定设置前后群公告没有变更

    @allure.story("设置群公告长度用例")
    def test_set_by_length(self):
        set_group_announcement_res = set_group_announcement(self.token, self.group_id, '')
        assert set_group_announcement_res['code'] == '0'

        set_group_announcement_res = set_group_announcement(self.token, self.group_id, '哈'*499)
        assert set_group_announcement_res['code'] == '0'

        set_group_announcement_res = set_group_announcement(self.token, self.group_id, '哈'*500)
        assert set_group_announcement_res['code'] == '0'

        set_group_announcement_res = set_group_announcement(self.token, self.group_id, '哈'*501)
        assert set_group_announcement_res['code'] == '1'
        assert set_group_announcement_res['error']['code'] == 1643 and set_group_announcement_res['error']['message'] == '群公告太长'

    @allure.story("设置异常群id")
    def test_set_announcement_by_err_group_id(self):
        announcement = 'hello world333'
        set_group_announcement_res = set_group_announcement(self.token, '123efsdget5ytg', announcement)
        my_log('test_set_announcement_by_err_group_id', {"group_id": '123efsdget5ytg', "announcement": announcement}, set_group_announcement_res)
        assert set_group_announcement_res['code'] == '1'
