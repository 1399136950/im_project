# -*- coding:utf-8 -*-
# @author  : ywt
# @file   : login.py
# @ide    : PyCharm
# @time    : 2021/3/26 13:45
from random import sample
from urllib import parse

import requests

from config.conf import LOGIN_HOST, clientId, clientSecret, device_info, AppID

'''
登录逻辑：
    1./api/v1/token 获取token
    2./api/v1/user/refreshLoginToken 刷新user_token 参数:header携带token
    3./mgacct/v1/{app_id}/sdkacct/login/v3 sdk用户登录  参数: header携带login_token,
     返回access_token
'''


def get_token():
    """
    获取应用方token，验证应用方token接口
    :return:        返回token
    """
    url = f'{LOGIN_HOST}/api/v1/token'
    payload = {
        'clientId': clientId,
        'clientSecret': clientSecret
    }
    reps = requests.get(url, params=payload, timeout=5)
    return reps.json()['data']['token']


def refresh_login_token(token, user_id):
    """
    刷新token，重新定义token接口
    :param token:           应用方获取的token
    :param user_id:         登录的用户id
    :return:
    """
    url = f'{LOGIN_HOST}/api/v1/user/refreshLoginToken'
    payload = {
        'token': sample('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', 21),
        'zxuid': user_id
    }
    headers = {
        'accessToken': token
    }
    reps = requests.post(url, payload, headers=headers, timeout=5)
    assert reps.json()['msg'] == 'SUCCESS'
    return payload['token']


def login(user_info, flag=True):
    """
    sdk用户登录接口，返回access_token
    :param user_info:       登录的用户信息
    :param flag:            标记，flag=True返回登录的token值，flag=False返回全部的返回值
    :return:
    """
    token = get_token()
    info = parse.quote(AppID)
    refresh_token = refresh_login_token(token, user_info['user_id'])
    url = f'{LOGIN_HOST}/mgacct/v1/{info}/sdkacct/login/v3'
    payload = {
        'app_id': AppID,
        'device_id': device_info['device_id'],
        'login_token': refresh_token,
        'manufacturer': device_info['manufacturer'],
        'module_types': user_info['module_types'],
        'platform': user_info['platform'],
        'user_id': user_info['user_id'],
        'version': user_info['version']
    }
    reps = requests.post(url, data=payload, timeout=5)
    print(reps.json())
    if flag is True:
        return reps.json()['data']['access_token']
    else:
        return reps.json()


if __name__ == '__main__':
    from config.conf import user1_info, user2_info, user3_info
    print(user1_info)
    print(login(user1_info))

