# -*- coding:utf-8 -*-
# @project : teacher_sq
# @author  : ywt
# @ide    : PyCharm
# @time    : 2021/3/29 16:54
from random import choice

import pytest
from lib.im_api_lib.login import login
from lib.im_api_lib.user import user_friend_list
from config.conf import user1_info


@pytest.fixture(scope="session", autouse=False)
def start_demo():
    token = login(user1_info)
    print('包级别的初始化')
    yield token


if __name__ == '__main__':
    print(start_demo().__next__())

