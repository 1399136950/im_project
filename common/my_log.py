# -*- coding:utf-8 -*-
# @author  : ywt
# @file   : my_log.py
# @ide    : PyCharm
# @time    : 2021/3/26 16:04
import logging
import os
import time
import sys

PID = os.getpid()


def create_log(log_path):
    logger = logging.getLogger(os.path.split(log_path)[1])
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(log_path, encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    formatter.datefmt = '%Y-%m-%d %H:%M:%S'
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


apiLog = create_log(f'../log/{PID}_{time.strftime("%Y-%m-%d-%H-%M-%S")}.log')  # 创建一个日志对象apiLog


def my_log(*args):
    """
    日志记录函数
    :param args: if len(args) == 2: in_data, reps = args elif len(args) == 3: interface_name, in_data, reps = args
    :return:
    """
    if len(args) == 3:
        interface_name, in_data, reps = args
        apiLog.info(f'[{interface_name}]: 请求参数:{in_data}')
        apiLog.info(f'[{interface_name}]: 请求结果:{reps}')
    elif len(args) == 2:
        frame_obj = sys._getframe(1)    # 上层栈对象
        interface_name = frame_obj.f_code.co_name   # 函数名
        class_obj = frame_obj.f_locals.get('self', None)
        if class_obj:
            interface_name = class_obj.__class__.__name__ + '.' + interface_name    # 类名
        in_data, reps = args
        apiLog.info(f'[{interface_name}]: 请求参数:{in_data}')
        apiLog.info(f'[{interface_name}]: 请求结果:{reps}')
    else:
        raise Exception('unknow param')
