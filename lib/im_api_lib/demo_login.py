# -*- coding:utf-8 -*-
# @author  : ywt
# @file   : demo_login.py
# @ide    : PyCharm
# @time    : 2021/6/2 21:25
import requests


def demo_user_login(login_host, phone, pwd):
    """
    DEMO用户登录接口：demo层（应用层）去得到手机号码对应的user_id
    :param login_host:
    :param phone:       demo层用户手机号码
    :param pwd:         demo层用户注册的密码
    :return:
    """
    url = login_host + '/demo/user/login'
    data = {
        'phone': phone,
        'password': pwd
    }
    reps = requests.post(url, data=data, timeout=5)
    return reps.json()


if __name__ == '__main__':
    res = demo_user_login('https://im-gateway.zhuanxin.com',
                          "18163606916",
                          "y1234567")
    print(res)
