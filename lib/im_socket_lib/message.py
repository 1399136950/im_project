# -*- coding: utf-8
"""
消息序列化及封装处理
@author gaofeng
"""
from enum import Enum

from .proto import MessageProBuf_pb2
from .proto import GlobalBoProto_pb2
from .utils.encrypt import aes_decrypt
from .utils.generator import get_time_stamp, device_id_gen
from .utils.packer import msg_pack
from google.protobuf.json_format import MessageToJson
import json
from random import choice


class CommandType(Enum):
    COMMAND_BIND_USER = 3  # 绑定用户
    COMMAND_SEND_MSG_REQ = 10  # 发送消息请求
    COMMAND_PING = 98  # 心跳
    COMMAND_TEST = 12  # 测试类型
    COMMAND_MESSAGE_ACK = 6	 # 消息送达ack 
    COMMAND_MESSAGE_READ = 7	 # 消息已读ack 
    COMMAND_PULL_MSG_REQ = 13   # 拉消息命令
    COMMAND_PULL_MSG_RESP = 14  # 服务器响应拉消息命令


RECEIVE_TYPE = {
    2: 'HANDSHAKE_RESP',
    4: 'BIND_USER_RESP',
    5: 'COMMAND_AUTH_REQ',
    6: 'MESSAGE_ACK',
    7: 'MESSAGE_READ',
    8: 'FORCE_LOGOUT',
    10: 'SEND_MSG_REQ',
    11: 'SEND_MSG_RSP',
    12: 'SEND_MSG_RSP_TEST',
    99: 'PONG',
}


class CommunicationType(Enum):
    """联系通道类型：单聊/群聊"""
    SINGLE_PERSON = 1


class MessageType(Enum):
    """消息类型"""
    TEXT = 1
    EMOJI = 2
    FILE = 3
    IMAGE = 4
    AUDIO = 5
    VIDEO = 6
    ADDRESS = 7


ProtoBuffers = {
        'CommunicationMessageProto': MessageProBuf_pb2.CommunicationMessageProto,
        'ReqBindUserChannel': MessageProBuf_pb2.ReqBindUserChannel,
        'RspBindUserChannel': MessageProBuf_pb2.RspBindUserChannel,
        'ReplyCommandSendMsgReq': MessageProBuf_pb2.ReplyCommandSendMsgReq,
        'MessageAckProto': MessageProBuf_pb2.MessageAckProto,
        'RespErrorResultProto': GlobalBoProto_pb2.RespErrorResultProto,
        'ForceLogoutProto': MessageProBuf_pb2.ForceLogoutProto,
        'HeartBeatMsg': MessageProBuf_pb2.HeartBeatMsg,
        'HeartBeatAckMsg': MessageProBuf_pb2.HeartBeatAckMsg,
        'BaseRespProto': GlobalBoProto_pb2.BaseRespProto
    }


def create_message(pb_instance, command, key, pb_name, body):
    """
    消息内容填充、序列化、打包
    """
    if body:
        [setattr(pb_instance, k, v) for k, v in body.items() if v is not None]
    data = pb_instance.SerializeToString()
    message = msg_pack(command, key, pb_name, data)

    return message


def decode_message(pb_name, pb_body):
    """
    消息解码
    """
    pb = ProtoBuffers.get(pb_name.decode('utf8'))
    if not pb:
        raise RuntimeError('该消息类型无法解码：{}'.format(pb_name))
    pb_instance = pb()
    try:
        pb_instance.ParseFromString(pb_body)
    except TypeError:
        return None
    else:
        # return pb_instance
        json_string_request = MessageToJson(pb_instance, preserving_proto_field_name=True)
        return json.loads(json_string_request)


def get_bind_message(token: str, key: str, user_info: dict, device_info: dict):
    """
    用户绑定消息
    """
    if token:
        body = {
            'app_id': user_info['app_id'],
            'user_id': user_info['user_id'],
            'token': token,
            'manufacturer': device_info['manufacturer'],
            'device_id': device_info['device_id'],
            'os_version': device_info['os_version']
        }
        pb = MessageProBuf_pb2.ReqBindUserChannel()
        message = create_message(pb, CommandType.COMMAND_BIND_USER.value, key, 'ReqBindUserChannel', body)
        return message
    else:
        return None


IMG_INFO = [
    {
            'file_name': 'mmexport1606175063254.jpg',
            'file_size': 28056,
            'file_uri': 'http://mgim-demo.files.zhuanxin.com/other/e16a589a4e1bfe35db36d93cfb428425.jpg',
            'file_suffix': '.jpg',
            'image_width': 690,
            'image_height': 690,
            'file_md5': '22de233764246068452798f3c4dde022'
    },
    {
            'file_name': 'c9f0af0dce59fa5fcd7ea878f65579cc.jpg',
            'file_size': 125596,
            'file_uri': 'http://mgim-sdk-dev.zhuanxin.com/other/9d934dce2316b70a217dcffc5e6ef433.jpg',
            'file_suffix': 'jpg',
            'image_width': 400,
            'image_height': 400,
            'file_md5': 'c9f0af0dce59fa5fcd7ea878f65579cc'
    },
    {
        'file_name': 'a67fcf905bd481d7bed714dc37a2df8f.gif',
        'file_size': 572652,
        'file_uri': 'http://mgim-sdk-dev.zhuanxin.com/other/6c507adbab87a57ca355bea637782c06.gif',
        'file_suffix': '.gif',
        'image_width': 1038,
        'image_height': 1036,
        'file_md5': 'a215f8b50d173907938dc27d006fd5ea'
    },
    {
        'file_name': '1585488076670933.png',
        'file_size': 115726,
        'file_uri': 'http://mgim-sdk-dev.zhuanxin.com/other/fc34dc6c39cb3426fa10da666fa3e0e6.png',
        'file_suffix': '.png',
        'image_width': 980,
        'image_height': 398,
        'file_md5': 'a637a09d72cd62abc00b74f93a094612'
    }
]


def set_img_msg_file(pb):
    msg_pb = pb.msg_file
    _img_info = choice(IMG_INFO)
    for k, v in _img_info.items():
        setattr(msg_pb, k, v)
    # return pb.SerializeToString()
    # return info


'''
线上环境的文件消息
'''
FILE_INFO = [
    {'file_name': '2020-11-27-20-54.tar.gz', 'file_size': 300472, 'file_uri': 'http://mgim-sdk.zhuanxin.com/other/3464b5528bbff24b0520d693fca0f99c.gz', 'file_suffix': 'gz', 'file_md5': '83449f3dca7568265766d5418e8d973f'},
    {'file_name': '1.mp3', 'file_size': 5056888, 'file_uri': 'http://mgim-sdk.zhuanxin.com/other/b18b0d554dd011fa059a249929cfb781.mp3', 'file_suffix': 'mp3', 'file_md5': '4b10c67ef1959433b9ac9280b9698156'},
    {'file_name': '单聊场景网络切换测试结果.xls', 'file_size': 22016, 'file_uri': 'http://mgim-sdk.zhuanxin.com/other/06183d8ed939ed1d06596d5aaad317aa.xls', 'file_suffix': 'xls', 'file_md5': '5f7b0b2ee9e9a643100947b84fa72fa1'},
    {'file_name': '会合APP需求说明书_20200619(1)(1).doc', 'file_size': 3463841, 'file_uri': 'http://mgim-sdk.zhuanxin.com/other/3ad54547584f91c28864e010fb3acdc7.doc', 'file_suffix': '.doc', 'file_md5': '7aadf72b623bc12e2332c368f8ec31a6'},
    {'file_name': '2021年01月23日产品发布清单.pdf', 'file_size': 35576, 'file_uri': 'http://mgim-sdk.zhuanxin.com/other/fabb2cefe3efa4079f05e3863b00002f.pdf', 'file_suffix': 'pdf', 'file_md5': 'a91ff471564292149ceea9a5fd7fe7bd'},
    {'file_name': '会合专信交流对接项目组.pptx', 'file_size': 6572453, 'file_uri': 'http://mgim-sdk.zhuanxin.com/other/b9c25c2b2513d0f1f6d392318b7c60a4.pptx', 'file_suffix': 'pptx', 'file_md5': '7565ae21608d87991fe6fe793ab383cc'}
]
'''
dev环境的文件消息
'''
# FILE_INFO = [
#     {'file_name': 'IM项目周报-20201225(1).pdf', 'file_size': 301979, 'file_uri': 'http://mgim-sdk-dev.zhuanxin.com/other/ea0baaf172c5444f92adbe045f1fef4d.pdf', 'file_suffix': 'pdf', 'file_md5': '461039b5a6931edcfd7eb1534ac866b9'},
#     {'file_name': '群聊消息优化_测试场景.xlsx', 'file_size': 13696, 'file_uri': 'http://mgim-sdk-dev.zhuanxin.com/other/2bc332b8daf9cc2bd041e4921f35088a.xlsx', 'file_suffix': 'xlsx', 'file_md5': '5bac094ee5264b182e569f3eb5fce4dd'},
#     {'file_name': '1.mp3', 'file_size': 5056888, 'file_uri': 'http://mgim-sdk-dev.zhuanxin.com/other/b18b0d554dd011fa059a249929cfb781.mp3', 'file_suffix': 'mp3', 'file_md5': '4b10c67ef1959433b9ac9280b9698156'},
#     {'file_name': '核心接口文档.docx', 'file_size': 43497, 'file_uri': 'http://mgim-sdk-dev.zhuanxin.com/other/b904d4794c1cc97299c8546ba5e4714f.docx', 'file_suffix': 'docx', 'file_md5': 'bd60ac6a613c2ac1cf3af3e73a5571ee'},
#     {'file_name': 'b9c25c2b2513d0f1f6d392318b7c60a4.pptx', 'file_size': 6572453, 'file_uri': 'http://mgim-sdk-dev.zhuanxin.com/other/b9c25c2b2513d0f1f6d392318b7c60a4.pptx', 'file_suffix': 'pptx', 'file_md5': '7565ae21608d87991fe6fe793ab383cc'},
#     {'file_name': '3464b5528bbff24b0520d693fca0f99c.gz', 'file_size': 300472, 'file_uri': 'http://mgim-sdk-dev.zhuanxin.com/other/3464b5528bbff24b0520d693fca0f99c.gz', 'file_suffix': 'gz', 'file_md5': '83449f3dca7568265766d5418e8d973f'}
# ]

VIDEO_INFO = [
    {
        'file_name': 'c8e03ff4-278c-11ea-a37a-965276b5d811.mp4',
        'file_pic': 'http://mgim-sdk-dev.zhuanxin.com/other/4e3a6cb05fba798c641a8b69e94a6ed5.jpg',
        'file_size': 1678210,
        'file_uri': 'http://mgim-sdk-dev.zhuanxin.com/other/52116e73840a5ce4587c23d4b1f017b2.mp4',
        'file_suffix': '.mp4',
        'file_duration': 26640,
        'file_md5': '52116e73840a5ce4587c23d4b1f017b2'
    }
]

LOCATION_INFO = [
    {'latitude': 22.535839, 'longitude': 113.953115, 'address': '广东省深圳市南山区科技园高新南六道10号', 'pic_url': 'http://mgim-sdk.zhuanxin.com/other/fd2365ade4492cdc0695c1c8db2f5ba0.jpg', 'name': '朗科大厦'}
]


EMOJI_INFO = [
    {'emoji_id': 'waiwai-4', 'emoji_group': 'waiwai', 'emoji_url': 'http://dev-im-sdk.phh4.com/imoji/b7b6812e484c4f6a1de2c2a61e738f94.jpg', 'width': 319, 'height': 274},
    {'emoji_id': 'ggy-5', 'emoji_group': 'guaiguaiyang1', 'emoji_url': 'http://dev-im-sdk.phh4.com/emoji/ggy/ggy-5.gif', 'width': 300, 'height': 300},
    {'emoji_id': 'ggy-7', 'emoji_group': 'guaiguaiyang1', 'emoji_url': 'http://dev-im-sdk.phh4.com/emoji/ggy/ggy-7.jpg', 'width': 300, 'height': 300},
    {'emoji_id': 'ggy-3', 'emoji_group': 'guaiguaiyang1', 'emoji_url': 'http://dev-im-sdk.phh4.com/emoji/ggy/ggy-3.gif', 'width': 300, 'height': 300},
    {'emoji_id': 'ggy-2', 'emoji_group': 'guaiguaiyang1', 'emoji_url': 'http://dev-im-sdk.phh4.com/emoji/ggy/ggy-3.gif', 'width': 300, 'height': 300},
    {'emoji_id': 'ggy-8', 'emoji_group': 'guaiguaiyang1', 'emoji_url': 'http://dev-im-sdk.phh4.com/emoji/ggy/ggy-8.gif', 'width': 300, 'height': 300},
    {'emoji_id': 'ggy-1', 'emoji_group': 'guaiguaiyang1', 'emoji_url': 'http://dev-im-sdk.phh4.com/emoji/ggy/ggy-1.jpg', 'width': 300, 'height': 300},
    {'emoji_id': 'ggy-6', 'emoji_group': 'guaiguaiyang1', 'emoji_url': 'http://dev-im-sdk.phh4.com/emoji/ggy/ggy-6.gif', 'width': 300, 'height': 300},
    {'emoji_id': 'waiwai-1', 'emoji_group': 'waiwai', 'emoji_url': 'http://dev-im-sdk.phh4.com/imoji/f660a54a55227c154e9694caa8aece57.jpg', 'width': 240, 'height': 240},
    {'emoji_id': 'waiwai-6', 'emoji_group': 'waiwai', 'emoji_url': 'http://dev-im-sdk.phh4.com/imoji/a5ca61f015f84c3a7a75237fbf6f0613.jpg', 'width': 240, 'height': 240},
    {'emoji_id': 'waiwai-5', 'emoji_group': 'waiwai', 'emoji_url': 'http://dev-im-sdk.phh4.com/imoji/b76391faab6d0e3db10ec2212c3bd994.gif', 'width': 300, 'height': 300},
    {'emoji_id': 'waiwai-4', 'emoji_group': 'waiwai', 'emoji_url': 'http://dev-im-sdk.phh4.com/imoji/b7b6812e484c4f6a1de2c2a61e738f94.jpg', 'width': 319, 'height': 274},
    {'emoji_id': 'waiwai-7', 'emoji_group': 'waiwai', 'emoji_url': 'http://dev-im-sdk.phh4.com/imoji/4f808293e68383d40418054b2bbb7479.jpg', 'width': 300, 'height': 300},
    {'emoji_id': 'waiwai-8', 'emoji_group': 'waiwai', 'emoji_url': 'http://dev-im-sdk.phh4.com/imoji/4d40464e5f98aec5f7a1521502337670.jpg', 'width': 300, 'height': 300},
    {'emoji_id': 'waiwai-2', 'emoji_group': 'waiwai', 'emoji_url': 'http://dev-im-sdk.phh4.com/imoji/ff5e3bf48cdb3fcb84c418d1711a5df5.gif', 'width': 300, 'height': 300},
    {'emoji_id': 'waiwai-3', 'emoji_group': 'waiwai', 'emoji_url': 'http://dev-im-sdk.phh4.com/imoji/c95efd9d38fd370b13467c0d2b89fc95.gif', 'width': 300, 'height': 300}
]


AUDIO_INFO = [
    {'file_name': 'voice.aac', 'file_size': 51419, 'file_uri': 'http://mgim-sdk.zhuanxin.com/other/75b4639bb9077017e6e2a9844f792c20.aac', 'file_suffix': 'aac', 'file_duration': 6, 'file_md5': '79ba87f7daa8206d68288c61f8eeb433'}
]


def set_video_msg_file(pb):
    msg_pb = pb.msg_file
    _file_info = choice(VIDEO_INFO)
    for k, v in _file_info.items():
        setattr(msg_pb, k, v)


def set_msg_emoji(pb):
    emoji_pb = pb.msg_emoji
    _emoji_info = choice(EMOJI_INFO)
    for k, v in _emoji_info.items():
        setattr(emoji_pb, k, v)


def set_msg_location(pb):
    location_pb = pb.msg_location
    _location_info = choice(LOCATION_INFO)
    for k, v in _location_info.items():
        setattr(location_pb, k, v)


def set_audio_msg_file(pb):
    msg_pb = pb.msg_file
    _file_info = choice(AUDIO_INFO)
    for k, v in _file_info.items():
        setattr(msg_pb, k, v)


def set_file_msg_file(pb):
    msg_pb = pb.msg_file
    _file_info = choice(FILE_INFO)
    for k, v in _file_info.items():
        setattr(msg_pb, k, v)


def get_communication_message_by_single(msg_type, key, app_id, user_id, target_id, communication_id, content=None, other=None):
    """
    生成单聊消息
    :param msg_type:
    :param key:
    :param app_id:
    :param user_id:
    :param target_id:
    :param communication_id:
    :param content:
    :param other:用户信息，如头像链接，id，昵称等
    :return:
    """
    _time_stamp = get_time_stamp()

    body = {
        'app_id': app_id,
        'from_user_id': user_id,
        'to_user_id': target_id,
        'communication_id': communication_id,
        'send_time': _time_stamp,
        'communication_type': CommunicationType.SINGLE_PERSON.value,
        'message_type': msg_type,
        'message_main_type': 1,
        # 'content': content,
        # 'setting': '{"read":false,"arrived":false,"read_delete":false,"dont_disturb":false}',
        'tag': device_id_gen()
    }
    # print('msg tag', body['tag'])

    if other is not None:
        body['other'] = other

    pb = MessageProBuf_pb2.CommunicationMessageProto()

    if msg_type == 1:   # 文本
        body['content'] = content
    elif msg_type == 2:  # 表情
        set_msg_emoji(pb)
    elif msg_type == 3:    # 文件
        body['setting'] = '{"read":false,"arrived":false,"read_delete":false,"dont_disturb":false}'
        set_file_msg_file(pb)
    elif msg_type == 4:    # 图片
        set_img_msg_file(pb)
        body['setting'] = '{"read":false,"arrived":false,"read_delete":false,"dont_disturb":false}'
    elif msg_type == 5:    # 语音消息
        set_audio_msg_file(pb)
    elif msg_type == 6:  # 视频
        body['setting'] = '{"read":false,"arrived":false,"read_delete":false,"dont_disturb":false}'
        set_video_msg_file(pb)
    elif msg_type == 7:  # 位置消息
        set_msg_location(pb)
        body['content'] = pb.msg_location.address
    message = create_message(pb, CommandType.COMMAND_SEND_MSG_REQ.value, key, 'CommunicationMessageProto', body)
    return message


def get_communication_message_by_group(msg_type, key, app_id, user_id, communication_id, content=None, other=None):
    """
    生成群聊消息
    :param msg_type:
    :param key:
    :param app_id:
    :param user_id:
    :param communication_id:
    :param content:
    :param other:用户信息，如头像链接，id，昵称等
    :return:
    """
    body = {
        'app_id': app_id,
        'from_user_id': user_id,
        'communication_id': communication_id,
        'send_time': get_time_stamp(),
        'communication_type': 2,
        'message_type': msg_type,
        'message_main_type': 1,
        'tag': device_id_gen()
    }

    if other is not None:
        body['other'] = other

    pb = MessageProBuf_pb2.CommunicationMessageProto()
    if msg_type == 1:   # 文本
        body['content'] = content
    elif msg_type == 2:  # 表情
        set_msg_emoji(pb)
    elif msg_type == 3:    # 文件
        body['setting'] = '{"read":false,"arrived":false,"read_delete":false,"dont_disturb":false}'
        set_file_msg_file(pb)
    elif msg_type == 4:    # 图片
        set_img_msg_file(pb)
        body['setting'] = '{"read":false,"arrived":false,"read_delete":false,"dont_disturb":false}'
    elif msg_type == 5:    # 语音消息
        set_audio_msg_file(pb)
    elif msg_type == 6:  # 视频
        body['setting'] = '{"read":false,"arrived":false,"read_delete":false,"dont_disturb":false}'
        set_video_msg_file(pb)
    elif msg_type == 7:  # 位置消息
        set_msg_location(pb)
        body['content'] = pb.msg_location.address
    message = create_message(pb, CommandType.COMMAND_SEND_MSG_REQ.value, key, 'CommunicationMessageProto', body)
    return message


def get_communication_message_by_chat_room(msg_type, key, app_id, user_id, communication_id, content=None, other=None):
    """
    生成聊天室消息
    """
    body = {
        'app_id': app_id,
        'from_user_id': user_id,
        'communication_id': communication_id,
        'send_time': get_time_stamp(),
        'communication_type': 3,
        'message_type': msg_type,
        'message_main_type': 1,
        'tag': device_id_gen()
    }

    if other is not None:
        body['other'] = other
    pb = MessageProBuf_pb2.CommunicationMessageProto()
    if msg_type == MessageType.TEXT.value:      # 文本
        body['content'] = content
    elif msg_type == MessageType.EMOJI.value:    # 动图表情
        set_msg_emoji(pb)
    elif msg_type == MessageType.FILE.value:    # 文件
        set_file_msg_file(pb)
        body['setting'] = '{"read":false,"arrived":false,"read_delete":false,"dont_disturb":false}'
    elif msg_type == MessageType.IMAGE.value:    # 图片
        set_img_msg_file(pb)
        body['setting'] = '{"read":false,"arrived":false,"read_delete":false,"dont_disturb":false}'
    elif msg_type == MessageType.AUDIO.value:    # 语音消息
        body['setting'] = '{"read":false,"arrived":false}'
        set_audio_msg_file(pb)
    elif msg_type == MessageType.VIDEO.value:     # 视频
        body['setting'] = '{"read":false,"arrived":false,"read_delete":false,"dont_disturb":false}'
        set_video_msg_file(pb)
    elif msg_type == MessageType.ADDRESS.value:     # 位置消息
        set_msg_location(pb)
        body['content'] = pb.msg_location.address
    message = create_message(pb, CommandType.COMMAND_SEND_MSG_REQ.value, key, 'CommunicationMessageProto', body)
    return message
    
    
def get_heartbeat_message(key, from_id=None, device_type=None, manufacturer=None, last_msg_sequence_id=0, last_msg_receive_time='', version=None, interface_up_time=None):
    # 发送请求消息响应只要三个参数device_type, last_msg_sequence_id, last_msg_receive_time 就可以
    """
    string from_id = 1;                         //发送人id
    int32 device_type = 2;                      //设备类型  1：移动端，2：WEB端，3：PC端
    int32 manufacturer = 3;                		//设备厂商 0=谷歌;1=苹果; 2=华为;3=小米;4=OPPO;5=魅族;6=VIVO;7=其他;
    int64 last_msg_sequence_id = 4;             //序列id
    int64 last_msg_receive_time = 5;            //最大时间
    string version = 6;                         //版本号
    int64 interface_up_time = 7;                //客户端接口升级时间戳
    """
    body = {
        'from_id': from_id,
        'device_type': device_type,
        'manufacturer': manufacturer,
        'last_msg_sequence_id': last_msg_sequence_id,
        'last_msg_receive_time': last_msg_receive_time,
        'version': version,
        'interface_up_time': interface_up_time
    }
    # print(body)
    pb = MessageProBuf_pb2.HeartBeatMsg()
    command_key = CommandType.COMMAND_PULL_MSG_REQ.value
    message = create_message(pb, command_key, key, 'HeartBeatMsg', body)
    return message
    
    
def decode_communication_message(proto_name, proto_body):
    """
    聊天消息解码
    """
    proto_body = aes_decrypt(proto_body)
    message = decode_message(proto_name, proto_body)
    return message


def get_msg_ack_message(key, app_id, from_user_id, to_user_id, communication_id, message_id, tag, last_receive_msg_no=None):
    """
    获取ack msg
    :param key:
    :param app_id:
    :param from_user_id:
    :param to_user_id:
    :param communication_id:
    :param message_id:
    :param tag:
    :param last_receive_msg_no:群消息的id序号,单聊不用此参数
    :return: bin data
    """
    pb = MessageProBuf_pb2.MessageAckProto()
    body = {
        'message_id': message_id,
        'app_id': app_id,
        'msg_from_user_id': from_user_id,
        'msg_to_user_id': to_user_id,
        'communication_id': communication_id,
        'tag': tag
    }
    command_key = CommandType.COMMAND_MESSAGE_ACK.value
    if last_receive_msg_no:
        body['last_receive_msg_no'] = last_receive_msg_no	
        command_key = CommandType.COMMAND_MESSAGE_ACK.value
    message = create_message(pb, command_key, key, 'MessageAckProto', body)
    return message


def get_msg_read_message(key, app_id, from_user_id, to_user_id, communication_id, message_id, tag, last_receive_msg_no=None):
    """
    聊天消息解码
    """
    pb = MessageProBuf_pb2.MessageAckProto()
    body = {
        'message_id': message_id,
        'app_id': app_id,
        'msg_from_user_id': from_user_id,
        'msg_to_user_id': to_user_id,
        'communication_id': communication_id,
        'tag': tag
    }
    command_key = CommandType.COMMAND_MESSAGE_READ.value
    if last_receive_msg_no:
        body['last_receive_msg_no'] = last_receive_msg_no	
        command_key = CommandType.COMMAND_MESSAGE_READ.value
    message = create_message(pb, command_key, key, 'MessageAckProto', body)
    return message
    
    
if __name__ == '__main__':
    # buffer1 = get_heartbeat_message('asdasdasd',  device_type=1, last_msg_receive_time='123', last_msg_sequence_id=0)
    # print(buffer1)
    # print(len(buffer1))
    # head = buffer1[0:5]
    # print(head[4])
    # buffer = buffer1[5:]
    # key_len = buffer[0]
    # key = buffer[1: 1+key_len]
    # protoname_len = buffer[1+key_len]
    # protoname = buffer[2+key_len: 2+key_len+protoname_len]
    # proto_body = buffer[2+key_len+protoname_len:]
    # print(protoname)
    r = decode_communication_message(b'BaseRespProto', b'i\xee\xc7\x08\xf6\x0c\x01\x1a\x0c\x1b\x8cp\xedz3\x99\xa87oA\xd0\xfeZX\x1c\x0e\xf2\xda;,\xdbd')
    print(r)
