import allure

from random import choice

from lib.im_api_lib.group_management import group_mutewhite_relieve
from lib.im_api_lib.group_management import group_mutewhite_add
from lib.im_api_lib.group_management import group_create_with_users
from lib.im_api_lib.group_management import group_manager_multi_add
from lib.im_api_lib.group_management import group_member_remove_multi
from lib.im_api_lib.group_management import group_mutewhite_list
from lib.im_api_lib.group_management import group_remove
from lib.im_api_lib.group_management import group_mute_list
from lib.im_api_lib.group_management import set_group_mute
from lib.im_api_lib.group_management import group_manager_list
from lib.im_api_lib.group_management import group_assignment
from lib.im_api_lib.group_management import group_detail
from lib.im_api_lib.group_management import group_member_list
from lib.im_api_lib.group_management import group_member_add_multi

from lib.im_api_lib.user import user_friend_invite_auto_accept, user_group_invite_auto_accept, user_friend_add_req, user_friend_del_all

from lib.im_api_lib.login import login
from common.my_log import my_log
from config.conf import user1_info, user2_info, user3_info, user4_info, user5_info


@allure.feature('测试群聊白名单场景')
class TestGroupWhiteList:
    
    def setup_class(self):
        self.users_token = {}
        self.user_ids = []
        for info in (user1_info, user2_info, user3_info, user4_info, user5_info):
            _token = login(info, True)
            self.users_token[info['user_id']] = _token
            self.user_ids.append(info['user_id'])
            user_friend_invite_auto_accept(_token, True)
            user_group_invite_auto_accept(_token, True)
        for k in self.users_token:
            for K in self.users_token:
                if K == k:
                    continue
                res = user_friend_add_req(self.users_token[k], K)
                print(res)
    
    def teardown_class(self):
        for _, token in self.users_token.items():
            user_friend_del_all(token)
    
    def setup_method(self):
        self.group_owner_id = choice(self.user_ids)
        member_list = self.user_ids[:]
        member_list.remove(self.group_owner_id)
        create_group_res = group_create_with_users(self.users_token[self.group_owner_id], user_ids=','.join(member_list))
        self.group_id = create_group_res['data']['communicationId']
        self.member_list = member_list
    
    def teardown_method(self):
        group_remove(self.users_token[self.group_owner_id], self.group_id)
    
    @allure.title('群主添加普通群员为白名单')
    def test_001(self):
        white_user_id = choice(self.member_list)
        add_res = group_mutewhite_add(self.users_token[self.group_owner_id], self.group_id, white_user_id)
        my_log('test_001[添加白名单]', white_user_id, add_res)
        assert add_res['code'] == '0'
        white_list_res = group_mutewhite_list(self.users_token[self.group_owner_id], self.group_id)
        my_log('test_001[白名单列表]', '', white_list_res)
        assert white_list_res['code'] == '0'
        assert white_user_id in [i['userId'] for i in white_list_res['data']]
    
    @allure.title('管理员添加普通群员为白名单')
    def test_002(self):
        manager_id = self.member_list.pop()
        add_manager_res = group_manager_multi_add(self.users_token[self.group_owner_id], self.group_id, manager_id)
        my_log('test_002[添加管理员]', manager_id, add_manager_res)
        assert add_manager_res['code'] == '0'
        
        white_user_id = choice(self.member_list)
        
        add_res = group_mutewhite_add(self.users_token[manager_id], self.group_id, white_user_id)
        my_log('test_002[添加白名单]', white_user_id, add_res)
        assert add_res['code'] == '0'
        white_list_res = group_mutewhite_list(self.users_token[manager_id], self.group_id)
        my_log('test_002[白名单列表]', '', white_list_res)
        assert white_list_res['code'] == '0'
        assert white_user_id in [i['userId'] for i in white_list_res['data']]
        
    @allure.title('普通成员加群主/管理员/普通用户/为白名单')
    def test_003(self):
        manager_id = self.member_list.pop()
        add_manager_res = group_manager_multi_add(self.users_token[self.group_owner_id], self.group_id, manager_id)
        my_log('test_003[添加管理员]', manager_id, add_manager_res)
        
        normal_id = self.member_list.pop()
        
        add_res = group_mutewhite_add(self.users_token[normal_id], self.group_id, self.group_owner_id)  # 加群主
        my_log('test_003[添加白名单]', self.group_owner_id, add_res)
        assert add_res['code'] == '1' and 'error' in add_res and add_res['error']['code'] == 1604 and add_res['error']['message'] == '没有权限进行该操作'
        
        add_res = group_mutewhite_add(self.users_token[normal_id], self.group_id, manager_id)  # 加管理员
        my_log('test_003[添加白名单]', self.group_owner_id, add_res)
        assert add_res['code'] == '1' and 'error' in add_res and add_res['error']['code'] == 1604 and add_res['error']['message'] == '没有权限进行该操作'
        
        add_res = group_mutewhite_add(self.users_token[normal_id], self.group_id, choice(self.member_list))  # 加普通成员
        my_log('test_003[添加白名单]', self.group_owner_id, add_res)
        assert add_res['code'] == '1' and 'error' in add_res and add_res['error']['code'] == 1604 and add_res['error']['message'] == '没有权限进行该操作'
    
    @allure.title('群主添加管理员为白名单')
    def test_004(self):
        manager_id = self.member_list.pop()
        add_manager_res = group_manager_multi_add(self.users_token[self.group_owner_id], self.group_id, manager_id)
        my_log('test_004[添加管理员]', manager_id, add_manager_res)
        
        add_res = group_mutewhite_add(self.users_token[self.group_owner_id], self.group_id, manager_id)  # 加管理员
        my_log('test_004[添加白名单]', manager_id, add_res)
        assert add_res['code'] == '1' and 'error' in add_res and add_res['error']['code'] == 1644 and add_res['error']['message'] == '群管理员不能添加进来'
        
    @allure.title('管理员添加群主为白名单')
    def test_005(self):
        manager_id = self.member_list.pop()
        add_manager_res = group_manager_multi_add(self.users_token[self.group_owner_id], self.group_id, manager_id)
        my_log('test_005[添加管理员]', manager_id, add_manager_res)
        
        add_res = group_mutewhite_add(self.users_token[manager_id], self.group_id, self.group_owner_id)  # 加群主
        my_log('test_005[添加白名单]', manager_id, add_res)
        assert add_res['code'] == '1' and 'error' in add_res and add_res['error']['code'] == 1645 and add_res['error']['message'] == '群主不能被加入禁言白名单'
        
    @allure.title('群主移除普通群员白名单')
    def test_006(self):
        white_user_id = choice(self.member_list)
        add_res = group_mutewhite_add(self.users_token[self.group_owner_id], self.group_id, white_user_id)
        my_log('test_006[添加白名单]', white_user_id, add_res)
        assert add_res['code'] == '0'
        white_list_res = group_mutewhite_list(self.users_token[self.group_owner_id], self.group_id)
        my_log('test_006[白名单列表]', '', white_list_res)
        assert white_list_res['code'] == '0'
        assert white_user_id in [i['userId'] for i in white_list_res['data']]
        
        group_mutewhite_relieve_res = group_mutewhite_relieve(self.users_token[self.group_owner_id], self.group_id, white_user_id)
        my_log('test_006[移除白名单列表]', white_user_id, group_mutewhite_relieve_res)
        assert group_mutewhite_relieve_res['code'] == '0'
        
        white_list_res = group_mutewhite_list(self.users_token[self.group_owner_id], self.group_id)
        my_log('test_006[白名单列表]', '', white_list_res)
        assert white_list_res['code'] == '0'
        assert white_user_id not in [i['userId'] for i in white_list_res['data']]
        
    @allure.title('管理员移除普通群员白名单')
    def test_007(self):
        manager_id = self.member_list.pop()
        add_manager_res = group_manager_multi_add(self.users_token[self.group_owner_id], self.group_id, manager_id)
        my_log('test_007[添加管理员]', manager_id, add_manager_res)
        assert add_manager_res['code'] == '0'
        
        white_user_id = choice(self.member_list)
        
        add_res = group_mutewhite_add(self.users_token[self.group_owner_id], self.group_id, white_user_id)
        my_log('test_007[添加白名单]', white_user_id, add_res)
        assert add_res['code'] == '0'
        white_list_res = group_mutewhite_list(self.users_token[self.group_owner_id], self.group_id)
        my_log('test_007[白名单列表]', '', white_list_res)
        assert white_list_res['code'] == '0'
        assert white_user_id in [i['userId'] for i in white_list_res['data']]
        
        group_mutewhite_relieve_res = group_mutewhite_relieve(self.users_token[manager_id], self.group_id, white_user_id)   # 管理员移除白名单
        my_log('test_007[移除白名单列表]', white_user_id, group_mutewhite_relieve_res)
        assert group_mutewhite_relieve_res['code'] == '0'
        
        white_list_res = group_mutewhite_list(self.users_token[self.group_owner_id], self.group_id)
        my_log('test_007[白名单列表]', '', white_list_res)
        assert white_list_res['code'] == '0'
        assert white_user_id not in [i['userId'] for i in white_list_res['data']]
        
    @allure.title('普通群员移除普通群员/群主/管理为白名单')
    def test_008(self):
        manager_id = self.member_list.pop()
        add_manager_res = group_manager_multi_add(self.users_token[self.group_owner_id], self.group_id, manager_id)
        my_log('test_008[添加管理员]', manager_id, add_manager_res)
        assert add_manager_res['code'] == '0'
        
        white_user_id = choice(self.member_list)
        
        add_res = group_mutewhite_add(self.users_token[manager_id], self.group_id, white_user_id)
        my_log('test_008[添加白名单]', white_user_id, add_res)
        assert add_res['code'] == '0'
        white_list_res = group_mutewhite_list(self.users_token[manager_id], self.group_id)
        my_log('test_008[白名单列表]', '', white_list_res)
        assert white_list_res['code'] == '0'
        assert white_user_id in [i['userId'] for i in white_list_res['data']]
        
        other_normal_id = self.member_list.pop()
        
        group_mutewhite_relieve_res = group_mutewhite_relieve(self.users_token[other_normal_id], self.group_id, white_user_id)   # 普通成员移除普通成员
        my_log('test_008[普通成员移除白名单列表]', white_user_id, group_mutewhite_relieve_res)
        assert group_mutewhite_relieve_res['code'] == '1' and 'error' in group_mutewhite_relieve_res and group_mutewhite_relieve_res['error']['code'] == 1604 and group_mutewhite_relieve_res['error']['message'] == '没有权限进行该操作'

        group_mutewhite_relieve_res = group_mutewhite_relieve(self.users_token[other_normal_id], self.group_id, manager_id)   # 普通成员移除管理员
        my_log('test_008[普通成员移除管理员]', white_user_id, group_mutewhite_relieve_res)
        assert group_mutewhite_relieve_res['code'] == '1' and 'error' in group_mutewhite_relieve_res and group_mutewhite_relieve_res['error']['code'] == 1604 and group_mutewhite_relieve_res['error']['message'] == '没有权限进行该操作'
        
        group_mutewhite_relieve_res = group_mutewhite_relieve(self.users_token[other_normal_id], self.group_id, self.group_owner_id)   # 普通成员移除群主
        my_log('test_008[普通成员移除群主]', white_user_id, group_mutewhite_relieve_res)
        assert group_mutewhite_relieve_res['code'] == '1' and 'error' in group_mutewhite_relieve_res and group_mutewhite_relieve_res['error']['code'] == 1604 and group_mutewhite_relieve_res['error']['message'] == '没有权限进行该操作'

    @allure.title('群主移除管理员白名单')
    def test_009(self):
        manager_id = self.member_list.pop()
        add_manager_res = group_manager_multi_add(self.users_token[self.group_owner_id], self.group_id, manager_id)
        my_log('test_009[添加管理员]', manager_id, add_manager_res)
        assert add_manager_res['code'] == '0'
        
        group_mutewhite_relieve_res = group_mutewhite_relieve(self.users_token[self.group_owner_id], self.group_id, manager_id)   # 群主移除管理员白名单
        my_log('test_009[群主移除管理员白名单]', manager_id, group_mutewhite_relieve_res)
        
        assert group_mutewhite_relieve_res['code'] != '0'

    @allure.title('管理员移除群主白名单')
    def test_010(self):
        manager_id = self.member_list.pop()
        add_manager_res = group_manager_multi_add(self.users_token[self.group_owner_id], self.group_id, manager_id)
        my_log('test_010[添加管理员]', manager_id, add_manager_res)
        assert add_manager_res['code'] == '0'
        
        group_mutewhite_relieve_res = group_mutewhite_relieve(self.users_token[manager_id], self.group_id, self.group_owner_id)   # 管理员移除群主白名单
        my_log('test_010[管理员移除群主白名单]', self.group_owner_id, group_mutewhite_relieve_res)
        
        assert group_mutewhite_relieve_res['code'] != '0'

    @allure.title('群主添加多个群员为白名单')
    def test_011(self):
        add_res = group_mutewhite_add(self.users_token[self.group_owner_id], self.group_id, ','.join(self.member_list))
        my_log('test_011[群主添加多个群员为白名单]', self.member_list, add_res)
        assert add_res['code'] == '0'
        white_list_res = group_mutewhite_list(self.users_token[self.group_owner_id], self.group_id)
        my_log('test_011[白名单列表]', '', white_list_res)
        assert white_list_res['code'] == '0'
        assert sorted(self.member_list) == sorted([i['userId'] for i in white_list_res['data']])
    
    @allure.title('管理员添加多个群员为白名单')
    def test_012(self):
        manager_id = self.member_list.pop()
        add_manager_res = group_manager_multi_add(self.users_token[self.group_owner_id], self.group_id, manager_id)
        my_log('test_012[添加管理员]', manager_id, add_manager_res)
        assert add_manager_res['code'] == '0'
        
        add_res = group_mutewhite_add(self.users_token[manager_id], self.group_id, ','.join(self.member_list))
        my_log('test_012[添加白名单]', self.member_list, add_res)
        assert add_res['code'] == '0'
        white_list_res = group_mutewhite_list(self.users_token[manager_id], self.group_id)
        my_log('test_012[白名单列表]', '', white_list_res)
        assert white_list_res['code'] == '0'
        assert sorted(self.member_list) == sorted([i['userId'] for i in white_list_res['data']])
        
    @allure.title('群主移出多个群员白名单')
    def test_013(self):
        add_res = group_mutewhite_add(self.users_token[self.group_owner_id], self.group_id, ','.join(self.member_list))
        my_log('test_013[群主添加多个群员为白名单]', self.member_list, add_res)
        assert add_res['code'] == '0'
        
        white_list_res = group_mutewhite_list(self.users_token[self.group_owner_id], self.group_id)
        my_log('test_013[白名单列表]', '', white_list_res)
        assert white_list_res['code'] == '0'
        assert sorted(self.member_list) == sorted([i['userId'] for i in white_list_res['data']])
        
        group_mutewhite_relieve_res = group_mutewhite_relieve(self.users_token[self.group_owner_id], self.group_id, ','.join(self.member_list))   # 群主移除所有ren
        my_log('test_013[群主移出多个群员白名单]', self.member_list, group_mutewhite_relieve_res)
        
        white_list_res = group_mutewhite_list(self.users_token[self.group_owner_id], self.group_id)
        my_log('test_013[白名单列表]', '', white_list_res)
        assert white_list_res['code'] == '0'
        assert [i['userId'] for i in white_list_res['data']] == []
        
    @allure.title('管理员移出多个群员白名单')
    def test_014(self):
        manager_id = self.member_list.pop()
        add_manager_res = group_manager_multi_add(self.users_token[self.group_owner_id], self.group_id, manager_id)
        my_log('test_014[添加管理员]', manager_id, add_manager_res)
        assert add_manager_res['code'] == '0'
        
        add_res = group_mutewhite_add(self.users_token[manager_id], self.group_id, ','.join(self.member_list))
        my_log('test_014[管理员添加多个群员为白名单]', self.member_list, add_res)
        assert add_res['code'] == '0'
        
        white_list_res = group_mutewhite_list(self.users_token[self.group_owner_id], self.group_id)
        my_log('test_014[白名单列表]', '', white_list_res)
        assert white_list_res['code'] == '0'
        assert sorted(self.member_list) == sorted([i['userId'] for i in white_list_res['data']])
        
        group_mutewhite_relieve_res = group_mutewhite_relieve(self.users_token[manager_id], self.group_id, ','.join(self.member_list))   # 管理员移除所有白名单
        my_log('test_014[管理员移除所有白名单]', self.member_list, group_mutewhite_relieve_res)
        assert group_mutewhite_relieve_res['code'] == '0'
        
        white_list_res = group_mutewhite_list(self.users_token[self.group_owner_id], self.group_id)
        my_log('test_014[白名单列表]', '', white_list_res)
        assert white_list_res['code'] == '0'
        assert [i['userId'] for i in white_list_res['data']] == []
        
    @allure.title('群主添加群禁言成员添加为白名单')
    def test_015(self):
        mute_id = self.member_list.pop()
        
        add_mute_res = set_group_mute(self.users_token[self.group_owner_id], self.group_id, mute_id, 'add')
        my_log('test_015[群主添加禁言名单]', mute_id, add_mute_res)
        assert add_mute_res['code'] == '0'
        
        group_mute_list_res = group_mute_list(self.users_token[self.group_owner_id], self.group_id)
        my_log('test_015[禁言列表]', '', group_mute_list_res)
        assert group_mute_list_res['code'] == '0'
        assert mute_id in [i['userId'] for i in group_mute_list_res['data']]
        
        add_res = group_mutewhite_add(self.users_token[self.group_owner_id], self.group_id, mute_id)    # 群主加禁言用户为白名单
        my_log('test_015[群主加禁言用户为白名单]', mute_id, add_res)
        assert add_res['code'] == '0'
        
        white_list_res = group_mutewhite_list(self.users_token[self.group_owner_id], self.group_id)
        my_log('test_015[白名单列表]', '', white_list_res)
        assert white_list_res['code'] == '0'
        assert mute_id in [i['userId'] for i in white_list_res['data']]
        
        group_mute_list_res = group_mute_list(self.users_token[self.group_owner_id], self.group_id)
        my_log('test_015[禁言列表]', '', group_mute_list_res)
        assert group_mute_list_res['code'] == '0'
        assert mute_id not in [i['userId'] for i in group_mute_list_res['data']]
    
    @allure.title('管理员添加群禁言成员添加为白名单')
    def test_016(self):
        manager_id = self.member_list.pop()
        add_manager_res = group_manager_multi_add(self.users_token[self.group_owner_id], self.group_id, manager_id)
        my_log('test_016[添加管理员]', manager_id, add_manager_res)
        assert add_manager_res['code'] == '0'
        
        mute_id = self.member_list.pop()
        
        add_mute_res = set_group_mute(self.users_token[self.group_owner_id], self.group_id, mute_id, 'add')
        my_log('test_016[群主添加禁言名单]', mute_id, add_mute_res)
        assert add_mute_res['code'] == '0'
        
        group_mute_list_res = group_mute_list(self.users_token[self.group_owner_id], self.group_id)
        my_log('test_016[禁言列表]', '', group_mute_list_res)
        assert group_mute_list_res['code'] == '0'
        assert mute_id in [i['userId'] for i in group_mute_list_res['data']]
        
        add_res = group_mutewhite_add(self.users_token[manager_id], self.group_id, mute_id)    # 管理员加禁言用户为白名单
        my_log('test_016[管理员加禁言用户为白名单]', mute_id, add_res)
        assert add_res['code'] == '0'
        
        white_list_res = group_mutewhite_list(self.users_token[self.group_owner_id], self.group_id)
        my_log('test_016[白名单列表]', '', white_list_res)
        assert white_list_res['code'] == '0'
        assert mute_id in [i['userId'] for i in white_list_res['data']]
        
        group_mute_list_res = group_mute_list(self.users_token[self.group_owner_id], self.group_id)
        my_log('test_016[禁言列表]', '', group_mute_list_res)
        assert group_mute_list_res['code'] == '0'
        assert mute_id not in [i['userId'] for i in group_mute_list_res['data']]
        
    @allure.title('白名单用户成为管理员')
    def test_017(self):
        white_user_id = choice(self.member_list)
        add_res = group_mutewhite_add(self.users_token[self.group_owner_id], self.group_id, white_user_id)
        my_log('test_017[添加白名单]', white_user_id, add_res)
        assert add_res['code'] == '0'
        white_list_res = group_mutewhite_list(self.users_token[self.group_owner_id], self.group_id)
        my_log('test_017[白名单列表]', '', white_list_res)
        assert white_list_res['code'] == '0'
        assert white_user_id in [i['userId'] for i in white_list_res['data']]
        
        add_manager_res = group_manager_multi_add(self.users_token[self.group_owner_id], self.group_id, white_user_id)
        my_log('test_017[群主添加白名单用户为管理员]', white_user_id, add_manager_res)
        assert add_manager_res['code'] == '0'
        
        group_manager_list_res = group_manager_list(self.users_token[self.group_owner_id], self.group_id)
        my_log('test_017[管理员列表]', '', group_manager_list_res)
        assert white_user_id in [i['userId'] for i in group_manager_list_res['data']]
        
        white_list_res = group_mutewhite_list(self.users_token[self.group_owner_id], self.group_id)
        my_log('test_017[白名单列表]', '', white_list_res)
        assert white_list_res['code'] == '0'
        assert white_user_id not in [i['userId'] for i in white_list_res['data']]
        
    @allure.title('白名单用户成为群主')
    def test_018(self):
        white_user_id = choice(self.member_list)
        add_res = group_mutewhite_add(self.users_token[self.group_owner_id], self.group_id, white_user_id)
        my_log('test_018[添加白名单]', white_user_id, add_res)
        assert add_res['code'] == '0'
        white_list_res = group_mutewhite_list(self.users_token[self.group_owner_id], self.group_id)
        my_log('test_018[白名单列表]', '', white_list_res)
        assert white_list_res['code'] == '0'
        assert white_user_id in [i['userId'] for i in white_list_res['data']]
        
        group_assignment_res = group_assignment(self.users_token[self.group_owner_id], self.group_id, white_user_id)
        my_log('test_018[群主将群转给白名单用户]', white_user_id, group_assignment_res)
        assert group_assignment_res['code'] == '0'
        self.group_owner_id = white_user_id
        
        group_detail_res = group_detail(self.users_token[self.group_owner_id], self.group_id)
        my_log('test_018[群详情]', '', group_detail_res)
        assert group_detail_res['code'] == '0'
        assert group_detail_res['data']['ownerId'] == white_user_id
        
        white_list_res = group_mutewhite_list(self.users_token[self.group_owner_id], self.group_id)
        my_log('test_018[白名单列表]', '', white_list_res)
        assert white_list_res['code'] == '0'
        assert white_user_id not in [i['userId'] for i in white_list_res['data']]
    
    @allure.title('白名单用户踢出群聊、白名单用户踢出群聊再进群')
    def test_019(self):
        white_user_id = choice(self.member_list)
        add_res = group_mutewhite_add(self.users_token[self.group_owner_id], self.group_id, white_user_id)
        my_log('test_019[添加白名单]', white_user_id, add_res)
        assert add_res['code'] == '0'
        white_list_res = group_mutewhite_list(self.users_token[self.group_owner_id], self.group_id)
        my_log('test_019[白名单列表]', '', white_list_res)
        assert white_list_res['code'] == '0'
        assert white_user_id in [i['userId'] for i in white_list_res['data']]
        
        group_member_remove_res = group_member_remove_multi(self.users_token[self.group_owner_id], self.group_id, white_user_id)
        my_log('test_019[将白名单用户移除群聊]', white_user_id, group_member_remove_res)
        assert group_member_remove_res['code'] == '0'
        
        group_member_list_res = group_member_list(self.users_token[self.group_owner_id], self.group_id)
        my_log('test_019[群成员列表]', '', group_member_list_res)
        assert group_member_list_res['code'] == '0'
        assert white_user_id not in [i['userId'] for i in group_member_list_res['data']]
        
        white_list_res = group_mutewhite_list(self.users_token[self.group_owner_id], self.group_id)
        my_log('test_019[白名单列表]', '', white_list_res)
        assert white_list_res['code'] == '0'
        assert white_user_id not in [i['userId'] for i in white_list_res['data']]
        
        # 群主再次将移除的用户邀请入群
        group_member_add_res = group_member_add_multi(self.users_token[self.group_owner_id], self.group_id, white_user_id)
        my_log('test_019[群主再次将移除的用户邀请入群]', '', group_member_add_res)
        assert group_member_add_res['code'] == '0'
        
        group_member_list_res = group_member_list(self.users_token[self.group_owner_id], self.group_id)
        my_log('test_019[群成员列表]', '', group_member_list_res)
        assert group_member_list_res['code'] == '0'
        assert white_user_id in [i['userId'] for i in group_member_list_res['data']]
        
        white_list_res = group_mutewhite_list(self.users_token[self.group_owner_id], self.group_id)
        my_log('test_019[白名单列表]', '', white_list_res)
        assert white_list_res['code'] == '0'
        assert white_user_id not in [i['userId'] for i in white_list_res['data']]
