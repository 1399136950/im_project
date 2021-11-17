# -*- coding:utf-8 -*-
# @project : teacher_sq
# @author  : ywt
# @file   : run_testcase.py
# @ide    : PyCharm
# @time    : 2021/3/26 11:02
import os
import sys
import pytest
import time

sys.path.append('..')

if os.path.exists('../log') is False:
    os.mkdir('../log')


DEV_PYTHON_CONF_PATH = '../config/.conf/dev_conf.py'    # dev环境 python 配置文件路径
PRO_PYTHON_CONF_PATH = '../config/.conf/pro_conf.py'    # 生产环境 python 配置文件路径
NORMAL_PYTHON_CONF_PATH = '../config/conf.py'   # 正常python配置文件路径


def change_config_file(env_model):
    if env_model == 'dev':
        with open(NORMAL_PYTHON_CONF_PATH, 'wb') as fd:
            with open(DEV_PYTHON_CONF_PATH, 'rb') as fd1:
                fd.write(fd1.read())
    elif env_model == 'pro':
        with open(NORMAL_PYTHON_CONF_PATH, 'wb') as fd:
            with open(PRO_PYTHON_CONF_PATH, 'rb') as fd1:
                fd.write(fd1.read())


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('empty model')
        exit(0)
    model = sys.argv[1]
    if len(sys.argv) == 2:
        print('dev env')
        change_config_file('dev')
    elif sys.argv[2] != '':
        print('produce env')
        change_config_file('pro')

    time_stamp = time.strftime('%Y-%m-%d_%H-%M-%S')  # 生成时间戳
    pytest.main([f"../{model}", "-s", "--alluredir", f"../.allure/{time_stamp}"])

    cmd = "allure " + "generate " + os.path.abspath(f"../.allure/{time_stamp}") + " -o " + os.path.abspath(f"../report/{time_stamp}") + ' --clean'    # 根据指定的allure路径生成html报告
    os.system(cmd)
    os.system(f"allure serve ../.allure/{time_stamp}")
