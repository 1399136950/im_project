# -*- coding:utf-8 -*-
# @author  : ywt
# @file   : chat_room_management.py
# @ide    : PyCharm
# @time    : 2021/6/7 8:53
import requests

from config.conf import HOST


def chat_room_announcement_get(token, chat_room_id):
    """
    获取聊天室公告接口
    :param token:           鉴权token值                    True        string
    :param chat_room_id:    聊天室ID                       True        string
    :return:                返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/chatroom/announcement/get'
    headers = {
        'access_token': token
    }
    payload = {"chatRoomId": chat_room_id}
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


def chat_room_announcement_update(token, chat_room_id, announcement=None):
    """
    设置公告接口
    :param token:           鉴权token值                    True        string
    :param chat_room_id:    聊天室ID                       True        string
    :param announcement:    公告                           False       string
    :return:                返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/chatroom/announcement/update'
    headers = {
        'access_token': token
    }
    payload = {"chatRoomId": chat_room_id}
    if announcement is not None:
        payload["announcement"] = announcement
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


def chat_room_assignment(token, chat_room_id, owner_id):
    """
    聊天室转让接口
    :param token:           鉴权token值                True        string
    :param chat_room_id:    聊天室 ID                  True        string
    :param owner_id:        要转让的聊天室用户ID         True        string
    :return:                返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/chatroom/assignment'
    headers = {
        'access_token': token
    }
    payload = {"chatRoomId": chat_room_id, "ownerId": owner_id}
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


def chat_room_black_list(token, chat_room_id):
    """
    聊天室黑名单列表接口
    :param token:           鉴权token值                True        string
    :param chat_room_id:    聊天室 ID                  True        string
    :return:                返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/chatroom/black/list'
    headers = {
        'access_token': token
    }
    payload = {"chatRoomId": chat_room_id}
    reps = requests.get(url, headers=headers, params=payload, timeout=5)
    return reps.json()


def chat_room_create(token, chat_room_name=None, description=None):
    """
    创建聊天室接口
    :param token:           鉴权token值         True        string
    :param chat_room_name:  聊天室名称           False       string
    :param description:     聊天室描述           False       string
    :return:
    """
    url = HOST + '/sdk/v1/chatroom/create'
    headers = {
        'access_token': token
    }
    payload = {}
    if chat_room_name is not None:
        payload["chatRoomName"] = chat_room_name
    if description is not None:
        payload["description"] = description
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


def chat_room_description_update(token, chat_room_id, description):
    """
    更新聊天室描述接口
    :param token:           鉴权token值         True        string
    :param chat_room_id:    聊天室ID            True        string
    :param description:     聊天室描述（签名）    True        string
    :return:
    """
    url = HOST + '/sdk/v1/chatroom/description/update'
    headers = {
        'access_token': token
    }
    payload = {"chatRoomId": chat_room_id, "description": description}
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


def chat_room_detail(token, chat_room_id):
    """
    查询聊天室详情接口
    :param token:           鉴权token值         True        string
    :param chat_room_id:    聊天室ID            True        string
    :return:
    """
    url = HOST + '/sdk/v1/chatroom/detail'
    headers = {
        'access_token': token
    }
    payload = {"chatRoomId": chat_room_id}
    reps = requests.get(url, headers=headers, params=payload, timeout=5)
    return reps.json()


def chat_room_detail_list(token, chat_room_ids):
    """
    查询聊天室详情接口
    :param token:           鉴权token值                      True        string
    :param chat_room_ids:   聊天室ID，以逗号分割， 如1,2,3,4    True        string
    :return:
    """
    url = HOST + '/sdk/v1/chatroom/detail/list'
    headers = {
        'access_token': token
    }
    payload = {"chatRoomIds": chat_room_ids}
    reps = requests.get(url, headers=headers, params=payload, timeout=5)
    return reps.json()


def chat_room_enter(token, chat_room_id):
    """
    进入聊天室接口
    :param token:           鉴权token值         True        string
    :param chat_room_id:    聊天室 ID           True        string
    :return:
    """
    url = HOST + '/sdk/v1/chatroom/enter'
    headers = {
        'access_token': token
    }
    payload = {"chatRoomId": chat_room_id}
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


def chat_room_exit(token, chat_room_id):
    """
    用户离开聊天室接口
    :param token:           鉴权token值         True        string
    :param chat_room_id:    聊天室 ID           True        string
    :return:
    """
    url = HOST + '/sdk/v1/chatroom/exit'
    headers = {
        'access_token': token
    }
    payload = {"chatRoomId": chat_room_id}
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


def chat_room_list_mine(token):
    """
    获取用户聊天室列表接口
    :param token:           鉴权token值         True        string
    :return:
    """
    url = HOST + '/sdk/v1/chatroom/list/mine'
    headers = {
        'access_token': token
    }
    reps = requests.get(url, headers=headers, timeout=5)
    return reps.json()


def chat_room_list_public(token, count=None, create_time=None):
    """
    获取聊天室列表接口
    :param token:           鉴权token值                        True        string
    :param count:           一次拉取列表数量                     False       integer(int32)
    :param create_time:     上次拉取的列表的最后一条的创建时间      False        integer(int64)
    :return:
    """
    url = HOST + '/sdk/v1/chatroom/list/public'
    headers = {
        'access_token': token
    }
    payload = {}
    if count is not None:
        payload["count"] = count
    if create_time is not None:
        payload["createTime"] = create_time
    reps = requests.get(url, headers=headers, params=payload, timeout=5)
    return reps.json()


def chat_room_manager_list(token, chat_room_id):
    """
    管理员列表接口
    :param token:           鉴权token值        True        string
    :param chat_room_id:    聊天室ID           True        string
    :return:
    """
    url = HOST + '/sdk/v1/chatroom/manager/list'
    headers = {
        'access_token': token
    }
    payload = {"chatRoomId": chat_room_id}
    reps = requests.get(url, headers=headers, params=payload, timeout=5)
    return reps.json()


def chat_room_manager_multi_add(token, chat_room_id, manager_ids):
    """
    新增管理员，多人接口
    :param token:           鉴权token值                True        string
    :param chat_room_id:    聊天室ID                   True        string
    :param manager_ids:     管理员用户ID集合，用逗号隔开   True        string
    :return:
    """
    url = HOST + '/sdk/v1/chatroom/manager/multi/add'
    headers = {
        'access_token': token
    }
    payload = {"chatRoomId": chat_room_id, "managerIds": manager_ids}
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


def chat_room_manager_multi_remove(token, chat_room_id, manager_ids):
    """
    移除多个管理员接口
    :param token:           鉴权token值                True        string
    :param chat_room_id:    聊天室ID                   True        string
    :param manager_ids:     管理员用户ID集合，用逗号隔开   True        string
    :return:
    """
    url = HOST + '/sdk/v1/chatroom/manager/multi/remove'
    headers = {
        'access_token': token
    }
    payload = {"chatRoomId": chat_room_id, "managerIds": manager_ids}
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


def chat_room_member_list(token, chat_room_id, count=None, create_time=None):
    """
    分页获取聊天室成员列表接口
    :param token:           鉴权token值                    True        string
    :param chat_room_id:    聊天室ID                       True        string
    :param count:           一次拉取列表数量                 False       integer(int32)
    :param create_time:     上次拉取的列表的最后一条的创建时间  False       integer(int64)
    :return:
    """
    url = HOST + '/sdk/v1/chatroom/member/list'
    headers = {
        'access_token': token
    }
    payload = {"chatRoomId": chat_room_id}
    if count is not None:
        payload["count"] = count
    if create_time is not None:
        payload["createTime"] = create_time
    reps = requests.get(url, headers=headers, params=payload, timeout=5)
    return reps.json()


def chat_room_member_remove(token, chat_room_id, user_ids):
    """
    聊天室管理踢人接口
    :param token:           鉴权token值                    True        string
    :param chat_room_id:    聊天室ID                       True        string
    :param user_ids:        聊天室用户ID集合，用逗号隔开      True        string
    :return:
    """
    url = HOST + '/sdk/v1/chatroom/member/remove'
    headers = {
        'access_token': token
    }
    payload = {"chatRoomId": chat_room_id, "userIds": user_ids}
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


def chat_room_mute_all(token, chat_room_id, mutable):
    """
    开启和关闭全员禁言接口
    :param token:           鉴权token值                    True        string
    :param chat_room_id:    聊天室ID                       True        string
    :param mutable:         是否全员禁言                    True        boolean
    :return:
    """
    url = HOST + '/sdk/v1/chatroom/mute/all'
    headers = {
        'access_token': token
    }
    payload = {"chatRoomId": chat_room_id, "mutable": mutable}
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


def chat_room_name_update(token, chat_room_id, chat_room_name):
    """
    修改聊天室名称接口
    :param token:           鉴权token值                    True        string
    :param chat_room_id:    聊天室ID                       True        string
    :param chat_room_name:  聊天室名称                      True        string
    :return:
    """
    url = HOST + '/sdk/v1/chatroom/name/update'
    headers = {
        'access_token': token
    }
    payload = {"chatRoomId": chat_room_id, "chatRoomName": chat_room_name}
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


def chat_room_remove(token, chat_room_id):
    """
    解散聊天室（删除聊天室）接口
    :param token:           鉴权token值                    True        string
    :param chat_room_id:    聊天室ID                       True        string
    :return:
    """
    url = HOST + '/sdk/v1/chatroom/remove'
    headers = {
        'access_token': token
    }
    payload = {"chatRoomId": chat_room_id}
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


def chat_room_remove_all(token):
    """
    解散当前用户所有的聊天室
    :param token:           鉴权token值                    True        string
    :return:
    """
    while 1:
        reps = chat_room_list_mine(token)
        chat_room_ids = [i['communicationId'] for i in reps['data']]
        if not chat_room_ids:
            break
        for chat_room_id in chat_room_ids:
            reps = chat_room_remove(token, chat_room_id)
            print(reps)


def chat_room_user_black_multi_remove(token, chat_room_id, user_ids):
    """
    移出黑名单接口
    :param token:           鉴权token值                    True        string
    :param chat_room_id:    聊天室ID                       True        string
    :param user_ids:        聊天室成员用户ID                True        string
    :return:
    """
    url = HOST + '/sdk/v1/chatroom/user/black/multi/remove'
    headers = {
        'access_token': token
    }
    payload = {"chatRoomId": chat_room_id, "userIds": user_ids}
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


def chat_room_user_multi_black(token, chat_room_id, user_ids):
    """
    批量加入黑名单接口
    :param token:           鉴权token值                    True        string
    :param chat_room_id:    聊天室ID                       True        string
    :param user_ids:        成员用户ID集合                  True        string
    :return:
    """
    url = HOST + '/sdk/v1/chatroom/user/multi/black'
    headers = {
        'access_token': token
    }
    payload = {"chatRoomId": chat_room_id, "userIds": user_ids}
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


def chat_room_user_multi_list(token, chat_room_id):
    """
    获取禁言成员列表接口
    :param token:           鉴权token值                    True        string
    :param chat_room_id:    聊天室ID                       True        string
    :return:
    """
    url = HOST + '/sdk/v1/chatroom/user/multi/list'
    headers = {
        'access_token': token
    }
    payload = {"chatRoomId": chat_room_id}
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


def chat_room_user_multi_mute(token, chat_room_id, user_ids):
    """
    多人禁言接口
    :param token:           鉴权token值                    True        string
    :param chat_room_id:    聊天室ID                       True        string
    :param user_ids:        用户ID                         True        string
    :return:
    """
    url = HOST + '/sdk/v1/chatroom/user/multi/mute'
    headers = {
        'access_token': token
    }
    payload = {"chatRoomId": chat_room_id, "userIds": user_ids}
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


def chat_room_user_multi_mute_relieve(token, chat_room_id, user_ids):
    """
    解除禁言，多人接口
    :param token:           鉴权token值                            True        string
    :param chat_room_id:    聊天室ID                               True        string
    :param user_ids:        聊天室用户ID集合，用逗号隔开，如1,2,3,4,5   True        string
    :return:
    """
    url = HOST + '/sdk/v1/chatroom/user/multi/mute/relieve'
    headers = {
        'access_token': token
    }
    payload = {"chatRoomId": chat_room_id, "userIds": user_ids}
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


def chat_room_user_mute_white_add(token, chat_room_id, user_ids):
    """
    添加禁言白名单接口
    :param token:           鉴权token值                            True        string
    :param chat_room_id:    聊天室ID                               True        string
    :param user_ids:        用户ID                                 True        string
    :return:
    """
    url = HOST + '/sdk/v1/chatroom/user/mutewhite/add'
    headers = {
        'access_token': token
    }
    payload = {"chatRoomId": chat_room_id, "userIds": user_ids}
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


def chat_room_user_mute_white_check(token, chat_room_id):
    """
    查看自己是否在禁言白名单中接口
    :param token:           鉴权token值                            True        string
    :param chat_room_id:    聊天室ID                               True        string
    :return:
    """
    url = HOST + '/sdk/v1/chatroom/user/mutewhite/check'
    headers = {
        'access_token': token
    }
    payload = {"chatRoomId": chat_room_id}
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


def chat_room_user_mute_white_list(token, chat_room_id):
    """
    获取禁言白名单列表接口
    :param token:           鉴权token值                            True        string
    :param chat_room_id:    聊天室ID                               True        string
    :return:
    """
    url = HOST + '/sdk/v1/chatroom/user/mutewhite/list'
    headers = {
        'access_token': token
    }
    payload = {"chatRoomId": chat_room_id}
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


def chat_room_user_mute_white_relieve(token, chat_room_id, user_ids):
    """
    解除禁言白名单接口
    :param token:           鉴权token值                            True        string
    :param chat_room_id:    聊天室ID                               True        string
    :param user_ids:        聊天室用户ID集合，用逗号隔开，如1,2,3,4,5  True        string
    :return:
    """
    url = HOST + '/sdk/v1/chatroom/user/mutewhite/relieve'
    headers = {
        'access_token': token
    }
    payload = {"chatRoomId": chat_room_id, "userIds": user_ids}
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


if __name__ == '__main__':
    from config.conf import user1_info, user2_info, user3_info
    from lib.im_api_lib.login import login
    import time
    import pprint
    token_1 = login(user1_info)
    token_2 = login(user2_info)

    chat_room_remove_all(token_1)
    print(chat_room_list_mine(token_1))

    # res = chat_room_create(token_1,
    #                        chat_room_name=f"新建聊天室{int(time.time()*1000)}",
    #                        description=f"新建聊天室{int(time.time()*1000)}")

    res = chat_room_create(token_1,
                           chat_room_name="新建聊天室name",
                           description="新建聊天室description")
    print(res)