# -*- coding:utf-8 -*-
# @project : teacher_sq
# @author  : ywt
# @file   : conftest.py
# @ide    : PyCharm
# @time    : 2021/3/29 16:54

import pytest
from lib.im_api_lib.login import login
from config.conf import user1_info


@pytest.fixture(scope="session", autouse=True)
def start_demo():
    token = login(user1_info)
    print('包级别的初始化')
    yield token

if __name__ == '__main__':
    print(start_demo().__next__())

