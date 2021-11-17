# -*- coding:utf-8 -*-
# @author  : ywt
# @file   : test_upload_file.py
# @ide    : PyCharm
# @time    : 2021/3/29 15:13
import json

import pytest
import requests
import allure

from lib.im_api_lib.upload_file_module import upload_file
from common.read_excel_data import get_excel_data
from common.my_log import my_log
from common.get_md5 import get_file_md5


@allure.feature("文件上传接口")
class TestUploadFile:
    @allure.story("单个文件上传场景")
    @allure.title("test_upload_single_file")
    @pytest.mark.skip("网速的贼慢跳过test_upload_single_file")
    @pytest.mark.parametrize("in_data,reps_data",
                             get_excel_data('../data/im/ZXIM接口测试用例-v1.0.xls',
                                            '文件上传模块',
                                            'upload_file'))
    def test_upload_single_file(self, start_demo, in_data, reps_data):
        """
        1:传递文件路径把文件上传
        2：断言上传文件的实际返回值和我们预期的返回值的msg字段相等
        3：如果上传成功会返回一个fileUrl文件下载地址，上传成功的文件断言下载的文件的md5和我们上传文件的md5值相等
           md5值相等才是同一文件
        :param start_demo:
        :param in_data:
        :param reps_data:
        :return:
        """
        token = start_demo
        file_path = json.loads(in_data)["file_path"]
        reps = upload_file(token, file_path)
        my_log('test_upload_single_file', in_data, reps)
        assert reps['msg'] == json.loads(reps_data)['msg']
        if "fileUrl" in reps:
            ret = requests.get(reps["fileUrl"]).content
            assert get_file_md5(ret) == get_file_md5(json.loads(in_data)["file_path"])



