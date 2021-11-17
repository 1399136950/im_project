# -*- coding:utf-8 -*-
# @author  : ywt
# @file   : File_upload_module.py
# @ide    : PyCharm
# @time    : 2021/3/29 13:34
import os
import math

import requests

from common.get_md5 import get_file_md5
from config.conf import HOST


def upload_file(token, file_path, scene=None):
    """
    上传单个文件接口：文件最大限制10M，最多总的除图片，音频视频外的其他文件
    :param token:           鉴权token值                         True        string
    :param file_path:       上传的文件的路径                      true        string
    :param scene:           上传场景: AVATAR=头像；               False       string
                                     CHAT=聊天文件
                                     CHAT_IMAGE=聊天图片；
                                     CHAT_AUDIO=聊天发送语音；
                                     CHAT_VIDEO=聊天发送视频文件；
                                     CHAT_ATTACHMENT=聊天附件
    :return:                返回返回体的字典格式
    """
    url = f'{HOST}/sdk/v1/upload/file'
    headers = {
        'accessToken': token
    }
    payload = {}
    if scene is not None:
        payload["scene"] = scene
    files = {'file': open(file_path, 'rb')}
    reps = requests.post(url, headers=headers, files=files, data=payload, timeout=10)
    return reps.json()


def upload_files():
    """
    上传多个文件接口
    :return:
    """
    pass


def upload_patch(token, file_path):
    """
    大文件的分片上传接口：超过10M大的文件都要进行分片上传，并且每个分片文件不能大于10M
    :param token:           鉴权token值                         True        string
    :param file_path:       上传的文件的路径                      true        string
    :return:                返回返回体的字典格式
    """
    url = f'{HOST}/sdk/v1/upload/patch'
    headers = {'accessToken': token}
    file_size = os.path.getsize(file_path)                          # 求出文件大小
    upload_count = math.ceil(file_size / (10 * 1024 * 1024))        # 文件上传的次数
    file_md5 = get_file_md5(file_path)                              # 文件的md5
    suffix = file_path.split(".")[-1]                               # 文件格式
    f0 = open(file_path, "rb")
    for i in range(1, upload_count + 1):
        files = f0.read(10 * 1024 * 1024)
        with open(f'../../data/im/upload_file/tmp/trunk.exe', 'wb') as f:
            f.write(files)
            f.close()
        fo = open(f'../../data/im/upload_file/tmp/trunk.exe', 'rb')
        payload = {"fileMd5": file_md5,
                   "patchCount": upload_count,
                   "seq": i,
                   "suffix": suffix
                   }
        files = {"file": fo}
        reps = requests.post(url, headers=headers, files=files, data=payload, timeout=10)
        fo.close()
        os.remove(f'../../data/im/upload_file/tmp/trunk.exe')
        if i == upload_count:
            return reps.json()
    f0.close()


if __name__ == '__main__':
    from lib.im_api_lib.login import login
    from config.conf import user1_info

    token_1 = login(user1_info)
    print(upload_patch(token_1, '../../data/im/upload_file/Xshell6_onlinedown.exe'))
