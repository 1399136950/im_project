# -*- coding:utf-8 -*-
# @author  : ywt
# @file   : group_management.py
# @ide    : PyCharm
# @time    : 2021/4/6 18:05
import requests

from config.conf import HOST


def group_create_with_users(token, announcement=None, avatar=None, description=None,
                            group_name=None, invite_msg=None,
                            max_member_limit=None, options=None, user_ids=None):
    """
    拉人创建群组接口
    :param token:               鉴权token值                    True        string
    :param announcement:        群公告                         false       string
    :param avatar:              群头像                         false       string
    :param description:         群描述                         false       string
    :param group_name:          群名称                         false       string
    :param invite_msg:          邀请消息                       false        string
    :param  max_member_limit:   群成员最大数量                  false        integer(int32)
    :param options:             群设置                         false        string
    :param user_ids:            拉进的群成员ID集合，逗号隔开      false        string
    :return:                    返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/group/create/with/users'
    headers = {
        'access_token': token
    }
    payload = {}
    if announcement is not None:
        payload["announcement"] = announcement
    if avatar is not None:
        payload["avatar"] = avatar
    if description is not None:
        payload["description"] = description
    if group_name is not None:
        payload["groupName"] = group_name
    if invite_msg is not None:
        payload["inviteMsg"] = invite_msg
    if max_member_limit is not None:
        payload["maxMemberLimit"] = max_member_limit
    if options is not None:
        payload["options"] = options
    if user_ids is not None:
        payload["userIds"] = user_ids
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


def group_info_update(token, group_id, group_name):
    """
    修改群名称接口
    :param token:       鉴权token值        True    string
    :param group_id:    群组ID             True    string
    :param group_name:  群组名称            True    string
    :return:            返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/group/info/update'
    headers = {
        'access_token': token
    }
    payload = {"groupId": group_id, "groupName": group_name}
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


def group_info_description_update(token, group_id, description):
    """
    修改群描述接口
    :param token:           鉴权token值         True    string
    :param description:     群组描述            True    string
    :param group_id:        群组ID             True    string
    :return:                返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/group/info/description/update'
    headers = {
        'access_token': token
    }
    payload = {"description": description, "groupId": group_id}
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


def group_list_mine(token):
    """
    获取用户加入的，或者是创建的所有的群列表接口
    :param token:       鉴权token值         True    string
    :return:            返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/group/list/mine'
    headers = {
        'access_token': token
    }
    reps = requests.get(url, headers=headers, timeout=5)
    return reps.json()


def group_remove(token, group_id):
    """
    解散群组接口
    :param token:       鉴权token值         True    string
    :param group_id:    群组ID              True    string
    :return:            返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/group/remove'
    headers = {
        'access_token': token
    }
    payload = {"groupId": group_id}
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


def group_remove_all(token):
    """
    解散用户当前所有的群组
    :param token:       鉴权token值         True    string
    :return:            None
    """
    reps = group_list_mine(token)['data']
    for i in reps:
        group_remove(token, i['communicationId'])


def group_member_exit(token, group_id):
    """
    退出群组接口
    :param token:       鉴权token值         True    string
    :param group_id:    群组ID              True    string
    :return:            返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/group/member/exit'
    headers = {
        'access_token': token
    }
    payload = {"groupId": group_id}
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


def group_member_exit_all(token):
    """
    退出所有的群组接口
    :param token:
    :return:
    """
    reps = group_list_mine(token)['data']
    for i in reps:
        group_member_exit(token, i['communicationId'])


def group_detail(token, group_id):
    """
    群组详情接口:查看单个接口
    :param token:       鉴权token值         True    string
    :param group_id:    群组ID              True    string
    :return:            返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/group/detail'
    headers = {
        'access_token': token
    }
    payload = {"groupId": group_id}
    reps = requests.get(url, headers=headers, params=payload, timeout=5)
    return reps.json()


def group_detail_list(token, group_ids):
    """
    群组详情接口:查看多个接口
    :param token:       鉴权token值                    True      string
    :param group_ids:   群组ID，以逗号分割， 如1,2,3,4    True	    string
    :return:            返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/group/detail/list'
    headers = {
        'access_token': token
    }
    payload = {"groupIds": group_ids}
    reps = requests.get(url, headers=headers, params=payload, timeout=5)
    return reps.json()


def group_manager_multi_add(token, group_id, manager_ids):
    """
    新增管理员接口
    :param token:           鉴权token值                    True      string
    :param group_id:        群组ID                         True      string
    :param manager_ids:     管理员用户ID集合，逗号隔开        True      string
    :return:                返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/group/manager/multi/add'
    headers = {
        'access_token': token
    }
    payload = {"groupId": group_id, "managerIds": manager_ids}
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


def group_manager_multi_remove(token, group_id, manager_ids):
    """
    删除管理员接口
    :param token:           鉴权token值                    True      string
    :param group_id:        群组ID                         True      string
    :param manager_ids:     管理员用户ID集合，逗号隔开        True      string
    :return:                返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/group/manager/multi/remove'
    headers = {
        'access_token': token
    }
    payload = {"groupId": group_id, "managerIds": manager_ids}
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


def group_manager_list(token, group_id):
    """
    群管理员列表
    :param token:           鉴权token值                    True      string
    :param group_id:        群组ID                         True      string
    :return:                返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/group/manager/list'
    headers = {
        'access_token': token
    }
    payload = {"groupId": group_id}
    reps = requests.get(url, headers=headers, params=payload, timeout=5)
    reps.close()
    return reps.json()


def group_member_remove_multi(token, group_id, user_ids):
    """
    踢出群成员接口
    :param token:           鉴权token值                    True      string
    :param group_id:        群组ID                         True      string
    :param user_ids:        群组成员用户ID集合               True      string
    :return:                返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/group/member/remove/multi'
    headers = {
        'access_token': token
    }
    payload = {"groupId": group_id, "userIds": user_ids}
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


def group_assignment(token, group_id, owner_id):
    """
    群组转让接口
    :param token:           鉴权token值                    True      string
    :param group_id:        群组ID                         True      string
    :param owner_id:        要转让的群主用户ID               True      string
    :return:                返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/group/assignment'
    headers = {
        'access_token': token
    }
    payload = {"groupId": group_id, "ownerId": owner_id}
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


def group_member_list(token, group_id):
    """
    成员列表接口
    :param token:           鉴权token值                    True      string
    :param group_id:        群组ID                         True      string
    :return:                返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/group/member/list'
    headers = {
        'access_token': token
    }
    payload = {"groupId": group_id}
    reps = requests.get(url, headers=headers, params=payload, timeout=5)
    return reps.json()


def get_group_announcement(token, group_id):
    """
    获取群公告接口
    :param token:           鉴权token值                    True      string
    :param group_id:        群组ID                         True      string
    :return:                返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/group/announcement/get'
    headers = {
        'access_token': token
    }
    data = {
        "groupId": group_id
    }
    reps = requests.post(url, headers=headers, data=data, timeout=5)
    return reps.json()


def set_group_announcement(token, group_id, announcement=None):
    """
    设置群公告接口
    :param token:           鉴权token值                    True      string
    :param group_id:        群组ID                         True      string
    :param announcement:    群公告                          False     string
    :return:                返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/group/announcement/update'
    headers = {
        'access_token': token
    }
    data = {}
    if announcement is not None:
        data["announcement"] = announcement
    data["groupId"] = group_id
    reps = requests.post(url, headers=headers, data=data, timeout=5)
    return reps.json()


def group_invite_user_accept(token, group_id):
    """
    用户接受群邀请接口
    :param token:           鉴权token值                    True      string
    :param group_id:        群组ID                         True      string
    :return:                返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/group/invite/user/accept'
    headers = {
        'access_token': token
    }
    payload = {"groupId": group_id}
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


def group_member_add_multi(token, group_id, user_ids, invite_msg=None):
    """
    拉人入群接口:如果用户设置需要确认的时候，则需要等待用户同意后才可入群
    :param token:           鉴权token值                        True      string
    :param group_id:        群组ID                             True      string
    :param user_ids:        用户ID,多个用逗号隔开，如 1,2,3,4,5   True      string
    :param invite_msg:      邀请信息                            False     string
    :return:                返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/group/member/add/multi'
    headers = {
        'access_token': token
    }
    payload = {"groupId": group_id, "userIds": user_ids}
    if invite_msg is not None:
        payload["inviteMsg"] = invite_msg
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()


def group_invite_user_reject(token, group_id, reason=None):
    """
    用户拒绝群邀请接口
    :param token:           鉴权token值                        True      string
    :param group_id:        群组ID                             True      string
    :param reason:          拒绝理由                            False     string
    :return:                返回返回体的字典格式
    """
    url = HOST + '/sdk/v1/group/invite/user/reject'
    headers = {
        'access_token': token
    }
    payload = {"groupId": group_id}
    if reason is not None:
        payload["reason"] = reason
    reps = requests.post(url, headers=headers, data=payload, timeout=5)
    return reps.json()
    
    
def set_group_mute(token, group_id, user_id_list_str, flag=None):  # 设置群聊禁言
    """
    :param token:
    :param group_id:
    :param user_id_list_str:
    :param flag: add添加，remove移除
    """
    if flag is None or flag == 'add':
        url = HOST + '/sdk/v1/group/user/multi/mute'
    elif flag == 'remove':
        url = HOST + '/sdk/v1/group/user/multi/mute/relieve'
    else:
        raise Exception('unknow flag')
    headers = {
        'access_token': token
    }
    data = {
        'groupId': group_id,
        'userIds': user_id_list_str
    }
    r = requests.post(url, headers=headers, data=data, timeout=5)
    r.close()
    # assert r.status_code == 200, r
    return r.json() 


def group_mute_list(token, group_id):
    """
    群禁言列表
    :param token:
    :param group_id:
    """
    url = HOST + '/sdk/v1/group/mute/list'
    headers = {
        'access_token': token
    }
    data = {
        'groupId': group_id
    }
    r = requests.get(url, headers=headers, params=data, timeout=5)
    r.close()
    return r.json()
    
    
def group_mutewhite_add(token, group_id, user_id_list_str):
    """
    添加群禁言白名单
    :param token:
    :param group_id:
    :param user_id_list_str:
    """
    url = HOST + '/sdk/v1/group/user/mutewhite/add'
    headers = {
        'access_token': token
    }
    data = {
        'groupId': group_id,
        'userIds': user_id_list_str
    }
    r = requests.post(url, headers=headers, data=data, timeout=5)
    r.close()
    return r.json()


def group_mutewhite_relieve(token, group_id, user_id_list_str):
    """
    解除群禁言白名单
    :param token:
    :param group_id:
    :param user_id_list_str:
    """
    url = HOST + '/sdk/v1/group/user/mutewhite/relieve'
    headers = {
        'access_token': token
    }
    data = {
        'groupId': group_id,
        'userIds': user_id_list_str
    }
    r = requests.post(url, headers=headers, data=data, timeout=5)
    r.close()
    return r.json()


def group_mutewhite_list(token, group_id):
    """
    获取群禁言白名单
    :param token:
    :param group_id:
    """
    url = HOST + '/sdk/v1/group/user/mutewhite/list'
    headers = {
        'access_token': token
    }
    data = {
        'groupId': group_id
    }
    r = requests.post(url, headers=headers, data=data, timeout=5)
    r.close()
    return r.json()


def group_share_files_list(token: str, group_id: str, count: int = None, create_time: int = None):
    """
    获取群共享文件
    :param token: token
    :param group_id: 群组ID
    :param count: 一次拉取列表数量
    :param create_time: 文件列表的最后一条的创建时间
    """
    url = HOST + '/sdk/v1/group/shareFiles/list'
    headers = {
        'access_token': token
    }
    data = {
        'groupId': group_id
    }
    if count:
        data['count'] = count
    if create_time:
        data['createTime'] = create_time
    r = requests.post(url, headers=headers, data=data, timeout=5)
    r.close()
    return r.json()


def group_share_files_upload(token: str, group_id: str, file_path: str):
    """
    上传群共享文件
    :param token: token
    :param group_id: 群组ID
    :param count: 一次拉取列表数量
    :param file_path: 文件路径
    """
    url = HOST + '/sdk/v1/group/shareFiles/upload'
    headers = {
        'access_token': token
    }
    data = {
        'groupId': group_id
    }
    files = {'file': open(file_path, 'rb')}
    r = requests.post(url, headers=headers, files=files, data=data, timeout=10)
    r.close()
    return r.json()


def group_share_files_del(token: str, group_id: str, file_id: int):
    """
    删除群共享文件
    :param token: token
    :param group_id: 群组ID
    :param file_id: 文件ID
    """
    url = HOST + '/sdk/v1/group/shareFiles/del'
    headers = {
        'access_token': token
    }
    data = {
        'groupId': group_id,
        'fileId': file_id
    }
    r = requests.post(url, headers=headers, data=data, timeout=5)
    r.close()
    return r.json()


if __name__ == '__main__':
    from config.conf import user1_info, user2_info, user3_info
    from lib.im_api_lib.login import login
    token_1 = login(user1_info)
    group_member_exit_all(token_1)
    group_remove_all(token_1)
    res = group_create_with_users(token_1, user_ids=f"{user2_info['user_id']},{user3_info['user_id']}")
    print(res)


