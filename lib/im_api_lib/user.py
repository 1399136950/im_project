# -*- coding:utf-8 -*-
# @author  : ywt
# @file   : user.py
# @ide    : PyCharm
# @time    : 2021/3/26 13:47
import os

import requests

from config.conf import HOST


def user_base_info_set(token, avatar=None, nickname=None, phone=None, sex=None):
    """
    设置基本信息接口
    :param token:       鉴权token值               True        string
    :param avatar:      头像，注意是图片地址        False       string
    :param nickname:    昵称                     False       string
    :param phone:       手机                     False       string
    :param sex:         性别1=male, 2=female     False       integer(int32)
    :return:            返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/user/baseinfo/set'
    headers = {
        'access_token': token
    }
    payload = {}
    if avatar is not None:
        payload["avatar"] = avatar
    if nickname is not None:
        payload["nickname"] = nickname
    if phone is not None:
        payload["phone"] = phone
    if sex is not None:
        payload["sex"] = sex
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


def user_avatar_update(token, file_path):
    """
    修改头像接口:直接覆盖原来OSS上面的用户头像，但是访问的时候需要特别注意，url后面添加一个时间戳
    支持jpeg  png   gif   *  几种格式的文件上传
    :param token:           鉴权token值               True        string
    :param file_path:       图片文件                  True        formData
    :return:                返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/user/avatar/update'
    headers = {
        'access_token': token
    }
    file_name = os.path.split(file_path)[-1]
    files = {"file": (file_name, open(file_path, 'rb'), 'image/*')}
    reps = requests.post(url, headers=headers, files=files, timeout=5)
    return reps.json()


def user_black_list(token):
    """
    黑名单列表接口
    :param token:       鉴权token值               True        string
    :return:            返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/user/black/list'
    headers = {
        'access_token': token
    }
    reps = requests.get(url, headers=headers, timeout=5)
    return reps.json()


def user_friend_black_multi(token, user_ids):
    """
    将好友加入黑名单，多人接口
    :param token:       鉴权token值               True        string
    :param user_ids:    要加入黑名单的用户ID        True        string
    :return:            返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/user/friend/black/multi'
    headers = {
        'access_token': token
    }
    payload = {"userIds": user_ids}
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


def user_friend_black_multi_remove(token, user_ids):
    """
    将好友移出黑名单,多人接口
    :param token:       鉴权token值                            True        string
    :param user_ids:    解除黑名单的好友用户ID集合，都逗号隔开      True        string
    :return:            返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/user/friend/black/multi/remove'
    headers = {
        'access_token': token
    }
    payload = {"userIds": user_ids}
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


def user_friend_black_multi_remove_all(token):
    """
    将所有人都移除黑名单
    :param token:       鉴权token值                            True        string
    :return:            None
    """
    try:
        reps = user_black_list(token)
        for i in reps['data']:
            user_friend_black_multi_remove(token, i['userId'])
    except Exception as e:
        raise Exception('清除操作异常') from e


def user_detail(token, user_id):
    """
    单用户信息接口
    :param token:       鉴权token值        True        string
    :param user_id:     用户ID             True        string
    :return:            返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/user/detail'
    headers = {
        'access_token': token
    }
    payload = {"userId": user_id}
    reps = requests.get(url, params=payload, headers=headers, timeout=5)
    return reps.json()


def user_friend_invite_auto_accept(token, auto):
    """
    设置自动加好友接口
    :param token:       鉴权token值        True        string
    :param auto:        是否自动加好友       False       boolean
    :return:            返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/user/friend/invite/auto/accept'
    headers = {
        'access_token': token
    }
    payload = {"auto": auto}
    reps = requests.get(url, params=payload, headers=headers, timeout=5)
    return reps.json()


def user_group_invite_auto_accept(token, auto):
    """
    设置自动接受群邀请接口
    :param token:       鉴权token值        True        string
    :param auto:        是否自动加好友       False       boolean
    :return:            返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/user/group/invite/auto/accept'
    headers = {
        'access_token': token
    }
    payload = {"auto": auto}
    reps = requests.get(url, params=payload, headers=headers, timeout=5)
    return reps.json()
    
    
def user_friend_del(token, user_id):
    """
    删除好友接口
    :param token:       鉴权token值        True        string
    :param user_id:     移除的好友的用户ID   True        string
    :return:            返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/user/friend/del'
    headers = {
        'access_token': token
    }
    payload = {"userId": user_id}
    reps = requests.post(url, data=payload, headers=headers, timeout=5)
    return reps.json()


def user_friend_del_all(token):
    """
    删除全部好友接口
    :param token:       鉴权token值        True        string
    :return:            返回返回体的字典格式
    """
    try:
        reps = user_friend_list(token)
        for i in reps['data']:
            user_friend_del(token, i['userId'])
    except Exception as e:
        raise Exception('清除操作异常') from e


def user_friend_add_req(token, user_id, remark=None, source=None):
    """
    请求添加好友接口
    :param token:       鉴权token值                                True        string
    :param user_id:     添加的好友的用户ID                           True        string
    :param remark:      邀请备注说明                                 False       string
    :param source:      来源：SEARCH=搜索；SCAN=扫码；GROUP=群组      False       string
    :return:            返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/user/friend/add/req'
    headers = {
        'access_token': token
    }
    payload = {"userId": user_id}
    if remark is not None:
        payload["remark"] = remark
    if source is not None:
        payload["source"] = source
    reps = requests.post(url, data=payload, headers=headers, timeout=5)
    return reps.json()


def user_friend_list(token):
    """
    好友列表接口
    :param token:       鉴权token值         True        string
    :return:            返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/user/friend/list'
    headers = {
        'access_token': token
    }
    reps = requests.get(url, headers=headers, timeout=5)
    return reps.json()


def user_friend_search(token, user_id):
    """
    查找好友接口
    :param token:       鉴权token值         True        string
    :param user_id:     用户ID              True        string
    :return:            返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/user/friend/search'
    headers = {
        'access_token': token
    }
    payload = {"userId": user_id}
    reps = requests.get(url, params=payload, headers=headers, timeout=5)
    return reps.json()


def user_setting_dont_disturb_detail(token, dont_disturb=None, dont_disturb_detail=None):
    """
    用户免打扰接口
    :param token:                   鉴权token值                             True        string
    :param dont_disturb:            是否免打扰                               False       boolean
    :param dont_disturb_detail:     免打扰详情，一天中的各种时间段，             false       string
                                    可以设置多个时间段（时间段本身‘-’隔开），
                                    各时间段分号隔开，
                                    如：7:00-8:00;12:00-13:00;22:00-24:00
    :return:                返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/user/setting/dontdisturb/detail'
    headers = {
        'access_token': token
    }
    payload = {}
    if dont_disturb is not None:
        payload["dont_disturb"] = dont_disturb
    if dont_disturb_detail is not None:
        payload["dontDisturbDetail"] = dont_disturb_detail
    reps = requests.post(url, data=payload, headers=headers, timeout=5)
    return reps.json()


def user_setting_dont_disturb(token, dont_disturb=None):
    """
    用户免打扰接口
    :param token:                   鉴权token值               True        string
    :param dont_disturb:            是否免打扰                 False       boolean
    """
    url = HOST + '/sdk/v1/user/setting/dontdisturb'
    headers = {
        'access_token': token
    }
    payload = {}
    if dont_disturb is not None:
        payload["dont_disturb"] = dont_disturb
    reps = requests.post(url, data=payload, headers=headers, timeout=5)
    return reps.json()


def user_search(token, keyword):
    """
    搜索用户接口：查询关键字，支持【手机，昵称，userId】完全匹配查询
    :param token:        鉴权token值                                   True        string
    :param keyword:      查询关键字，支持【手机，昵称，userId】完全匹配查询   True        string
    :return:             返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/user/search'
    headers = {
        'access_token': token
    }
    payload = {"keyword": keyword}
    reps = requests.post(url, data=payload, headers=headers, timeout=5)
    return reps.json()


def user_im_setting(token):
    """
    查询用户设置信息接口
    :param token:       鉴权token值        True        string
    :return:            返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/user/im/setting'
    headers = {
        'access_token': token
    }
    reps = requests.get(url, headers=headers, timeout=5)
    return reps.json()


def user_list(token, user_ids):
    """
    多用户信息接口
    :param token:           鉴权token值                    True        string
    :param user_ids:        用户ID列表，逗号隔开，如1,2,3,4   False       string
    :return:
    """
    url = HOST + '/sdk/v1/user/list'
    headers = {
        'access_token': token
    }
    payload = {"userIds": user_ids}
    reps = requests.get(url, params=payload, headers=headers, timeout=5)
    return reps.json()


def friend_attr_set(token, friend_id, key, value):
    """
    设置好友扩展
    :param token:       鉴权token值    True        string
    :param friend_id:   好友ID         True        string
    :param key:         扩展key        True        string
    :param value:       扩展value      True        string
    :return:
    """
    url = HOST + '/sdk/v1/user/friend/attr/set'
    headers = {
        'access_token': token
    }
    payload = {
        "friendId": friend_id,
        "key": key,
        "value": value
    }
    reps = requests.post(url, data=payload, headers=headers, timeout=5)
    return reps.json()


if __name__ == '__main__':
    from lib.im_api_lib.login import login
    user_info = {
        'password': '123456',
        'phone_num': '18163606916',
        'module_types': 'im',
        'platform': 'web',
        'version': '3.1.0',
        'user_id': '17jdewa7rxzyylirbiflt'
    }
    token_181 = login(user_info)
    user_setting_dont_disturb(token_181, True)
    # user_friend_invite_auto_accept(token_181, False)
    print(user_im_setting(token_181))
