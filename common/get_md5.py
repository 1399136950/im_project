# -*- coding:utf-8 -*-
# @author  : ywt
# @file   : get_md5.py
# @ide    : PyCharm
# @time    : 2021/3/29 18:13
import os
import hashlib

import requests


def get_file_md5(filename):
    md5 = hashlib.md5()
    if type(filename) == str:
        if not os.path.isfile(filename):
            return
        f = open(filename, 'rb')
        while True:
            b = f.read(8096)
            if not b:
                break
            md5.update(b)
        f.close()
        return md5.hexdigest()
    else:
        md5.update(filename)
        return md5.hexdigest()


if __name__ == '__main__':
    print(get_file_md5('../data/im/upload_file/2mb.exe'))
    ret = requests.get('http://mgim-sdk.zhuanxin.com/other/41190a5ddc051e93be4406563c7e5a17.exe').content
    print(get_file_md5(ret))
