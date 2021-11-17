import os
from threading import Thread, Lock
from collections import defaultdict, deque
from random import randint
import socket
import json

from .sdk_api import *
from .utils.generator import device_info_gen
from .message import get_bind_message, get_communication_message_by_group, get_communication_message_by_single, decode_communication_message, get_msg_ack_message, get_msg_read_message, get_heartbeat_message, get_communication_message_by_chat_room
from .utils.packer import msg_unpack_length_and_command


def get_reply_msg(msg):
    reply_msg = msg.replace('吗', '')
    reply_msg = reply_msg.replace('是不是', '是')
    reply_msg = reply_msg.replace('?', '!')
    reply_msg = reply_msg.replace('我', '你')
    return reply_msg


def get_src_body(buffer) -> tuple:
    """
    根据编码后的body获取原始的proto_name和proto_body
    @param buffer:
    @return: tuple: proto_name, proto_body
    """
    buffer = buffer[5:]
    key_len = buffer[0]
    _ = buffer[1: 1 + key_len]
    proto_name_len = buffer[1 + key_len]
    proto_name = buffer[2 + key_len: 2 + key_len + proto_name_len]
    proto_body = buffer[2 + key_len + proto_name_len:]
    return proto_name, proto_body


class IMUser:

    DEBUG = False

    INFO = False

    def __init__(self, user_info: dict, device_type='ios'):
        self.address = None    # im服务器地址
        self.exit = False   # 退出flag
        self.user_info = user_info  # 用户信息
        self.user_id = user_info['user_id']
        self.token = None
        self.phone = None
        self.demo_token = None
        self.device_type = device_type
        self.device_info = device_info_gen(device_type)  # 初始化设备信息
        self.key = ';'.join([self.user_info['app_id'], self.user_info['user_id'], self.device_info['device_id']])

        self.start = False  # start flag
        self.header_beat_time = 2  # 心跳间隔
        self.communication_info = defaultdict(dict)    # 存放会话信息
        self.communication_msg = defaultdict(deque)     # 存放会话消息,comm_id => msg_list []
        self.reply_command_send_msg_req = []    # 存放reply_command_send_msg_req
        self.already_destroy_comm_id_set = set()    # 存储已经被销毁(解散)的会话ID
        self.last_msg_sequence_id = 0
        self.last_msg_receive_time = ''
        self.commid_to_user_id_dict = {}  # 单聊会话id对应的user_id

        self.is_login = False
        self.last_send_heartbeat_time = 0
        self.last_send_seq_id = -1
        self.last_msg_seq_json_path = 'runtime/' + self.user_info['user_id'] + '.json'
        self.lock = Lock()

        self.err_msg = None
        self.user_id_to_nickname = {}   # 用户id对应的详细信息
        self.friend_id_list = []    # 存放好友id的列表
        self.user_detail = {}           # 存放用户信息
        self.group_info = {}  # 存放群聊信息
        self.group_id_list = []  # 存放群id列表
        self.head_photo_bytes = b''    # 存放自己的头像 (二进制)
        self.send_msg_details = {
            'communication_type': {},
            'message_type': {},
            'communication_id': {}
        }  # 用来统计发送消息详情

        self.cost = []  # 统计消息延时等
        self.sock = socket.socket()
        self.other = ''  # 用户扩展信息

    def __repr__(self):
        return f'<user_id: {self.user_id}, device_type: {self.device_type}>' + super().__repr__()

    def debug(self, *args, **kw):
        if self.DEBUG:
            print('[{}] [new_im_user.py]'.format(time.strftime('%Y-%m-%d %H:%M:%S')), *args, **kw)

    def info(self, *args, **kw):
        if self.INFO:
            print('[{}] [new_im_user.py]'.format(time.strftime('%Y-%m-%d %H:%M:%S')), *args, **kw)

    def enter_chat_room(self, chat_room_id):
        self.debug('[enter_chat_room]')
        res = chat_room_enter(self.token, chat_room_id)
        return res

    def exit_chat_room(self, chat_room_id):
        self.debug('[exit_chat_room]')
        # del self.chat_room_msg[chat_room_id]
        res = chat_room_exit(self.token, chat_room_id)
        return res

    def login(self):
        """
        用户接口登录，返回token
        :return: token
        """
        try:
            login_res = login_by_sdk(self.user_info, self.device_info)
        except Exception as _e:
            self.debug('[login]', _e)
            raise Exception('服务器登陆失败: '+str(_e))
        else:

            if 'code' in login_res and login_res['code'] == '0':
                self.token = login_res['data']['access_token']
                self.debug('[login]', login_res)
                self.address = (login_res['data']['im_module']['server_addr'], login_res['data']['im_module']['socket_port'])
                self.get_user_detail()
                return login_res
            else:
                raise Exception('服务器登陆失败!', login_res)

    def get_group_name(self, group_id):
        if group_id not in self.group_info:
            _r = get_group_detail(self.token, group_id)
            self.debug('[get_group_name]', _r)
            if _r['code'] == '0':
                self.group_info[group_id] = {
                    'name': _r['data']['name'],
                    'ownerId': _r['data']['ownerId']
                }
            else:
                self.group_info[group_id] = {
                    'name': '',
                    'ownerId': ''
                }
        return self.group_info[group_id]['name']

    def get_group_detail(self, group_id):
        _r = get_group_detail(self.token, group_id)
        self.debug('[get_group_detail]', _r)
        return _r

    def find_reply_msg_by_tag(self, tag):
        """
        根据源消息的tag，从reply_command_send_msg_req中找到对应的reply_msg并返回
        超时时间20秒，找不到则返回为空
        :param tag: 消息tag
        :return: msg or None
        """
        retry_times = 0
        while retry_times < 100:
            if len(self.reply_command_send_msg_req) > 0 and self.reply_command_send_msg_req[-1]['tag'] == tag:
                break
            else:
                time.sleep(0.2)
                retry_times += 1
        if len(self.reply_command_send_msg_req) == 0 or self.reply_command_send_msg_req[-1]['tag'] != tag:
            return None
        return self.reply_command_send_msg_req.pop()

    def find_communication_msg_by_id(self, communication_id, msg_id):
        """
        给定communication_id和msg_id,从该会话消息中找到msg_id相等的消息
        超时时间20秒，找不到则返回为空
        :param communication_id:会话id
        :param msg_id: 消息id
        :return: msg or None
        """
        retry_times = 0
        while retry_times < 100:
            if len(self.communication_msg[communication_id]) == 0 or 'message_id' not in self.communication_msg[communication_id][-1] or self.communication_msg[communication_id][-1]['message_id'] != msg_id:
                retry_times += 1
                time.sleep(0.2)
            else:
                return self.communication_msg[communication_id].pop()
        return None

    def find_communication_msg_by_msg_main_type(self, communication_id, message_main_type):
        """
        给定communication_id和message_main_type,从该会话消息中找到消息
        超时时间20秒，找不到则返回为空
        :param communication_id:
        :param message_main_type:
        :return: msg or None
        """
        retry_times = 0
        while retry_times < 100:
            if len(self.communication_msg[communication_id]) == 0 or 'message_main_type' not in self.communication_msg[communication_id][-1] or self.communication_msg[communication_id][-1]['message_main_type'] != message_main_type:
                retry_times += 1
                time.sleep(0.2)
            else:
                return self.communication_msg[communication_id].pop()
        return None

    def clean_msg(self):
        """
        清空用户的会话消息和reply 消息
        :return: None
        """
        self.communication_info = defaultdict(dict)    # 存放会话信息
        self.communication_msg = defaultdict(deque)     # 存放会话消息,comm_id => msg_list []
        self.reply_command_send_msg_req = []    # 存放reply_command_send_msg_req

    def get_nickname(self, user_id):
        # self.debug('[get_nickname]')
        if user_id not in self.user_id_to_nickname:
            _r = self.get_user_detail(user_id)
            self.user_id_to_nickname[user_id] = dict()
            self.user_id_to_nickname[user_id]['nickname'] = _r['data']['nickname'] if _r['data']['nickname'] is not None else '匿名用户'
            self.user_id_to_nickname[user_id]['last_update_time'] = time.time()
        elif time.time() - self.user_id_to_nickname[user_id]['last_update_time'] > 3600:
            _r = self.get_user_detail(user_id)
            self.user_id_to_nickname[user_id]['nickname'] = _r['data']['nickname'] if _r['data']['nickname'] is not None else '匿名用户'
            self.user_id_to_nickname[user_id]['last_update_time'] = time.time()
        return self.user_id_to_nickname[user_id]['nickname']

    def get_friend_communication(self, user_id):
        return self.user_id_to_nickname[user_id]['communication_id']

    def get_user_detail_by_multi(self, user_id_list):
        dst_id_list = []
        for _id in user_id_list:
            if _id not in self.user_id_to_nickname:
                dst_id_list.append(_id)
        if len(dst_id_list) == 0:
            return
        step = 100
        start = 0
        while 1:
            tmp = dst_id_list[start: start+step]
            if len(tmp) == 0:
                break
            start += step
            try:
                _res = get_user_detail_by_multi(self.token, ','.join(tmp))
            except Exception as _e:
                print(_e)
                raise Exception(_e)
            else:
                if 'code' in _res and _res['code'] == '0':
                    for user_info in _res['data']:
                        # print(user_info)
                        user_id = user_info['userId']
                        self.user_id_to_nickname[user_id] = dict()
                        self.user_id_to_nickname[user_id]['nickname'] = user_info['nickname'] if user_info['nickname'] is not None else '匿名用户'
                        self.user_id_to_nickname[user_id]['last_update_time'] = time.time()
                else:
                    print(_res)
                    raise Exception(_res['code'])

    def get_user_detail(self, user_id=None):
        self.debug('[get_user_detail]', user_id)
        if user_id is None:
            user_id = self.user_info['user_id']
        _r = get_user_detail(self.token, user_id)
        return _r

    def get_user_head_photo_bytes(self, user_id=None):
        self.debug('[get_user_head_photo_bytes]')
        if user_id is None or user_id == self.user_info['user_id']:
            if self.head_photo_bytes != b'':
                return self.head_photo_bytes
        _res = self.get_user_detail(user_id)
        if _res['data']['avatar'] is not None and _res['data']['avatar'] != '':
            _r = requests.get(_res['data']['avatar'])
            if _r.status_code == 200:
                if user_id is None or user_id == self.user_info['user_id']:
                    self.head_photo_bytes = _r.content
                return _r.content
        return None

    def get_chat_room_list_by_type(self, chat_room_type, create_time=None):
        """
        获取聊天室列表
        :param chat_room_type: 0:公开聊天室列表;1:个人聊天室列表
        :param create_time: 创建时间
        :return:
        """
        self.debug('[get_chat_room_list_by_type]')
        if chat_room_type == 0:
            _res = chat_room_list_public(self.token, create_time=create_time)
        elif chat_room_type == 1:
            _res = chat_room_list_mine(self.token)
        else:
            raise Exception(f'unknow chat_room_type {chat_room_type}')
        return _res

    def get_chat_room_member_list(self, chat_room_id, create_time=None):
        self.debug('[get_chat_room_member_list]')
        res = chat_room_member_list(self.token, chat_room_id, create_time)
        return res
        
    def get_chat_room_announcement(self, chat_room_id):
        self.debug('[get_chat_room_announcement]')
        res = chat_room_announcement_get(self.token, chat_room_id)
        return res

    def get_chat_room_description(self, chat_room_id):
        self.debug('[get_chat_room_description]')
        res = self.get_chat_room_detail(chat_room_id)
        return res['data']['description']

    def get_chat_room_black_list(self, chat_room_id):
        self.debug('[get_chat_room_black_list]')
        res = chat_room_black_list(self.token, chat_room_id)
        return res

    def get_chat_room_manager_list(self, chat_room_id):
        self.debug('[get_chat_room_manager_list]')
        res = chat_room_manager_list(self.token, chat_room_id)
        return res

    def get_chat_room_white_list(self, chat_room_id):
        self.debug('[get_chat_room_white_list]')
        res = chat_room_user_mute_white_list(self.token, chat_room_id)
        return res

    def get_chat_room_mute_list(self, chat_room_id):
        self.debug('[get_chat_room_mute_list]')
        res = chat_room_user_multi_list(self.token, chat_room_id)
        return res

    def set_group_allow_invite(self, group_id, allow_invite_flag):  # 群设置，是否允许群成员邀请他人入群
        _r = set_group_allow_invite(self.token, group_id, allow_invite_flag)
        return _r

    def set_group_name(self, group_id, group_name):
        _r = update_group_name(self.token, group_id, group_name)
        return _r

    def set_group_join_apply(self, group_id, need_apply_flag):  # 群设置入群许可,入群需要群主或管理员同意
        _r = set_group_join_apply(self.token, group_id, need_apply_flag)
        return _r

    def set_user_baseinfo(self, **kw):
        """
        设置用户基础信息
        @param kw:
            avatar	头像，注意是图片地址
            birthDay	string(date-time)
            email	邮箱	string
            nickname	昵称	string
            phone	手机	string
            sex	性别1=male, 2=female integer(int32)
            signInfo	签名
        @return:
        """
        _r = set_user_baseinfo(self.token, **kw)
        return _r

    def change_group_owner(self, group_id, new_owner_id):   # 更改群主
        _r = change_group_owner(self.token, group_id, new_owner_id)
        if _r['code'] == '0':
            pass
            self.group_info[group_id]['ownerId'] = new_owner_id
        return _r

    def build_connection(self):
        try:
            self.sock.connect(self.address)
        except Exception as _e:
            self.err_msg = str(_e)
            raise Exception('connect host error') from _e
        else:
            self.debug('[build_connection] self.token: ', self.token)
            if not self.token:
                return
            msg = get_bind_message(self.token, self.key, self.user_info, self.device_info)
            self.debug('[build_connection] bind_message: ', msg)
            self.start = True
            self.sock.send(msg)
            while not self.is_login:
                time.sleep(0.1)

    def update_friend_list(self):
        self.debug('[update_friend_list]')
        _r = self.get_friend_list()
        self.debug('[update_friend_list]', _r)

        if _r['code'] == '0':
            self.friend_id_list = []

            for _ in _r['data']:
                if _['userId'] in self.user_detail:
                    self.user_detail[_['userId']].update(_)
                else:
                    self.user_detail[_['userId']] = _
                self.user_detail[_['userId']]['last_update_time'] = time.time()
                self.friend_id_list.append(_['userId'])
                self.commid_to_user_id_dict[_['conversationId']] = _['userId']   # 更新会话id对应的好友id
        else:
            self.debug('[update_friend_list]', _r)

    def logout(self):
        """
        关闭socket
        :return: None
        """
        self.exit = True
        time.sleep(4)
        self.save_last_seq_id_and_timestamp()
        self.sock.close()

    def logout_without_save_info(self):
        """
        退出，但是不更新当前的消息ID和时间戳
        :return:
        """
        self.exit = True
        time.sleep(4)
        # self.save_last_seq_id_and_timestamp()
        self.sock.close()

    def save_last_seq_id_and_timestamp(self):
        """将最后的消息id和消息时间戳保存到文件"""
        # if self.last_msg_sequence_id > 0 and self.last_msg_receive_time:
        #     data = {
        #         'last_msg_sequence_id': self.last_msg_sequence_id,
        #         'last_msg_receive_time': self.last_msg_receive_time
        #     }
        #     self.debug('[save_last_seq_id_and_timestamp]', data)
        #     with open(self.last_msg_seq_json_path, 'w') as fd:
        #         json.dump(data, fd)

        """将最后的消息id和消息时间戳保存到文件"""
        if os.path.exists(self.last_msg_seq_json_path):
            with open(self.last_msg_seq_json_path, 'r') as f:
                data = json.load(f)
        else:
            data = {}
        # 记录最后心跳消息id和时间戳
        if self.last_msg_sequence_id > 0 and self.last_msg_receive_time:
            data['last_msg_sequence_id'] = self.last_msg_sequence_id
            data['last_msg_receive_time'] = self.last_msg_receive_time

        # 记录每一个会话的最后消息id
        if 'communication_last_id' not in data:
            data['communication_last_id'] = {}

        for communication_id in self.communication_info:

            communication_last_msg = self.communication_info[communication_id]['last_msg']
            data['communication_last_id'][communication_id] = communication_last_msg['message_id'] if 'message_id' in communication_last_msg else communication_last_msg['messageId']
            if type(data['communication_last_id'][communication_id]) == str:
                data['communication_last_id'][communication_id] = int(data['communication_last_id'][communication_id])

        # 已经被解散的会话不需要存储
        data['communication_last_id'] = {communication_id: data['communication_last_id'][communication_id] for communication_id in data['communication_last_id'] if communication_id not in self.already_destroy_comm_id_set}

        self.debug('[save_last_seq_id_and_timestamp]', data)
        with open(self.last_msg_seq_json_path, 'w') as fd:
            json.dump(data, fd, indent=4)

    def recall_msg(self, comm_id, msg_id):
        """
        撤回消息
        :param comm_id: 会话id
        :param msg_id: 消息id
        :return: dict(json)
        """
        return recall_msg(self.token, comm_id, msg_id)

    def send_address_msg(self, comm_id, comm_type, to_id=None):
        """
        发送位置消息
        :param comm_id:  会话id
        :param comm_type: 会话类型
        :param to_id: 接收方id, 如果是群聊类型 传None
        :return: 解码后的msg
        """
        if comm_type == 1:
            msg = get_communication_message_by_single(7, self.key, self.user_info['app_id'], self.user_info['user_id'], to_id, comm_id, other=self.other)
        elif comm_type == 2:
            msg = get_communication_message_by_group(7, self.key, self.user_info['app_id'], self.user_info['user_id'], comm_id, other=self.other)
        else:
            msg = get_communication_message_by_chat_room(7, self.key, self.user_info['app_id'], self.user_info['user_id'], comm_id, other=self.other)
        self.sock.send(msg)

        return decode_communication_message(*get_src_body(msg))

    def send_emoji_msg(self, comm_id, comm_type, to_id=None):
        """
        发送表情消息
        :param comm_id:  会话id
        :param comm_type: 会话类型
        :param to_id: 接收方id, 如果是群聊类型 传None
        :return: 解码后的msg
        """
        if comm_type == 1:
            msg = get_communication_message_by_single(2, self.key, self.user_info['app_id'], self.user_info['user_id'], to_id, comm_id, other=self.other)
        elif comm_type == 2:
            msg = get_communication_message_by_group(2, self.key, self.user_info['app_id'], self.user_info['user_id'], comm_id, other=self.other)
        else:
            msg = get_communication_message_by_chat_room(2, self.key, self.user_info['app_id'], self.user_info['user_id'], comm_id, other=self.other)
        self.sock.send(msg)

        return decode_communication_message(*get_src_body(msg))

    def send_text_msg(self, comm_id, comm_type, content_msg, to_id=None):
        """
        发送文本消息
        :param comm_id:  会话id
        :param comm_type: 会话类型
        :param content_msg: 文本内容
        :param to_id: 接收方id, 如果是群聊类型 传None
        :return: 解码后的msg
        """
        if comm_type == 1:
            msg = get_communication_message_by_single(1, self.key, self.user_info['app_id'], self.user_info['user_id'], to_id, comm_id, content=content_msg, other=self.other)
        elif comm_type == 2:
            msg = get_communication_message_by_group(1, self.key, self.user_info['app_id'], self.user_info['user_id'], comm_id, content=content_msg, other=self.other)
        else:
            msg = get_communication_message_by_chat_room(1, self.key, self.user_info['app_id'], self.user_info['user_id'], comm_id, content=content_msg, other=self.other)
        self.sock.send(msg)
        return decode_communication_message(*get_src_body(msg))

    def send_read_destroy_msg(self, comm_id, comm_type, content_msg, to_id=None):
        """
        发送阅后即焚消息
        :param comm_id:  会话id
        :param comm_type: 会话类型
        :param content_msg: 文本内容
        :param to_id: 接收方id, 如果是群聊类型 传None
        :return: 解码后的msg
        """
        other = json.loads(self.other)
        other['burn'] = {"burnMsgType": "1", "isClicked": False}
        other = json.dumps(other)
        if comm_type == 1:
            msg = get_communication_message_by_single(1, self.key, self.user_info['app_id'], self.user_info['user_id'], to_id, comm_id, content=content_msg, other=other)
        elif comm_type == 2:
            msg = get_communication_message_by_group(1, self.key, self.user_info['app_id'], self.user_info['user_id'], comm_id, content=content_msg, other=other)
        else:
            msg = get_communication_message_by_chat_room(1, self.key, self.user_info['app_id'], self.user_info['user_id'], comm_id, content=content_msg, other=other)
        self.sock.send(msg)
        return decode_communication_message(*get_src_body(msg))

    def send_video_msg(self, comm_id, comm_type, to_id=None):
        """
        发送视频消息
        :param comm_id:  会话id
        :param comm_type: 会话类型
        :param to_id: 接收方id, 如果是群聊类型 传None
        :return: 解码后的msg
        """
        if comm_type == 1:
            msg = get_communication_message_by_single(6, self.key, self.user_info['app_id'], self.user_info['user_id'], to_id, comm_id, other=self.other)
        elif comm_type == 2:
            msg = get_communication_message_by_group(6, self.key, self.user_info['app_id'], self.user_info['user_id'], comm_id, other=self.other)
        else:
            msg = get_communication_message_by_chat_room(6, self.key, self.user_info['app_id'], self.user_info['user_id'], comm_id, other=self.other)
        self.sock.send(msg)
        return decode_communication_message(*get_src_body(msg))

    def send_image_msg(self, comm_id, comm_type, to_id=None):
        """
        发送图片消息
        :param comm_id:  会话id
        :param comm_type: 会话类型
        :param to_id: 接收方id, 如果是群聊类型 传None
        :return: 解码后的msg
        """
        if comm_type == 1:
            msg = get_communication_message_by_single(4, self.key, self.user_info['app_id'], self.user_info['user_id'], to_id, comm_id, other=self.other)
        elif comm_type == 2:
            msg = get_communication_message_by_group(4, self.key, self.user_info['app_id'], self.user_info['user_id'], comm_id, other=self.other)
        else:
            msg = get_communication_message_by_chat_room(4, self.key, self.user_info['app_id'], self.user_info['user_id'], comm_id, other=self.other)
        self.sock.send(msg)
        return decode_communication_message(*get_src_body(msg))

    def send_audio_msg(self, comm_id, comm_type, to_id=None):
        """
        发送音频消息
        :param comm_id:  会话id
        :param comm_type: 会话类型
        :param to_id: 接收方id, 如果是群聊类型 传None
        :return: 解码后的msg
        """
        if comm_type == 1:
            msg = get_communication_message_by_single(5, self.key, self.user_info['app_id'], self.user_info['user_id'], to_id, comm_id, other=self.other)
        elif comm_type == 2:
            msg = get_communication_message_by_group(5, self.key, self.user_info['app_id'], self.user_info['user_id'], comm_id, other=self.other)
        else:
            msg = get_communication_message_by_chat_room(5, self.key, self.user_info['app_id'], self.user_info['user_id'], comm_id, other=self.other)
        self.sock.send(msg)
        return decode_communication_message(*get_src_body(msg))

    def send_file_msg(self, comm_id, comm_type, to_id=None):
        """
        发送文件消息
        :param comm_id:  会话id
        :param comm_type: 会话类型
        :param to_id: 接收方id, 如果是群聊类型 传None
        :return: 解码后的msg
        """
        if comm_type == 1:
            msg = get_communication_message_by_single(3, self.key, self.user_info['app_id'], self.user_info['user_id'], to_id, comm_id, other=self.other)
        elif comm_type == 2:
            msg = get_communication_message_by_group(3, self.key, self.user_info['app_id'], self.user_info['user_id'], comm_id, other=self.other)
        else:
            msg = get_communication_message_by_chat_room(3, self.key, self.user_info['app_id'], self.user_info['user_id'], comm_id, other=self.other)
        self.sock.send(msg)
        return decode_communication_message(*get_src_body(msg))

    def send_chat_msg(self, to_id, comm_id, comm_type, msg_type, count, sleep_time, content_msg=None):
        """
        发送消息函数
        """
        time.sleep(randint(1, 10) / 10)
        if type(comm_type) == str:
            comm_type = int(comm_type)
        self.info('[send_chat_msg]', to_id, comm_id, comm_type, msg_type, count, sleep_time)
        flag = ''.join(sample('abcedfghijklmnopqrstuvwxyzABCEDFGHIJKLMNOPQRSTUVWXYZ0123456789', 6))
        _s = time.time()
        for i in range(count):
            if msg_type == 1:
                if content_msg is None:
                    _content_msg = '{}-{}-[{}] [{:>03}]'.format(comm_id, flag, time.strftime('%Y-%m-%d %H:%M:%S'), i)
                else:
                    _content_msg = content_msg
            else:
                _content_msg = None

            if comm_type == 1:
                msg = self.get_single_msg(msg_type, to_id, comm_id, _content_msg)
            elif comm_type == 2:
                msg = self.get_group_msg(msg_type, comm_id, _content_msg)
            elif comm_type == 3:
                msg = self.get_chat_room_msg(msg_type, comm_id, _content_msg)
            else:
                raise Exception('unknow comm_type {}'.format(comm_type))
            # await self.write_queue.put(msg)
            self.sock.send(msg)
            time.sleep(sleep_time)
        _e = time.time()
        print('cost: ', _e - _s)
        self.info('[send_chat_msg]', 'finished')
        if comm_type in self.send_msg_details['communication_type']:
            self.send_msg_details['communication_type'][comm_type] += count
        else:
            self.send_msg_details['communication_type'][comm_type] = count

        if msg_type in self.send_msg_details['message_type']:
            self.send_msg_details['message_type'][msg_type] += count
        else:
            self.send_msg_details['message_type'][msg_type] = count

        if comm_id in self.send_msg_details['communication_id']:
            self.send_msg_details['communication_id'][comm_id] += count
        else:
            self.send_msg_details['communication_id'][comm_id] = count
        return comm_id, count

    def clear_send_msg_details(self):
        self.send_msg_details = {
            'communication_type': {},
            'message_type': {},
            'communication_id': {}
        }

    def del_friend(self, user_id: str) -> dict:
        """
        删除好好友
        :param user_id: 好友id
        :return: json
        """
        _res = del_friend(self.token, user_id)
        self.debug('[del_friend]', _res['code'])
        if _res['code'] == '0':
            # del self.user_id_to_nickname[user_id]
            try:
                self.friend_id_list.remove(user_id)
            except Exception as _e:
                self.debug('[del_friend]', _e)
        return _res

    def delete_sync_msg_by_communication(self, conversation_id):
        """
        删除会话的漫游消息
        :param conversation_id:
        :return:
        """
        _res = delete_sync_msg_by_communication(self.token, conversation_id)
        self.debug('[delete_sync_msg_by_communication]', _res)
        return _res

    def delete_sync_msg_by_user(self):
        """
        删除用户的全部漫游消息
        :return:
        """
        _res = delete_sync_msg_by_user(self.token)
        self.debug('[delete_sync_msg_by_user]', _res)
        return _res

    def delete_runtime_json(self):
        """
        删除用户的runtime json文件(存放最后的消息ID及时间戳等)
        :return:
        """
        if os.path.exists(self.last_msg_seq_json_path):
            os.remove(self.last_msg_seq_json_path)
        return not os.path.exists(self.last_msg_seq_json_path)

    def exit_group(self, comm_id: str) -> dict:
        """
        退出群聊
        :param comm_id: 群id
        :return: json
        """
        _res = exit_group(self.token, comm_id)
        self.debug('[exit_group]', _res['code'])
        if _res['code'] == '0':
            self.group_id_list.remove(comm_id)
        return _res

    def remove_group(self, comm_id: str) -> dict:
        """
        删除群聊(群主才能操作)
        :param comm_id: 群id
        :return: json
        """
        _res = remove_group(self.token, comm_id)
        self.debug('[remove_group]', _res['code'])
        # if _res['code'] == '0':
        #     self.group_id_list.remove(comm_id)
        return _res

    def remove_chat_room(self, chat_room_id):
        self.debug('[remove_chat_room]')
        res = chat_room_remove(self.token, chat_room_id)
        return res

    def add_friend(self, dst_id: str) -> dict:
        """
        添加好友
        :param dst_id: 好友id
        :return: json
        """
        _res = add_friend(self.token, dst_id)
        self.debug('[add_friend]', _res['code'])
        if 'data' in _res:
            if 'resourceType' in _res['data'] and _res['data']['resourceType'] == 2:
                self.update_friend_list()
        return _res

    def get_friend_list(self) -> dict:
        """
        显示好友, 返回给gui线程显示出来
        """
        _res = get_friend_list(self.token)
        self.debug('[get_friend_list]', _res['code'])
        return _res

    def get_user_black_list(self):  # 獲取好友黑名单
        _r = get_user_black_list(self.token)
        return _r
    
    def get_chat_room_detail(self, chat_room_id):
        self.debug('[get_chat_room_detail]')
        res = chat_room_detail(self.token, chat_room_id)
        return res
        
    def get_chat_room_detail_multi(self, chat_room_ids):
        self.debug('[get_chat_room_detail_multi]')
        res = chat_room_detail_list(self.token, chat_room_ids)
        return res
                
    def set_friend_black_list(self, user_id_list_str, flag):    # 设置通讯录黑名单
        _r = set_friend_black_list(self.token, user_id_list_str, flag)
        return _r

    def invite_user_to_group(self, group_id: str, user_id_list_str: str) -> dict:
        _res = invite_user_to_group(self.token, group_id, user_id_list_str, 'hello world')
        self.debug('[invite_user_to_group]', _res['code'])
        return _res

    def remove_group_member(self, group_id: str, user_id_list_str: str) -> dict:     # 群主或管理员踢出多个群组成员
        _res = remove_group_member(self.token, group_id, user_id_list_str)
        self.debug('[remove_group_member]', _res['code'])
        return _res

    def get_group_list(self) -> dict:
        """
        显示群聊, 返回给gui线程显示出来
        """
        _res = get_group_list(self.token)
        self.debug('[get_group_list]', _res['code'])
        self.group_id_list = []
        for _i in _res['data']:
            group_id = _i['communicationId']
            self.group_id_list.append(group_id)
            self.group_info[group_id] = {}
            self.group_info[group_id]['name'] = _i['name']
            self.group_info[group_id]['ownerId'] = _i['ownerId']
        return _res

    def get_group_user_list(self, group_id: str) -> dict:
        _res = search_group_userlist(self.token, group_id)
        self.debug('[get_group_user_list]', _res['code'])
        return _res

    def get_group_black_list(self, group_id):
        _res = get_group_black_list(self.token, group_id)
        return _res

    def get_group_manager_list(self, group_id):
        _res = get_group_manager_list(self.token, group_id)
        return _res

    def get_group_mute_list(self, group_id):
        _res = get_group_mute_list(self.token, group_id)
        return _res

    def set_group_mute(self, group_id, user_id_list_str, flag):  # 设置群聊禁言
        _res = set_group_mute(self.token, group_id, user_id_list_str, flag)
        return _res

    def set_group_all_mute(self, group_id, mute_status: bool):
        _res = set_group_all_mute(self.token, group_id, mute_status)
        return _res

    def set_group_black_list(self, group_id, user_id_list_str, flag=None):
        _res = set_group_black_list(self.token, group_id, user_id_list_str, flag)
        return _res

    def set_group_white_list(self, group_id, user_id_list_str, flag='add'):
        _res = set_group_white_list(self.token, group_id, user_id_list_str, flag)
        return _res

    def set_group_manager(self, group_id, user_id_list_str, flag):
        _res = set_group_manager(self.token, group_id, user_id_list_str, flag)
        return _res

    def set_group_attribute(self, group_id, key, value):
        _res = set_group_attribute(self.token, group_id, key, value)
        return _res

    def set_group_remark(self, group_id, remark):
        _res = set_group_remark(self.token, group_id, remark)
        return _res

    def set_chat_room_announcement(self, chat_room_id, announcement):
        self.debug('set_chat_room_announcement', announcement)

        res = chat_room_announcement_update(self.token, chat_room_id, announcement)
        return res

    def set_chat_room_manager(self, chat_room_id, manager_ids_str, flag):
        self.debug('[set_chat_room_manager]')
        res = chat_room_manager_multi_set(self.token, chat_room_id, manager_ids_str, flag)
        return res

    def set_chat_room_black_list(self, chat_room_id, black_list_str, flag):
        self.debug('[set_chat_room_black_list]')
        res = chat_room_user_multi_black_set(self.token, chat_room_id, black_list_str, flag)
        return res

    def set_chat_room_white_list(self, chat_room_id, while_list_str, flag):
        self.debug('[set_chat_room_white_list]')
        res = chat_room_user_mute_white_set(self.token, chat_room_id, while_list_str, flag)
        return res

    def set_chat_room_mute(self, chat_room_id, mute_list_str, flag):
        self.debug('[set_chat_room_mute]')
        res = chat_room_user_multi_mute_set(self.token, chat_room_id, mute_list_str, flag)
        return res

    def set_chat_room_member(self, chat_room_id, member_list_str, flag):
        self.debug('[set_chat_room_member]')
        res = chat_room_member_set(self.token, chat_room_id, member_list_str, flag)
        return res

    def set_chat_room_name(self, chat_room_id, name):
        self.debug('[set_chat_room_name]')
        res = chat_room_name_update(self.token, chat_room_id, name)
        return res

    def set_chat_room_all_mute(self, chat_room_id: str, status: bool):
        self.debug('[set_chat_room_all_mute]')
        res = chat_room_mute_all(self.token, chat_room_id, status)
        return res

    def set_user_new_notify(self, notify_switch: bool, notify_type: int):
        """
        设置新通知方式
        :param notify_switch: 通知开关,true-开,false-关
        :param notify_type: 通知类型，0-响铃 1-振动
        :return:
        """
        self.debug('[set_user_new_notify]')
        _res = user_setting_new_notify(self.token, notify_switch, notify_type)
        return _res

    def set_user_auto_login(self, auto_login: bool):
        """
        设置是否自动登录
        :param auto_login:
        :return:
        """
        self.debug('[set_user_auto_login]')
        _res = user_setting_auto_login(self.token, auto_login)
        return _res

    def set_user_show_push_detail(self, show: bool):
        """
        设置是否显示用户通知详情
        :param show:
        :return:
        """
        _res = user_setting_show_push_detail(self.token, show)
        self.debug('[set_user_show_push_detail]')
        return _res

    def group_share_files_list(self, group_id: str, count: int = None, create_time: int = None):
        """
        获取群共享文件
        :param group_id: 群组ID
        :param count: 一次拉取列表数量
        :param create_time: 文件列表的最后一条的创建时间
        """
        _res = group_share_files_list(self.token, group_id, count, create_time)
        return _res

    def group_share_files_upload(self, group_id: str, file_path: str):
        """
        上传群共享文件
        :param group_id: 群组ID
        :param file_path: 文件路径
        """
        _res = group_share_files_upload(self.token, group_id, file_path)
        return _res

    def group_share_files_del(self, group_id: str, file_id: int):
        _res = group_share_files_del(self.token, group_id, file_id)
        return _res

    def accept_friend_group(self) -> (dict, dict):
        """
        设置自动入群和加好友
        """
        self.debug('[accept_friend_group]')
        res1 = set_auto_add_friend_accept(self.token, True)
        res2 = set_auto_accept(self.token, True)
        return res1, res2

    def refuse_friend_group(self) -> (dict, dict):
        """
        关闭自动入群和加好友
        """
        self.debug('[refuse_friend_group]')
        res1 = set_auto_add_friend_accept(self.token, False)
        res2 = set_auto_accept(self.token, False)
        return res1, res2

    def create_group(self, user_list_strs: str, group_name=None) -> dict:
        if group_name is None:
            group_name = '[' + time.strftime('%Y-%m-%d %H:%M:%S') + ']'
        _res = create_group(self.token, group_name, user_list_strs, '', 'hello world', '')
        self.info('[create_group]', _res['code'])
        if _res['code'] == '0':
            data = _res['data']
            self.group_id_list.append(data['communicationId'])
            self.group_info[data['communicationId']] = {
                'ownerId': self.user_info['user_id'],
                'name': data['name']
            }
        return _res

    def create_chat_room(self):
        self.debug('[create_chat_room]')
        name = '{}'.format(time.strftime('%Y-%m-%d %H:%M:%S'))
        _res = chat_room_create(self.token, name, '聊天室测试')
        return _res

    def accept_friend_apply(self, user_id):  # 同意添加好友
        _res = accept_friend_req(self.token, user_id)
        self.info('[accept_friend_apply]', _res)
        if _res['code'] == '0':
            self.update_friend_list()
        return _res

    def refuse_friend_apply(self, user_id):  # 拒绝好友申请
        _res = reject_friend_req(self.token, user_id)
        self.info('[refuse_friend_apply]', _res)
        return _res

    def user_accept_group_invite(self, group_id):   # 用户同意入群
        _res = user_accept_group_invite(self.token, group_id)
        # print(_res)
        self.info('[user_accept_group_invite]', _res)
        if _res['code'] == '0' and _res['data']['inviteStatus'] == 1:   # 入群成功
            # 更新 self.group_id_list
            self.group_id_list.append(group_id)
            # 更新 self.group_info
            self.group_info[group_id] = {
                'name': _res['data']['groupInfo']['name'],
                'ownerId': _res['data']['groupInfo']['ownerId']
            }
        return _res

    def user_reject_group_invite(self, group_id):   # 用户拒绝入群
        _res = user_reject_group_invite(self.token, group_id)
        self.info('[user_reject_group_invite]', _res)
        return _res

    def manager_accept_group_invite(self, group_id, user_id):    # 群成员拉人入群被管理员通过
        _res = manager_accept_group_invite(self.token, group_id, user_id)
        self.info('[manager_accept_group_invite]', _res)
        return _res

    def manager_reject_group_invite(self, group_id, user_id):    # 群成员拉人入群被管理员拒绝
        _res = manager_reject_group_invite(self.token, group_id, user_id)
        self.info('[manager_reject_group_invite]', _res)
        return _res

    def get_single_msg(self, msg_type, to_id, comm_id, msg) -> bytes:
        _msg = get_communication_message_by_single(msg_type, self.key, self.user_info['app_id'], self.user_info['user_id'], to_id, comm_id, msg, other=self.other)
        return _msg
        
    def get_group_msg(self, msg_type, comm_id, msg) -> bytes:
        _msg = get_communication_message_by_group(msg_type, self.key, self.user_info['app_id'], self.user_info['user_id'], comm_id, msg, other=self.other)
        return _msg

    def get_chat_room_msg(self, msg_type, comm_id, msg) -> bytes:
        _msg = get_communication_message_by_chat_room(msg_type, self.key, self.user_info['app_id'], self.user_info['user_id'], comm_id, msg, other=self.other)
        return _msg

    def heartbeat_thread(self):
        """
        心跳协程, 定时产生一条心跳消息到协程队列
        """
        while not self.is_login:
            time.sleep(0.1)
        while not self.exit:
            current_timestamp = time.time()
            if current_timestamp - self.last_send_heartbeat_time >= self.header_beat_time:
                with self.lock:
                    _msg = self.get_heartbeat_msg()
                if _msg:
                    self.sock.send(_msg)
                time.sleep(self.header_beat_time)
            else:
                time.sleep(self.header_beat_time - current_timestamp + self.last_send_heartbeat_time)
        self.debug('[heartbeat_thread] heartbeat_thread exit')
        # self.sock.close()

    def get_heartbeat_msg(self):
        current_time_stamp = time.time()
        _last_msg_sequence_id = self.last_msg_sequence_id
        _last_send_heartbeat_time = self.last_send_heartbeat_time
        if current_time_stamp - _last_send_heartbeat_time < self.header_beat_time:  # 发送间隔小于心跳间隔
            # if self.last_msg_receive_time == _last_send_heartbeat_time:  # 如果id小于等于上次发送的id就返回空
            if self.last_send_seq_id == self.last_msg_sequence_id:
                return
        # 其他情况下都允许发送一个心跳
        self.last_send_heartbeat_time = time.time()
        self.last_send_seq_id = _last_msg_sequence_id
        msg = get_heartbeat_message(
            self.key,
            device_type=1,
            last_msg_sequence_id=_last_msg_sequence_id,
            last_msg_receive_time=self.last_msg_receive_time
        )
        # self.info('[get_heartbeat_msg] send heartbeat: timestamp:{:.3f}, last_id:{}, last_timestamp: {}'.format(current_time_stamp, self.last_msg_sequence_id, self.last_msg_receive_time))
        return msg

    def get_ack_msg(self, from_user_id, to_user_id, communication_id, message_id, msg_no=None) -> bytes:
        msg = get_msg_ack_message(self.key, self.user_info['app_id'], from_user_id, to_user_id, communication_id, message_id, msg_no)
        return msg

    def get_read_msg(self, from_user_id, to_user_id, communication_id, message_id, msg_no=None) -> bytes:
        msg = get_msg_read_message(self.key, self.user_info['app_id'], from_user_id, to_user_id, communication_id, message_id, msg_no)
        return msg

    def get_offline_msg(self):
        """
        拉取离线消息
        :return: None
        """
        if os.path.exists(self.last_msg_seq_json_path):
            with open(self.last_msg_seq_json_path, 'r') as json_fd:
                data = json.load(json_fd)
            if type(data['last_msg_receive_time']) == int:
                data['last_msg_receive_time'] = str(data['last_msg_receive_time'])
        else:
            data = {
                'last_msg_receive_time': '0',
                'last_msg_sequence_id': 0
            }
        # 拉取离线会话需要用到上次的id和时间戳信息
        offline_conversation_list_res = get_offline_conversation_list(self.token, 1, data['last_msg_receive_time'], data['last_msg_sequence_id'])
        self.debug('[get_offline_msg] offline_conversation_list_res: ', offline_conversation_list_res)
        if 'code' not in offline_conversation_list_res or offline_conversation_list_res['code'] != '0':
            return  # 拉取离线会话异常就直接返回
        for _k in ['conversationRespVoList', 'notifyMsgList']:
            for comm_info in offline_conversation_list_res['data'][_k]:
                start_msg_id = self.last_msg_sequence_id
                last_msg_receive_time = self.last_msg_receive_time
                while 1:
                    # 拉取离线会话的消息时，需要上一次拉到的离线消息最小ID,如果是第一次拉取，传登录时服务器返回的seq_id
                    # 时间戳传登录时服务器返回的时间戳
                    offline_msg_res = get_offline_msg_by_cid(self.token, comm_info['communicationId'], 50, 1, start_msg_id, last_msg_receive_time)
                    offline_msg_len = 0
                    if 'msgList' in offline_msg_res['data']:
                        offline_msg_len += len(offline_msg_res['data']['msgList'])
                    if offline_msg_len == 0:
                        break
                    receive_offline_msg_id_list = list()
                    if 'msgList' in offline_msg_res['data']:
                        for _offline_msg in offline_msg_res['data']['msgList']:
                            self.handle_offline_msg(_offline_msg)
                            receive_offline_msg_id_list.append(_offline_msg['messageId'])
                    start_msg_id = min(receive_offline_msg_id_list)
                    end_msg_id = max(receive_offline_msg_id_list)
                    # 删除消息时，需要用到当前拉到的消息的最大ID和最小ID
                    _res = clean_offline_message(self.token, 1, comm_info['communicationId'], end_msg_id, self.last_msg_receive_time, start_msg_id)
                    self.info('[get_offline_msg] [clean_offline_message]', _res)

    def handle_offline_msg(self, msg: dict):
        """
        处理离线消息, append到对应的会话队列中
        :param msg:
        :return: None
        """
        self.debug('[handle_offline_msg]', msg['content'] if 'content' in msg else msg['messageType'])
        if 'communicationType' not in msg or msg['communicationType'] == 0:
            msg['communicationType'] = 100
        if msg['communicationType'] == 100:
            msg['communicationId'] = 'system'
        if 'communicationId' not in msg:
            msg['communicationId'] = 'system'
        try:
            if 'msg_count' in self.communication_info[msg['communicationId']]:
                self.communication_info[msg['communicationId']]['msg_count'] += 1   # 总消息数量
            else:
                self.communication_info[msg['communicationId']]['msg_count'] = 1
            self.debug('[handle_offline_msg]', self.communication_info[msg['communicationId']]['msg_count'])
            self.communication_info[msg['communicationId']]['last_time_stamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
            if 'last_msg' not in self.communication_info[msg['communicationId']]:
                self.communication_info[msg['communicationId']]['last_msg'] = msg
            self.communication_msg[msg['communicationId']].appendleft(msg)
        except Exception as _e:
            print(_e, 'handle_offline_msg')

    def get_sync_msg(self):
        """
        同步消息记录
        :return:
        """
        if os.path.exists(self.last_msg_seq_json_path):
            with open(self.last_msg_seq_json_path, 'r') as f:
                data = json.load(f)
        else:
            data = {
                'last_msg_sequence_id': 0
            }
        communication_last_id_info = data['communication_last_id'] if 'communication_last_id' in data else {}
        sync_communication_list_res = get_sync_communication_list(self.token, 1, data['last_msg_sequence_id'])
        self.debug('[get_sync_msg]', sync_communication_list_res)

        # 处理普通消息
        for communication_info in sync_communication_list_res['data']['conversationRespVoList']:
            communication_id = communication_info['communicationId']
            current_communication_last_id = communication_last_id_info[communication_id] if communication_id in communication_last_id_info else 0   # 当前会话上次最后拉的消息
            # self.debug('[get_sync_msg]', communication_info)
            last_msg_id = communication_info['lastMsgId']
            """
            如果服务器返回的该会话最后一条消息大于current_communication_last_id, 就将这消息插入到新消息中
            因为get_sync_message_list接口逻辑是返回小于传入的消息id,没有取<=
            如果不把该会话的lastMsg保存起来，那么通过get_sync_message_list接口会拉不到这条消息
            """
            if last_msg_id > current_communication_last_id:
                self.handle_sync_msg(communication_info['lastMsg'])
            while current_communication_last_id < last_msg_id:
                msg_list_res = get_sync_message_list(self.token, communication_id, 50, last_msg_id)
                self.debug('[get_sync_msg]', communication_id, 50, last_msg_id)
                for msg in msg_list_res['data']['msgList']:
                    if msg['messageId'] > current_communication_last_id:
                        self.handle_sync_msg(msg)
                if len(msg_list_res['data']['msgList']) < 50:   # 拉到的消息小于50条说明没有新消息可拉取
                    break
                last_msg_id = min([_msg['messageId'] for _msg in msg_list_res['data']['msgList']])    # last_msg_id每次取最小msg_id
        # 处理通知类型消息
        for notify_msg in sync_communication_list_res['data']['notifyMsgList']:
            self.handle_sync_msg(notify_msg)

    def handle_sync_msg(self, msg: dict):
        if 'communicationId' not in msg:
            msg['communicationId'] = 'system'

        # if 'communicationType' not in msg or msg['communicationType'] == 0:
        #     msg['communicationType'] = 100
        # if msg['communicationType'] == 100:
        #     msg['communicationId'] = 'system'

        try:
            if 'msg_count' in self.communication_info[msg['communicationId']]:
                if msg['fromUserId'] != self.user_id:
                    self.communication_info[msg['communicationId']]['msg_count'] += 1   # 总消息数量
            else:
                if msg['fromUserId'] != self.user_id:
                    self.communication_info[msg['communicationId']]['msg_count'] = 1
                else:
                    self.communication_info[msg['communicationId']]['msg_count'] = 0
            # self.debug('[handle_offline_msg]', self.communication_info[msg['communicationId']]['msg_count'])
            self.communication_info[msg['communicationId']]['last_time_stamp'] = time.strftime('%Y-%m-%d %H:%M:%S')

            if 'last_msg' not in self.communication_info[msg['communicationId']]:
                self.communication_info[msg['communicationId']]['last_msg'] = msg
            self.communication_msg[msg['communicationId']].appendleft(msg)
        except Exception as _e:
            print(_e, 'handle_sync_msg')

    def handle_chat_room_msg(self, msg):
        self.communication_msg[msg['communication_id']].append(msg)

    def handle_recv_msg(self, msg):
        """
        单条聊天消息的处理, append到对应的会话队列中
        :param msg: 聊天消息
        :return: None
        """
        # try:
        #     send_time_stamp = int(msg['tag'][0:13])
        #     current_time_stamp = time.time()*1000
        #     cost = current_time_stamp - send_time_stamp
        #     self.cost.append(cost)
        # except Exception as _e:
        #     self.debug('handle_recv_msg', _e)
        self.debug('[handle_recv_msg]', msg)
        if 'communication_type' in msg and msg['communication_type'] == 3:
            self.handle_chat_room_msg(msg)
            return

        if msg['from_user_id'] == self.user_info['user_id']:
            if 'message_main_type' in msg and msg['message_main_type'] == 1:
                return
            if 'communication_type' in msg and msg['communication_type'] in [1, 2] and msg['message_type'] in [1, 2, 3, 4, 5, 6, 7]:
                return
        if 'communication_type' not in msg or msg['communication_type'] == 0:
            msg['communication_type'] = 100
        # elif msg['communication_type'] == 100:
        #     msg['communication_id'] = 'system'
        if 'communication_id' not in msg:
            msg['communication_id'] = 'system'
        if 'msg_count' in self.communication_info[msg['communication_id']]:
            self.communication_info[msg['communication_id']]['msg_count'] += 1
        else:
            self.communication_info[msg['communication_id']]['msg_count'] = 1
            self.communication_info[msg['communication_id']]['start'] = 0
        self.communication_info[msg['communication_id']]['last_time_stamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
        _nickname = ''
        self.communication_info[msg['communication_id']]['last_msg'] = msg
        self.communication_msg[msg['communication_id']].append(msg)

        if msg['message_type'] == 106:    # 好友关系确认
            self.update_friend_list()
        elif msg['message_type'] == 107:  # 删除好友
            try:
                self.friend_id_list.remove(msg['from_user_id'])
            except Exception as _e:
                self.debug('[handle_recv_msg]', _e)
        elif msg['message_type'] == 110:  # 删除后重新添加好友
            if msg['from_user_id'] == self.user_id:
                self.update_friend_list()
        elif msg['message_type'] == 111:    # 用户信息更新
            pass
        elif msg['message_type'] in {304, 324}:    # 被踢,群被解散
            current_group_id = json.loads(msg['content'])['groupId']
            if current_group_id in self.group_id_list:
                self.group_id_list.remove(current_group_id)
            if msg['message_type'] == 324:  # 群解散
                self.already_destroy_comm_id_set.add(current_group_id)
        elif msg['message_type'] == 301:    # 自动入群
            if msg['from_user_id'] == self.user_info['user_id']:
                return
            group_id = json.loads(msg['content'])['groupId']
            self.get_group_name(group_id)
            self.group_id_list.append(group_id)
        elif msg['message_type'] == 323:    # 群主变更
            pass
        elif msg['message_type'] == 325:    # 群名变更
            pass
        elif msg['message_type'] == 326:    # 群列表变更
            self.get_group_list()

    def handle_read(self):
        """
        读取socket数据线程
        :return: None
        """
        while not self.start:
            time.sleep(0.1)
        sock = self.sock
        while not self.exit:
            try:
                buffer = sock.recv(5)  # 前4个字节代表包的长度
                lens = len(buffer)
                while lens < 5:
                    _d = sock.recv(5-lens)
                    if _d is None or _d == b'':
                        self.debug('[handle_read] read_head', _d, buffer)
                        raise Exception('[handle_read] get header error')
                    else:
                        buffer += _d
                    lens = len(buffer)
                length, command = msg_unpack_length_and_command(buffer)  # 解析包长度及类型
                if not length or not command:
                    print(length, command)
                length -= 1  # 上面读了5字节数据,总长度:4bytes,command:1bytes,相当于多读了1字节，所以实际长度-1
                buffer = sock.recv(length)
            except Exception as exce:
                self.debug('[handle_read] recv get error: ', exce)
                # self.q.put(None)
                # sock.close()
                self.exit = True   # 退出flag
                self.debug('[handle_read] set exit: ', self.exit)
                # self.save_last_seq_id_and_timestamp()
                self.err_msg = str(exce)
                self.info(self.err_msg)
                # raise Exception('recv eror') from exce
            else:
                buff_len = len(buffer)
                while buff_len < length:
                    buffer += sock.recv(length-buff_len)
                    buff_len = len(buffer)
                key_len = buffer[0]
                _ = buffer[1: 1+key_len]    # key
                proto_name_len = buffer[1+key_len]
                proton_ame = buffer[2+key_len: 2+key_len+proto_name_len]
                proto_body = buffer[2+key_len+proto_name_len:]
                self.debug('[handle_read]', proton_ame)
                if proto_body:
                    res = decode_communication_message(proton_ame, proto_body)
                    self.info('[handle_read]', res)
                    if proton_ame == b'RspBindUserChannel':
                        if 'resp' in res and 'ret' in res['resp'] and res['resp']['ret'] != 0:
                            self.debug('[handle_read] [RspBindUserChannel]', res)
                            raise Exception('RspBindUserChannel Error!, {}'.format(str(res)))
                        self.is_login = True
                        self.last_msg_receive_time = res['last_msg_receive_time']
                        self.last_msg_sequence_id = int(res['last_msg_sequence_id'])
                    elif proton_ame == b'CommunicationMessageProto':
                        self.handle_recv_msg(res)  # 处理接收的消息
                    elif proton_ame == b'ReplyCommandSendMsgReq':
                        if 'resp' in res and 'ret' in res['resp']:
                            self.debug('[handle_read] [ReplyCommandSendMsgReq]', res['resp']['ret'])
                        self.reply_command_send_msg_req.append(res)
                    elif proton_ame == b'ForceLogoutProto':
                        self.err_msg = '[handle_read] ForceLogoutProto'
                        self.debug('[handle_read] ForceLogoutProto')
                        time.sleep(2)
                        raise Exception('ForceLogoutError')
                    elif proton_ame == b'HeartBeatAckMsg':
                        """
                        新版本的心跳响应包,需要重新处理
                        """
                        if 'chatMsg' in res:
                            current_max_sequence_id = int(res['last_msg_sequence_id'])
                            current_max_receive_time = res['last_msg_receive_time']
                            self.last_msg_sequence_id = current_max_sequence_id
                            self.last_msg_receive_time = current_max_receive_time
                            for _msg in res['chatMsg']:
                                self.handle_recv_msg(_msg)  # 处理接收的消息
                            self.info('[handle read] chatMsg size: ', len(res['chatMsg']))
                            if len(res['chatMsg']) >= 50:
                                _heartbeat_msg = self.get_heartbeat_msg()
                                if _heartbeat_msg:
                                    with self.lock:
                                        sock.send(_heartbeat_msg)
                    elif proton_ame == b'RespErrorResultProto':
                        self.debug('[handle read]', res)
                    else:
                        self.debug('[handle read]', res)
        self.debug('[handle_read]', 'read exit')
        sock.close()
    
    def _wait_until_connect_success(self):
        """
        等待服务器鉴权通过
        :return: None
        """
        while not self.is_login:    # 等待socket绑定成功
            time.sleep(0.1)
    
    def analysis_msg_cost(self):
        if len(self.cost) == 0:
            return
        print('len', len(self.cost))
        print('min', min(self.cost))
        print('max', max(self.cost))
        print('avg', sum(self.cost)/len(self.cost))

    def run(self):
        self.login()    # sdk登录
        self.get_group_list()  # 拉取群列表
        self.update_friend_list()  # 拉取好友列表
        user_detail_res = self.get_user_detail()
        _other = {
            "userinfo": {
                'username': user_detail_res['data']['nickname'].encode('utf-8').decode('utf-8'),
                'userId': self.user_info['user_id']
            }
        }
        if user_detail_res['data']['avatar'] is not None:
            _other['userinfo']['avatarUrl'] = user_detail_res['data']['avatar']
        self.other = json.dumps(_other, ensure_ascii=False)
        Thread(target=self.build_connection).start()
        Thread(target=self.heartbeat_thread).start()
        Thread(target=self.handle_read).start()
        self._wait_until_connect_success()
