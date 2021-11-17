from random import choice
import time

import pytest
import allure

from lib.im_socket_lib.sync_im_user import IMUser
from common.my_log import my_log


from config.conf import USER_INFO


@allure.feature('测试单聊删除漫游消息')
class TestSingleDelRoamingMsg:

    users = {}
    friend_id_list = []

    def setup_class(self):
        self.users = {}
        self.user_id_list = []
        all_user_info = USER_INFO[:]

        for info in all_user_info:
            user_id = info['user_id']
            self.users[user_id] = IMUser(info)
            self.users[user_id].run()
            del_res = self.users[user_id].delete_sync_msg_by_user()
            my_log('setup_class[删除用户漫游消息]', user_id, del_res)
            self.users[user_id].accept_friend_group()   # 设置自动加好友和加入群
            self.user_id_list.append(user_id)

        for user_id in self.users:
            user = self.users[user_id]
            for friend_id in self.users:
                if friend_id == user_id:
                    continue
                res = user.add_friend(friend_id)
                print(res)
        self.test_user_info = choice(all_user_info)
        self.users[self.test_user_info['user_id']].logout()
        self.user_id_list.remove(self.test_user_info['user_id'])

    # def setup_method(self):
    #     self.users = {}
    #     self.user_id_list = []
    #     all_user_info = [user1_info, user2_info, user3_info, user4_info, user5_info]
    #
    #     for info in all_user_info:
    #         user_id = info['user_id']
    #         self.users[user_id] = IMUser(info)
    #         self.users[user_id].run()
    #         del_res = self.users[user_id].delete_sync_msg_by_user()
    #         my_log('setup_method[删除用户漫游消息]', user_id, del_res)
    #         self.users[user_id].accept_friend_group()   # 设置自动加好友和加入群
    #         self.user_id_list.append(user_id)
    #
    #     for user_id in self.users:
    #         user = self.users[user_id]
    #         for friend_id in self.users:
    #             if friend_id == user_id:
    #                 continue
    #             res = user.add_friend(friend_id)
    #             print(res)
    #
    #     self.test_user_info = choice(all_user_info)
    #     self.users[self.test_user_info['user_id']].logout()
    #     self.user_id_list.remove(self.test_user_info['user_id'])

    def teardown_method(self):
        test_user_id = self.test_user_info['user_id']
        test_user = self.users[test_user_id]
        del_res = test_user.delete_sync_msg_by_user()
        assert del_res['code'] == '0'
        test_user.logout()

    def teardown_class(self):
        for user_id in self.users:
            # del_res = self.users[user_id].delete_sync_msg_by_user()
            # my_log('teardown_class[删除用户漫游消息]', user_id, del_res)
            self.users[user_id].logout()

    @allure.title('用户离线，好友给他发送消息，用户上线接收该离线消息，然后清空漫游消息，不保存消息ID和时间戳退出，再次上线拉取，然后清空用户漫游消息，退出重新登录拉取消息')
    def test_001(self):
        normal_user_id = choice(self.user_id_list)
        normal_user = self.users[normal_user_id]

        test_user_id = self.test_user_info['user_id']

        src_msg = normal_user.send_text_msg(normal_user.user_detail[test_user_id]['conversationId'], 1, time.strftime('%Y-%m-%d %H:%M:%S'), test_user_id)

        reply_msg = normal_user.find_reply_msg_by_tag(src_msg['tag'])

        my_log('test_001[发送消息]', src_msg, reply_msg)

        time.sleep(1)

        test_user = IMUser(self.test_user_info)
        self.users[test_user_id] = test_user
        test_user.run()

        test_user.get_sync_msg()

        offline_msg_list = test_user.communication_msg[test_user.user_detail[normal_user_id]['conversationId']]

        my_log('test_001[离线消息]', '', offline_msg_list)

        assert len(offline_msg_list) > 0

        assert str(offline_msg_list[-1]['messageId']) == reply_msg['message_id']

        test_user.logout_without_save_info()    # 退出时不更新ID和时间戳
        time.sleep(5)

        # 再次上线，确保能拉到离线消息
        test_user = IMUser(self.test_user_info)
        self.users[test_user_id] = test_user
        test_user.run()

        test_user.get_sync_msg()

        new_offline_msg_list = test_user.communication_msg[test_user.user_detail[normal_user_id]['conversationId']]

        my_log('test_001[重新登录再次拉取离线消息]', '', new_offline_msg_list)

        assert new_offline_msg_list == offline_msg_list

        del_res = test_user.delete_sync_msg_by_user()
        my_log('test_001[删除用户漫游消息]', '', del_res)
        assert del_res['code'] == '0'
        test_user.logout_without_save_info()
        time.sleep(5)

        # 再次上线，确保拉不到离线消息
        test_user = IMUser(self.test_user_info)
        self.users[test_user_id] = test_user
        test_user.run()

        test_user.get_sync_msg()

        offline_msg_list = test_user.communication_msg[test_user.user_detail[normal_user_id]['conversationId']]

        my_log('test_001[重新登录再次拉取离线消息]', '', offline_msg_list)

        assert len(offline_msg_list) == 0

    @allure.title('用户离线，好友给他发送消息，用户上线接收该离线消息，不保存消息ID和时间戳退出，再次上线拉取，然后清空会话漫游消息，退出重新登录拉取消息')
    def test_002(self):
        normal_user_id = choice(self.user_id_list)
        normal_user = self.users[normal_user_id]

        test_user_id = self.test_user_info['user_id']

        src_msg = normal_user.send_text_msg(normal_user.user_detail[test_user_id]['conversationId'], 1, time.strftime('%Y-%m-%d %H:%M:%S'), test_user_id)

        reply_msg = normal_user.find_reply_msg_by_tag(src_msg['tag'])

        my_log('test_002[发送消息]', src_msg, reply_msg)
        time.sleep(1)
        test_user = IMUser(self.test_user_info)
        self.users[test_user_id] = test_user
        test_user.run()

        test_user.get_sync_msg()

        offline_msg_list = test_user.communication_msg[test_user.user_detail[normal_user_id]['conversationId']]

        my_log('test_002[离线消息]', '', offline_msg_list)

        assert len(offline_msg_list) > 0

        assert str(offline_msg_list[-1]['messageId']) == reply_msg['message_id']

        test_user.logout_without_save_info()    # 退出时不更新ID和时间戳
        time.sleep(5)

        # 再次上线，确保能拉到离线消息
        test_user = IMUser(self.test_user_info)
        self.users[test_user_id] = test_user
        test_user.run()

        test_user.get_sync_msg()

        new_offline_msg_list = test_user.communication_msg[test_user.user_detail[normal_user_id]['conversationId']]

        my_log('test_002[重新登录再次拉取离线消息]', '', new_offline_msg_list)

        assert new_offline_msg_list == offline_msg_list

        del_res = test_user.delete_sync_msg_by_communication(test_user.user_detail[normal_user_id]['conversationId'])
        my_log('test_002[删除会话漫游消息]', '', del_res)
        assert del_res['code'] == '0'
        test_user.logout_without_save_info()
        time.sleep(5)

        # 再次上线，确保拉不到离线消息
        test_user = IMUser(self.test_user_info)
        self.users[test_user_id] = test_user
        test_user.run()

        test_user.get_sync_msg()

        offline_msg_list = test_user.communication_msg[test_user.user_detail[normal_user_id]['conversationId']]

        my_log('test_002[重新登录再次拉取离线消息]', '', offline_msg_list)

        assert len(offline_msg_list) == 0

    @allure.title('用户退出后不保存并删除其保存的runtime信息')
    def test_003(self):
        normal_user_id = choice(self.user_id_list)
        normal_user = self.users[normal_user_id]

        test_user_id = self.test_user_info['user_id']

        src_msg = normal_user.send_text_msg(normal_user.user_detail[test_user_id]['conversationId'], 1, time.strftime('%Y-%m-%d %H:%M:%S'), test_user_id)

        reply_msg = normal_user.find_reply_msg_by_tag(src_msg['tag'])

        my_log('test_003[发送消息]', src_msg, reply_msg)
        time.sleep(1)
        test_user = IMUser(self.test_user_info)
        self.users[test_user_id] = test_user
        test_user.run()

        test_user.get_sync_msg()

        offline_msg_list = test_user.communication_msg[test_user.user_detail[normal_user_id]['conversationId']]

        my_log('test_003[离线消息]', '', offline_msg_list)

        assert len(offline_msg_list) > 0

        assert str(offline_msg_list[-1]['messageId']) == reply_msg['message_id']

        del_res = test_user.delete_sync_msg_by_user()
        my_log('test_003[删除用户漫游消息]', '', del_res)
        assert del_res['code'] == '0'
        test_user.logout_without_save_info()

        assert test_user.delete_runtime_json()

        test_user = IMUser(self.test_user_info)
        self.users[test_user_id] = test_user
        test_user.run()
        test_user.get_sync_msg()

        my_log('test_003[用户离线消息]', '', test_user.communication_msg)
        for key in test_user.communication_msg:
            assert len(test_user.communication_msg[key]) == 0

    @allure.title('用户退出后不保存并删除其保存的runtime信息,然后删除会话漫游消息重新登录拉取')
    def test_004(self):
        normal_user_id = choice(self.user_id_list)
        normal_user = self.users[normal_user_id]

        test_user_id = self.test_user_info['user_id']

        src_msg = normal_user.send_text_msg(normal_user.user_detail[test_user_id]['conversationId'], 1, time.strftime('%Y-%m-%d %H:%M:%S'), test_user_id)

        reply_msg = normal_user.find_reply_msg_by_tag(src_msg['tag'])

        my_log('test_004[发送消息]', src_msg, reply_msg)
        time.sleep(1)
        test_user = IMUser(self.test_user_info)
        self.users[test_user_id] = test_user
        test_user.run()

        test_user.get_sync_msg()

        offline_msg_list = test_user.communication_msg[test_user.user_detail[normal_user_id]['conversationId']]

        my_log('test_004[离线消息]', '', offline_msg_list)

        assert len(offline_msg_list) > 0

        assert str(offline_msg_list[-1]['messageId']) == reply_msg['message_id']

        del_res = test_user.delete_sync_msg_by_communication(test_user.user_detail[normal_user_id]['conversationId'])
        my_log('test_004[删除会话漫游消息]', test_user.user_detail[normal_user_id]['conversationId'], del_res)
        assert del_res['code'] == '0'
        test_user.logout_without_save_info()

        assert test_user.delete_runtime_json()

        test_user = IMUser(self.test_user_info)
        self.users[test_user_id] = test_user
        test_user.run()
        test_user.get_sync_msg()

        my_log('test_004[用户离线消息]', '', test_user.communication_msg)

        assert len(test_user.communication_msg[test_user.user_detail[normal_user_id]['conversationId']]) == 0


@allure.feature('测试群聊删除漫游消息')
class TestGroupDelRoamingMsg:

    users = {}
    user_id_list = []

    def setup_class(self):
        self.users = {}
        self.user_id_list = []
        all_user_info = USER_INFO[:]

        for info in all_user_info:
            user_id = info['user_id']
            self.users[user_id] = IMUser(info)
            self.users[user_id].run()
            del_res = self.users[user_id].delete_sync_msg_by_user()
            my_log('setup_method[删除用户漫游消息]', user_id, del_res)
            self.users[user_id].accept_friend_group()   # 设置自动加好友和加入群
            self.user_id_list.append(user_id)

        for user_id in self.users:
            user = self.users[user_id]
            for friend_id in self.users:
                if friend_id == user_id:
                    continue
                res = user.add_friend(friend_id)
                print(res)
        self.test_user_info = choice(all_user_info)
        self.users[self.test_user_info['user_id']].logout()
        self.user_id_list.remove(self.test_user_info['user_id'])

        group_owner_id = choice(self.user_id_list)
        self.user_id_list.remove(group_owner_id)
        self.group_owner = self.users[group_owner_id]

    def teardown_class(self):
        for user_id in self.users:
            # del_res = self.users[user_id].delete_sync_msg_by_user()
            # my_log('teardown_class[删除用户漫游消息]', user_id, del_res)
            self.users[user_id].logout()

    def setup_method(self):
        group_name = time.strftime('%Y-%m-%d %H:%M:%S')
        t = self.user_id_list[:]
        t.append(self.test_user_info['user_id'])
        create_group_res = self.group_owner.create_group(','.join(t), group_name)
        assert create_group_res['code'] == '0'
        self.group_id = create_group_res['data']['communicationId']

    def teardown_method(self):
        test_user_id = self.test_user_info['user_id']
        test_user = self.users[test_user_id]
        del_res = test_user.delete_sync_msg_by_user()
        assert del_res['code'] == '0'
        test_user.logout()
        remove_group_res = self.group_owner.remove_group(self.group_id)
        assert remove_group_res['code'] == '0'

    @allure.title('用户离线，群主拉他入群并发送消息，用户上线接收该离线消息，然后不保存信息退出再次登录拉取，不保存消息ID和时间戳退出，清除用户漫游消息再次上线')
    def test_001(self):
        time.sleep(3)
        content = time.strftime('%Y-%m-%d %H:%M:%S')
        src_msg = self.group_owner.send_text_msg(self.group_id, 2, content)
        reply_msg = self.group_owner.find_reply_msg_by_tag(src_msg['tag'])
        my_log('test_001[群主发消息]', src_msg, reply_msg)
        time.sleep(2)

        test_user_id = self.test_user_info['user_id']
        test_user = IMUser(self.test_user_info)
        self.users[test_user_id] = test_user
        test_user.run()
        test_user.get_sync_msg()

        offline_msg_list = test_user.communication_msg[self.group_id]
        my_log('test_001[离线消息]', test_user_id, offline_msg_list)
        assert len(offline_msg_list) > 0
        assert str(offline_msg_list[-1]['messageId']) == reply_msg['message_id']

        test_user.logout_without_save_info()
        time.sleep(5)

        test_user = IMUser(self.test_user_info)
        self.users[test_user_id] = test_user
        test_user.run()
        test_user.get_sync_msg()

        new_offline_msg_list = test_user.communication_msg[self.group_id]
        my_log('test_001[登录后退出不保存信息再登录再拉取离线消息]', test_user_id, new_offline_msg_list)
        assert len(new_offline_msg_list) > 0
        assert str(new_offline_msg_list[-1]['messageId']) == reply_msg['message_id']

        del_res = test_user.delete_sync_msg_by_user()
        my_log('test_001[用户清除漫游消息]', test_user_id, del_res)
        test_user.logout_without_save_info()

        test_user = IMUser(self.test_user_info)
        self.users[test_user_id] = test_user
        test_user.run()
        test_user.get_sync_msg()

        new_offline_msg_list1 = test_user.communication_msg[self.group_id]
        my_log('test_001[登录后清除漫游消息不保存信息退出再登录再拉取离线消息]', test_user_id, new_offline_msg_list1)
        assert len(new_offline_msg_list1) == 0

    # @pytest.mark.skip('')
    @allure.title('用户离线，群主拉他入群并发送消息，用户上线接收该离线消息，然后不保存信息退出再次登录拉取，不保存消息ID和时间戳退出，清除会话漫游消息再次上线')
    def test_002(self):
        time.sleep(3)
        content = time.strftime('%Y-%m-%d %H:%M:%S')
        src_msg = self.group_owner.send_text_msg(self.group_id, 2, content)
        reply_msg = self.group_owner.find_reply_msg_by_tag(src_msg['tag'])
        my_log('test_002[群主发消息]', src_msg, reply_msg)
        time.sleep(2)
        
        test_user_id = self.test_user_info['user_id']
        test_user = IMUser(self.test_user_info)
        self.users[test_user_id] = test_user
        test_user.run()
        test_user.get_sync_msg()

        offline_msg_list = test_user.communication_msg[self.group_id]
        my_log('test_002[离线消息]', test_user_id, offline_msg_list)
        assert len(offline_msg_list) > 0
        assert str(offline_msg_list[-1]['messageId']) == reply_msg['message_id']

        test_user.logout_without_save_info()
        time.sleep(5)

        test_user = IMUser(self.test_user_info)
        self.users[test_user_id] = test_user
        test_user.run()
        test_user.get_sync_msg()

        new_offline_msg_list = test_user.communication_msg[self.group_id]
        my_log('test_002[登录后退出不保存信息再登录再拉取离线消息]', test_user_id, new_offline_msg_list)
        assert len(new_offline_msg_list) > 0
        assert str(new_offline_msg_list[-1]['messageId']) == reply_msg['message_id']

        del_res = test_user.delete_sync_msg_by_communication(self.group_id)
        my_log('test_002[用户清除会话漫游消息]', self.group_id, del_res)
        test_user.logout_without_save_info()

        test_user = IMUser(self.test_user_info)
        self.users[test_user_id] = test_user
        test_user.run()
        test_user.get_sync_msg()

        new_offline_msg_list1 = test_user.communication_msg[self.group_id]
        my_log('test_002[登录后清除漫游消息不保存信息退出再登录再拉取离线消息]', test_user_id, new_offline_msg_list1)
        assert len(new_offline_msg_list1) == 0

    @allure.title('用户退出后不保存并删除其保存的runtime信息，然后清空用户漫游消息重新登录拉取')
    def test_003(self):
        time.sleep(3)
        content = time.strftime('%Y-%m-%d %H:%M:%S')
        src_msg = self.group_owner.send_text_msg(self.group_id, 2, content)
        reply_msg = self.group_owner.find_reply_msg_by_tag(src_msg['tag'])
        my_log('test_003[群主发消息]', src_msg, reply_msg)
        time.sleep(2)
        
        test_user_id = self.test_user_info['user_id']
        test_user = IMUser(self.test_user_info)
        self.users[test_user_id] = test_user
        test_user.run()
        test_user.get_sync_msg()

        offline_msg_list = test_user.communication_msg[self.group_id]
        my_log('test_003[离线消息]', test_user_id, offline_msg_list)
        assert len(offline_msg_list) > 0
        assert str(offline_msg_list[-1]['messageId']) == reply_msg['message_id']

        test_user.logout_without_save_info()
        time.sleep(5)

        test_user = IMUser(self.test_user_info)
        self.users[test_user_id] = test_user
        test_user.run()
        test_user.get_sync_msg()

        new_offline_msg_list = test_user.communication_msg[self.group_id]
        my_log('test_003[登录后退出不保存信息再登录再拉取离线消息]', test_user_id, new_offline_msg_list)
        assert len(new_offline_msg_list) > 0
        assert str(new_offline_msg_list[-1]['messageId']) == reply_msg['message_id']

        assert test_user.delete_runtime_json()
        del_res = test_user.delete_sync_msg_by_user()
        my_log('test_003[删除用户漫游消息]', '', del_res)
        assert del_res['code'] == '0'
        test_user.logout_without_save_info()
        time.sleep(5)

        test_user = IMUser(self.test_user_info)
        self.users[test_user_id] = test_user
        test_user.run()
        test_user.get_sync_msg()

        my_log('test_003[用户所有离线消息]', '', test_user.communication_msg)

        for key in test_user.communication_msg:
            assert len(test_user.communication_msg[key]) == 0

    @allure.title('用户退出后不保存并删除其保存的runtime信息，然后清空会话漫游消息重新登录拉取')
    def test_004(self):
        time.sleep(3)
        content = time.strftime('%Y-%m-%d %H:%M:%S')
        src_msg = self.group_owner.send_text_msg(self.group_id, 2, content)
        reply_msg = self.group_owner.find_reply_msg_by_tag(src_msg['tag'])
        my_log('test_004[群主发消息]', src_msg, reply_msg)
        time.sleep(2)
        
        test_user_id = self.test_user_info['user_id']
        test_user = IMUser(self.test_user_info)
        self.users[test_user_id] = test_user
        test_user.run()
        test_user.get_sync_msg()

        offline_msg_list = test_user.communication_msg[self.group_id]
        my_log('test_004[离线消息]', test_user_id, offline_msg_list)
        assert len(offline_msg_list) > 0
        assert str(offline_msg_list[-1]['messageId']) == reply_msg['message_id']

        test_user.logout_without_save_info()
        time.sleep(5)

        test_user = IMUser(self.test_user_info)
        self.users[test_user_id] = test_user
        test_user.run()
        test_user.get_sync_msg()

        new_offline_msg_list = test_user.communication_msg[self.group_id]
        my_log('test_004[登录后退出不保存信息再登录再拉取离线消息]', test_user_id, new_offline_msg_list)
        assert len(new_offline_msg_list) > 0
        assert str(new_offline_msg_list[-1]['messageId']) == reply_msg['message_id']

        assert test_user.delete_runtime_json()
        del_res = test_user.delete_sync_msg_by_communication(self.group_id)
        my_log('test_004[删除会话漫游消息]', self.group_id, del_res)
        assert del_res['code'] == '0'
        test_user.logout_without_save_info()
        time.sleep(5)

        test_user = IMUser(self.test_user_info)
        self.users[test_user_id] = test_user
        test_user.run()
        test_user.get_sync_msg()

        my_log('test_004[用户所有离线消息]', '', test_user.communication_msg)

        assert len(test_user.communication_msg[self.group_id]) == 0

    @allure.title('群聊单聊都产生离线消息，用户上线拉取后，清除会话漫游消息，不保存信息退出，再重新拉取')
    @pytest.mark.parametrize('is_delete_group, is_delete_single', [(True, True), (True, False), (False, True), (False, False)])
    def test_005(self, is_delete_group, is_delete_single):
        """
        群聊单聊都产生离线消息，用户上线拉取后，清除会话漫游消息，不保存信息退出，再重新拉取
        :param is_delete_group: 是否删除群聊漫游消息
        :param is_delete_single: 是否删除单聊漫游消息
        :return:
        """
        time.sleep(3)
        single_reply_msg_list = []
        group_reply_msg_list = []
        test_user_id = self.test_user_info['user_id']
        single_conversation_id = self.group_owner.user_detail[test_user_id]['conversationId']  # 单聊会话ID

        for i in range(100):
            content = time.strftime('%Y-%m-%d %H:%M:%S') + '---' + str(i)
            group_src_msg = self.group_owner.send_text_msg(self.group_id, 2, content)
            reply_group_msg = self.group_owner.find_reply_msg_by_tag(group_src_msg['tag'])
            my_log('test_005[群主发群聊消息]', group_src_msg, reply_group_msg)
            group_reply_msg_list.append(reply_group_msg)

            single_src_msg = self.group_owner.send_text_msg(single_conversation_id, 1, content, test_user_id)
            reply_single_msg = self.group_owner.find_reply_msg_by_tag(single_src_msg['tag'])
            my_log('test_005[群主发单聊消息]', single_src_msg, reply_single_msg)
            single_reply_msg_list.append(reply_single_msg)
            time.sleep(0.1)
        
        time.sleep(2)
        test_user = IMUser(self.test_user_info)
        self.users[test_user_id] = test_user
        test_user.run()
        test_user.get_sync_msg()

        my_log('test_005[用户离线消息]', '', test_user.communication_msg)

        assert self.group_id in test_user.communication_msg
        assert len(test_user.communication_msg[self.group_id]) >= 100

        assert single_conversation_id in test_user.communication_msg
        assert len(test_user.communication_msg[single_conversation_id]) >= 100

        index = 99
        end = -1
        while index >= 0:
            assert str(test_user.communication_msg[single_conversation_id][end]['messageId']) == single_reply_msg_list[end]['message_id']
            assert str(test_user.communication_msg[self.group_id][end]['messageId']) == group_reply_msg_list[end]['message_id']
            end -= 1
            index -= 1

        if is_delete_group:
            del_group_res = test_user.delete_sync_msg_by_communication(self.group_id)
            my_log('test_005[删除群聊会话漫游消息]', '', del_group_res)
            assert del_group_res['code'] == '0'

        if is_delete_single:
            del_single_res = test_user.delete_sync_msg_by_communication(single_conversation_id)
            my_log('test_005[删除单聊会话漫游消息]', '', del_single_res)
            assert del_single_res['code'] == '0'

        test_user.logout_without_save_info()
        time.sleep(10)

        test_user = IMUser(self.test_user_info)
        self.users[test_user_id] = test_user
        test_user.run()
        test_user.get_sync_msg()

        my_log('test_005[用户离线消息]', '', test_user.communication_msg)

        if is_delete_group:
            assert self.group_id not in test_user.communication_msg or len(test_user.communication_msg[self.group_id]) == 0
        else:
            assert self.group_id in test_user.communication_msg
            assert len(test_user.communication_msg[self.group_id]) >= 100

        if is_delete_single:
            assert single_conversation_id not in test_user.communication_msg or len(test_user.communication_msg[single_conversation_id]) == 0
        else:
            assert single_conversation_id in test_user.communication_msg
            assert len(test_user.communication_msg[single_conversation_id]) >= 100

        index = 99
        end = -1
        while index >= 0:
            if not is_delete_group:
                assert str(test_user.communication_msg[self.group_id][end]['messageId']) == group_reply_msg_list[end]['message_id']
            if not is_delete_single:
                assert str(test_user.communication_msg[single_conversation_id][end]['messageId']) == single_reply_msg_list[end]['message_id']
            end -= 1
            index -= 1
