import time
from random import choice

import pytest
import allure

from lib.im_socket_lib.sync_im_user import IMUser
from common.my_log import my_log


from config.conf import USER_INFO


@allure.feature('聊天室白名单测试')
class TestChatRoomWhileList:

    users = None
    user_id_list = None

    def setup_class(self):
        self.users = {}
        self.user_id_list = []
        for info in USER_INFO[:]:
            user_id = info['user_id']
            self.user_id_list.append(user_id)
            self.users[user_id] = IMUser(info)
            self.users[user_id].run()

    def teardown_class(self):
        for k, v in self.users.items():
            v.logout()

    def setup_method(self):
        member_list = self.user_id_list[:]
        chat_room_owner_id = choice(member_list)
        member_list.remove(chat_room_owner_id)
        self.member_list = member_list
        self.chat_room_owner = self.users[chat_room_owner_id]
        create_room_res = self.chat_room_owner.create_chat_room()
        assert create_room_res['code'] == '0', create_room_res
        self.chat_room_id = create_room_res['data']['communicationId']
        for user_id in self.users:
            self.users[user_id].enter_chat_room(self.chat_room_id)

    def teardown_method(self):
        self.chat_room_owner.remove_chat_room(self.chat_room_id)
        for user_id in self.users:
            self.users[user_id].clean_msg()

    @allure.title('设置白名单')
    @pytest.mark.parametrize('who_set, set_who', [(i, j) for i in range(6) for j in range(6)])
    def test_001(self, who_set, set_who):
        """
        设置白名单
        :param who_set: 谁设置, 0-室主，1-管理员，2-普通成员，3-黑名单用户， 4-禁言用户，5-非聊天室成员
        :param set_who: 设置谁 ,0-室主，1-管理员，2-普通成员，3-黑名单用户， 4-禁言用户，5-非聊天室成员
        :return:
        """
        identity = {
            0: '室主',
            1: '管理员',
            2: '普通成员',
            3: '黑名单用户',
            4: '禁言用户',
            5: '非聊天室成员'
        }

        print(f'{identity[who_set]}设置{identity[set_who]}到白名单')
        if who_set in (0, 1) and set_who == 3:
            return
        if who_set == 0:
            current_user = self.chat_room_owner
        elif who_set == 1:
            manager_id = self.member_list.pop()
            set_manager_res = self.chat_room_owner.set_chat_room_manager(self.chat_room_id, manager_id, 'add')
            my_log('test_001[设置管理员]', manager_id, set_manager_res)
            assert set_manager_res['code'] == '0'
            manager_list_res = self.chat_room_owner.get_chat_room_manager_list(self.chat_room_id)
            my_log('test_001[管理员列表]', '', manager_list_res)
            assert manager_list_res['code'] == '0'
            assert manager_id in [info['userId'] for info in manager_list_res['data']]
            current_user = self.users[manager_id]
        elif who_set == 2:
            normal_id = self.member_list.pop()
            current_user = self.users[normal_id]
        elif who_set == 3:
            black_id = self.member_list.pop()
            set_black_list_res = self.chat_room_owner.set_chat_room_black_list(self.chat_room_id, black_id, 'add')
            my_log('test_001[设置黑名单]', black_id, set_black_list_res)
            black_list_res = self.chat_room_owner.get_chat_room_black_list(self.chat_room_id)
            my_log('test_001[黑名单列表]', '', black_list_res)
            assert black_list_res['code'] == '0'
            assert black_id in [info['userId'] for info in black_list_res['data']]
            current_user = self.users[black_id]
        elif who_set == 4:
            mute_id = self.member_list.pop()
            set_mute_res = self.chat_room_owner.set_chat_room_mute(self.chat_room_id, mute_id, 'add')
            assert set_mute_res['code'] == '0'
            my_log('test_001[设置禁言列表]', mute_id, set_mute_res)
            mute_list_res = self.chat_room_owner.get_chat_room_mute_list(self.chat_room_id)
            assert mute_list_res['code'] == '0'
            my_log('test_001[禁言列表]', '', mute_list_res)
            assert mute_id in [info['userId'] for info in mute_list_res['data']]
            current_user = self.users[mute_id]
        elif who_set == 5:
            normal_id = self.member_list.pop()
            current_user = self.users[normal_id]
            exit_res = current_user.exit_chat_room(self.chat_room_id)
            assert exit_res['code'] == '0'
        else:
            raise Exception(f'未知用户身份: {who_set}')

        if set_who == 0:
            dst_id = self.chat_room_owner.user_info['user_id']
        elif set_who == 1:
            dst_id = self.member_list.pop()
            set_manager_res = self.chat_room_owner.set_chat_room_manager(self.chat_room_id, dst_id, 'add')
            my_log('test_001[设置管理员]', dst_id, set_manager_res)
            assert set_manager_res['code'] == '0'
            manager_list_res = self.chat_room_owner.get_chat_room_manager_list(self.chat_room_id)
            my_log('test_001[管理员列表]', '', manager_list_res)
            assert manager_list_res['code'] == '0'
            assert dst_id in [info['userId'] for info in manager_list_res['data']]
        elif set_who == 2:
            dst_id = self.member_list.pop()
        elif set_who == 3:
            dst_id = self.member_list.pop()
            set_black_list_res = self.chat_room_owner.set_chat_room_black_list(self.chat_room_id, dst_id, 'add')
            assert set_black_list_res['code'] == '0'
            my_log('test_001[设置黑名单]', dst_id, set_black_list_res)
            black_list_res = self.chat_room_owner.get_chat_room_black_list(self.chat_room_id)
            my_log('test_001[黑名单列表]', '', black_list_res)
            assert black_list_res['code'] == '0'
            assert dst_id in [info['userId'] for info in black_list_res['data']]
        elif set_who == 4:
            dst_id = self.member_list.pop()
            set_mute_res = self.chat_room_owner.set_chat_room_mute(self.chat_room_id, dst_id, 'add')
            assert set_mute_res['code'] == '0'
            my_log('test_001[设置禁言列表]', dst_id, set_mute_res)
            mute_list_res = self.chat_room_owner.get_chat_room_mute_list(self.chat_room_id)
            assert mute_list_res['code'] == '0'
            my_log('test_001[禁言列表]', '', mute_list_res)
            assert mute_list_res['code'] == '0'
            assert dst_id in [info['userId'] for info in mute_list_res['data']]
        elif set_who == 5:
            dst_id = self.member_list.pop()
            exit_res = self.users[dst_id].exit_chat_room(self.chat_room_id)
            my_log('test_001[退出聊天室]', dst_id, exit_res)
            assert exit_res['code'] == '0'
        else:
            raise Exception(f'未知用户身份: {set_who}')

        time.sleep(1)

        set_white_list_res = current_user.set_chat_room_white_list(self.chat_room_id, dst_id, 'add')
        my_log(f'test_001[{identity[who_set]}设置{identity[set_who]}到白名单]', '', set_white_list_res)

        if who_set in (0, 1) and set_who in (2, 3, 4):
            assert set_white_list_res['code'] == '0'
            white_list_res = self.chat_room_owner.get_chat_room_white_list(self.chat_room_id)
            my_log('test_001[白名单列表]', '', white_list_res)
            assert white_list_res['code'] == '0'
            assert dst_id in [info['userId'] for info in white_list_res['data']]
        else:

            if who_set in (0, 1) and set_who == 0:
                assert set_white_list_res['code'] == '1' and 'error' in set_white_list_res
                assert set_white_list_res['error']['code'] == 1671 and set_white_list_res['error']['message'] == '聊天室拥有者不能被操作'
            elif who_set in (0, 1) and set_who == 1:
                assert set_white_list_res['code'] == '1' and 'error' in set_white_list_res
                assert set_white_list_res['error']['code'] == 1673 and set_white_list_res['error']['message'] == '聊天室管理员不能添加进来'
            elif who_set in (0, 1) and set_who == 5:
                # todo 设置非聊天室成员到白名单断言
                assert set_white_list_res['code'] == '0'    # 服务端对不在聊天室的ID不做处理，因此正常返回
            else:
                assert set_white_list_res['code'] == '1' and 'error' in set_white_list_res
                assert set_white_list_res['error']['code'] == 1654 and set_white_list_res['error']['message'] == '没有权限进行该操作'
            white_list_res = self.chat_room_owner.get_chat_room_white_list(self.chat_room_id)
            my_log('test_001[白名单列表]', '', white_list_res)
            assert white_list_res['code'] == '0'
            assert dst_id not in [info['userId'] for info in white_list_res['data']]

    @allure.title('将禁言用户设置到白名单')
    def test_002(self):
        mute_id = self.member_list.pop()
        set_mute_res = self.chat_room_owner.set_chat_room_mute(self.chat_room_id, mute_id, 'add')
        assert set_mute_res['code'] == '0'
        my_log('test_002[设置禁言列表]', mute_id, set_mute_res)
        mute_list_res = self.chat_room_owner.get_chat_room_mute_list(self.chat_room_id)
        assert mute_list_res['code'] == '0'
        my_log('test_002[禁言列表]', '', mute_list_res)
        assert mute_id in [info['userId'] for info in mute_list_res['data']]

        mute_user = self.users[mute_id]

        src_msg = mute_user.send_text_msg(self.chat_room_id, 3, 'hello')
        reply_msg = mute_user.find_reply_msg_by_tag(src_msg['tag'])
        my_log('test_002[禁言用户发送消息]', src_msg, reply_msg)
        assert 'resp' in reply_msg and reply_msg['resp'] == {'ret': 1617, 'errorCode': '已被禁言'}

        set_white_list_res = self.chat_room_owner.set_chat_room_white_list(self.chat_room_id, mute_id, 'add')
        my_log('test_002[设置禁言用户到白名单]', mute_id, set_white_list_res)
        assert set_white_list_res['code'] == '0'
        """
        断言用户在白名单中
        """
        white_list_res = self.chat_room_owner.get_chat_room_white_list(self.chat_room_id)
        my_log('test_002[白名单列表]', '', white_list_res)
        assert white_list_res['code'] == '0'
        assert mute_id in [info['userId'] for info in white_list_res['data']]

        """
        断言用户不在禁言名单中
        """
        mute_list_res = self.chat_room_owner.get_chat_room_mute_list(self.chat_room_id)
        assert mute_list_res['code'] == '0'
        my_log('test_002[禁言列表]', '', mute_list_res)
        assert mute_id not in [info['userId'] for info in mute_list_res['data']]

        content = 'hello world'
        src_msg = mute_user.send_text_msg(self.chat_room_id, 3, content)
        reply_msg = mute_user.find_reply_msg_by_tag(src_msg['tag'])
        my_log('test_002[白名单用户发送消息]', src_msg, reply_msg)
        assert 'resp' in reply_msg and reply_msg['resp'] == {}

        for user_id in self.users:
            if user_id == mute_id:
                continue
            dst_msg = self.users[user_id].find_communication_msg_by_id(self.chat_room_id, reply_msg['message_id'])
            my_log('test_002[接受方收到聊天室消息]', user_id, dst_msg)
            assert dst_msg is not None
            assert dst_msg['app_id'] == src_msg['app_id']
            assert dst_msg['content'] == content
            assert 'msg_file' not in dst_msg or dst_msg['msg_file'] == {}
            assert dst_msg['from_user_id'] == mute_id
            assert dst_msg['communication_id'] == self.chat_room_id
            assert dst_msg['tag'] == src_msg['tag']
            assert dst_msg['communication_type'] == src_msg['communication_type']
            assert dst_msg['message_type'] == src_msg['message_type']
            assert dst_msg['message_main_type'] == src_msg['message_main_type']
            assert dst_msg['other'] == src_msg['other']
            assert dst_msg['send_time'] == reply_msg['send_time']
            assert dst_msg['communication_show'] is True

    @allure.title('开启全员禁言，然后设置白名单，然后白名单用户发言,然后再移除白名单用户，然后该用户再发言')
    def test_003(self):
        """
        开启全员禁言，然后设置白名单，然后白名单用户发言,然后再移除白名单用户，然后该用户再发言
        :return:
        """
        normal_id = self.member_list.pop()
        normal_user = self.users[normal_id]

        set_all_mute_res = self.chat_room_owner.set_chat_room_all_mute(self.chat_room_id, True)
        my_log('test_003[设置全员禁言]', True, set_all_mute_res)
        assert set_all_mute_res['code'] == '0'

        src_msg = normal_user.send_text_msg(self.chat_room_id, 3, 'hello')
        reply_msg = normal_user.find_reply_msg_by_tag(src_msg['tag'])
        my_log('test_003[普通用户发送消息]', src_msg, reply_msg)
        assert 'resp' in reply_msg and reply_msg['resp'] == {'ret': 1617, 'errorCode': '已被禁言'}

        set_white_list_res = self.chat_room_owner.set_chat_room_white_list(self.chat_room_id, normal_id, 'add')
        my_log('test_003[设置普通用户到白名单]', normal_id, set_white_list_res)
        assert set_white_list_res['code'] == '0'
        """
        断言用户在白名单中
        """
        white_list_res = self.chat_room_owner.get_chat_room_white_list(self.chat_room_id)
        my_log('test_003[白名单列表]', '', white_list_res)
        assert white_list_res['code'] == '0'
        assert normal_id in [info['userId'] for info in white_list_res['data']]

        content = 'hello world'
        src_msg = normal_user.send_text_msg(self.chat_room_id, 3, content)
        reply_msg = normal_user.find_reply_msg_by_tag(src_msg['tag'])
        my_log('test_003[白名单用户发送消息]', src_msg, reply_msg)
        assert 'resp' in reply_msg and reply_msg['resp'] == {}

        for user_id in self.users:
            if user_id == normal_id:
                continue
            dst_msg = self.users[user_id].find_communication_msg_by_id(self.chat_room_id, reply_msg['message_id'])
            my_log('test_003[接受方收到聊天室消息]', user_id, dst_msg)
            assert dst_msg is not None
            assert dst_msg['app_id'] == src_msg['app_id']
            assert dst_msg['content'] == content
            assert 'msg_file' not in dst_msg or dst_msg['msg_file'] == {}
            assert dst_msg['from_user_id'] == normal_id
            assert dst_msg['communication_id'] == self.chat_room_id
            assert dst_msg['tag'] == src_msg['tag']
            assert dst_msg['communication_type'] == src_msg['communication_type']
            assert dst_msg['message_type'] == src_msg['message_type']
            assert dst_msg['message_main_type'] == src_msg['message_main_type']
            assert dst_msg['other'] == src_msg['other']
            assert dst_msg['send_time'] == reply_msg['send_time']
            assert dst_msg['communication_show'] is True

        del_white_list_res = self.chat_room_owner.set_chat_room_white_list(self.chat_room_id, normal_id, 'remove')
        my_log('test_003[将用户从白名单移除]', normal_id, del_white_list_res)
        assert del_white_list_res['code'] == '0'

        white_list_res = self.chat_room_owner.get_chat_room_white_list(self.chat_room_id)
        my_log('test_003[白名单列表]', '', white_list_res)
        assert white_list_res['code'] == '0'
        assert normal_id not in [info['userId'] for info in white_list_res['data']]

        src_msg = normal_user.send_text_msg(self.chat_room_id, 3, 'hello')
        reply_msg = normal_user.find_reply_msg_by_tag(src_msg['tag'])
        my_log('test_003[普通用户发送消息]', src_msg, reply_msg)
        assert 'resp' in reply_msg and reply_msg['resp'] == {'ret': 1617, 'errorCode': '已被禁言'}

    @allure.title('将白名单用户设置为管理员、黑名单、禁言')
    @pytest.mark.parametrize('set_to', [1, 3, 4])
    def test_004(self, set_to):
        """
        将白名单用户设置为管理员、黑名单、禁言
        :param set_to: 1-管理员，3-黑名单，4-禁言
        :return:
        """
        normal_id = self.member_list.pop()
        normal_user = self.users[normal_id]

        set_white_list_res = self.chat_room_owner.set_chat_room_white_list(self.chat_room_id, normal_id, 'add')
        my_log('test_004[设置普通用户到白名单]', normal_id, set_white_list_res)
        assert set_white_list_res['code'] == '0'
        """
        断言用户在白名单中
        """
        white_list_res = self.chat_room_owner.get_chat_room_white_list(self.chat_room_id)
        my_log('test_004[白名单列表]', '', white_list_res)
        assert white_list_res['code'] == '0'
        assert normal_id in [info['userId'] for info in white_list_res['data']]

        if set_to == 1:
            set_manager_res = self.chat_room_owner.set_chat_room_manager(self.chat_room_id, normal_id, 'add')
            my_log('test_004[设置管理员]', normal_id, set_manager_res)
            assert set_manager_res['code'] == '0'
            manager_list_res = self.chat_room_owner.get_chat_room_manager_list(self.chat_room_id)
            my_log('test_004[管理员列表]', '', manager_list_res)
            assert manager_list_res['code'] == '0'
            assert normal_id in [info['userId'] for info in manager_list_res['data']]
        elif set_to == 3:
            set_black_list_res = self.chat_room_owner.set_chat_room_black_list(self.chat_room_id, normal_id, 'add')
            assert set_black_list_res['code'] == '0'
            my_log('test_004[设置黑名单]', normal_id, set_black_list_res)
            black_list_res = self.chat_room_owner.get_chat_room_black_list(self.chat_room_id)
            my_log('test_004[黑名单列表]', '', black_list_res)
            assert black_list_res['code'] == '0'
            assert normal_id in [info['userId'] for info in black_list_res['data']]
        elif set_to == 4:
            set_mute_res = self.chat_room_owner.set_chat_room_mute(self.chat_room_id, normal_id, 'add')
            assert set_mute_res['code'] == '0'
            my_log('test_004[设置禁言列表]', normal_id, set_mute_res)
            mute_list_res = self.chat_room_owner.get_chat_room_mute_list(self.chat_room_id)
            assert mute_list_res['code'] == '0'
            my_log('test_004[禁言列表]', '', mute_list_res)
            assert mute_list_res['code'] == '0'
            assert normal_id in [info['userId'] for info in mute_list_res['data']]
        else:
            raise Exception('未知用户身份')

        white_list_res = self.chat_room_owner.get_chat_room_white_list(self.chat_room_id)
        my_log('test_004[白名单列表]', '', white_list_res)
        assert white_list_res['code'] == '0'
        assert normal_id not in [info['userId'] for info in white_list_res['data']]

    @allure.title('白名单用户退出聊天室再重新进入')
    def test_005(self):
        normal_id = self.member_list.pop()
        normal_user = self.users[normal_id]

        set_white_list_res = self.chat_room_owner.set_chat_room_white_list(self.chat_room_id, normal_id, 'add')
        my_log('test_005[设置普通用户到白名单]', normal_id, set_white_list_res)
        assert set_white_list_res['code'] == '0'
        """
        断言用户在白名单中
        """
        white_list_res = self.chat_room_owner.get_chat_room_white_list(self.chat_room_id)
        my_log('test_005[白名单列表]', '', white_list_res)
        assert white_list_res['code'] == '0'
        assert normal_id in [info['userId'] for info in white_list_res['data']]

        exit_res = normal_user.exit_chat_room(self.chat_room_id)
        my_log('test_005[白名单用户退出聊天室]', '', exit_res)
        assert exit_res['code'] == '0'

        white_list_res = self.chat_room_owner.get_chat_room_white_list(self.chat_room_id)
        my_log('test_005[白名单列表]', '', white_list_res)
        assert white_list_res['code'] == '0'
        assert normal_id in [info['userId'] for info in white_list_res['data']]

        enter_res = normal_user.enter_chat_room(self.chat_room_id)
        my_log('test_005[白名单用户进入聊天室]', '', enter_res)
        assert enter_res['code'] == '0'

        white_list_res = self.chat_room_owner.get_chat_room_white_list(self.chat_room_id)
        my_log('test_005[白名单列表]', '', white_list_res)
        assert white_list_res['code'] == '0'
        assert normal_id in [info['userId'] for info in white_list_res['data']]

    @allure.title('将禁言用户设置白名单')
    @pytest.mark.parametrize('set_who_to_white_list', [4])
    def test_006(self, set_who_to_white_list):
        """
        将禁言用户设置白名单
        :param set_who_to_white_list: 将谁设置为白名单
        :return:
        """
        normal_id = self.member_list.pop()
        normal_user = self.users[normal_id]

        if set_who_to_white_list == 3:
            set_black_list_res = self.chat_room_owner.set_chat_room_black_list(self.chat_room_id, normal_id, 'add')
            assert set_black_list_res['code'] == '0'
            my_log('test_006[设置黑名单]', normal_id, set_black_list_res)
            black_list_res = self.chat_room_owner.get_chat_room_black_list(self.chat_room_id)
            my_log('test_006[黑名单列表]', '', black_list_res)
            assert black_list_res['code'] == '0'
            assert normal_id in [info['userId'] for info in black_list_res['data']]
        elif set_who_to_white_list == 4:
            set_mute_res = self.chat_room_owner.set_chat_room_mute(self.chat_room_id, normal_id, 'add')
            assert set_mute_res['code'] == '0'
            my_log('test_006[设置禁言列表]', normal_id, set_mute_res)
            mute_list_res = self.chat_room_owner.get_chat_room_mute_list(self.chat_room_id)
            assert mute_list_res['code'] == '0'
            my_log('test_006[禁言列表]', '', mute_list_res)
            assert mute_list_res['code'] == '0'
            assert normal_id in [info['userId'] for info in mute_list_res['data']]
        else:
            raise Exception('未知用户身份')

        set_white_list_res = self.chat_room_owner.set_chat_room_white_list(self.chat_room_id, normal_id, 'add')
        my_log('test_006[设置普通用户到白名单]', normal_id, set_white_list_res)
        assert set_white_list_res['code'] == '0'
        """
        断言用户在白名单中
        """
        white_list_res = self.chat_room_owner.get_chat_room_white_list(self.chat_room_id)
        my_log('test_006[白名单列表]', '', white_list_res)
        assert white_list_res['code'] == '0'
        assert normal_id in [info['userId'] for info in white_list_res['data']]

        if set_who_to_white_list == 3:
            black_list_res = self.chat_room_owner.get_chat_room_black_list(self.chat_room_id)
            my_log('test_006[黑名单列表]', '', black_list_res)
            assert black_list_res['code'] == '0'
            assert normal_id not in [info['userId'] for info in black_list_res['data']]
        elif set_who_to_white_list == 4:
            mute_list_res = self.chat_room_owner.get_chat_room_mute_list(self.chat_room_id)
            assert mute_list_res['code'] == '0'
            my_log('test_006[禁言列表]', '', mute_list_res)
            assert mute_list_res['code'] == '0'
            assert normal_id not in [info['userId'] for info in mute_list_res['data']]
