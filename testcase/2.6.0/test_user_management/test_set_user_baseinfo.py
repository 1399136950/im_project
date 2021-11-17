# -*- coding:utf-8 -*-
# @author  : ywt
# @file   : test_set_user_baseinfo.py
# @ide    : PyCharm
# @time    : 2021/3/26 13:54
import json

import pytest
import allure

from lib.im_api_lib.user import user_base_info_set  # 设置基本信息接口
from common.read_excel_data import get_excel_data  # 读取excel测试用例
from lib.im_api_lib.user import user_detail  # 单用户信息接口
from common.my_log import my_log
from config.conf import user1_info, user2_info
from lib.im_api_lib.login import login


@allure.feature("设置用户基本信息接口")
class TestSetUserBaseInfo:
    def setup_class(self):
        self.token_2 = login(user2_info)
        self.default_nickname = "匿名用户10086"
        self.same_nickname = "测试相同的昵称"
        self.new_avatar = "https://www.baidu.com/"
        self.new_phone = "16666666666"
        self.new_sex = "2"

    @pytest.fixture(scope="class")
    def before_func(self, start_demo):
        print("类的初始化")
        token_1 = start_demo
        user_base_info_set(token_1,
                           nickname=self.default_nickname,
                           avatar=self.new_avatar,
                           phone=self.new_phone,
                           sex=self.new_sex)
        yield token_1
        user_base_info_set(token_1,
                           nickname=self.default_nickname,
                           avatar=self.new_avatar,
                           phone=self.new_phone,
                           sex=self.new_sex)
        print("类的清除")

    @allure.story("设置用户昵称场景")
    @allure.title("test_set_user_nickname")
    @pytest.mark.parametrize("in_data,reps_data",
                             get_excel_data('../data/im/ZXIM接口测试用例-v1.0.xls',
                                            '用户管理模块',
                                            'test_set_user_nickname'))
    def test_set_user_nickname(self, in_data, reps_data, before_func):
        """
        1:用户user1设置昵称然后断言设置昵称接口的返回值的code等于预期
          如果昵称设置成功的话断言设置的昵称等于查询出来的昵称
        :param in_data:
        :param reps_data:
        :param before_func:
        :return:
        """
        token_1 = before_func
        reps = user_base_info_set(token_1, nickname=json.loads(in_data)["nickname"])
        my_log('test_set_user_nickname', in_data, reps)
        assert reps["code"] == json.loads(reps_data)["code"]
        if reps['msg'] == "SUCCESS":
            assert json.loads(in_data)["nickname"] == user_detail(token_1,
                                                                  user1_info['user_id'])['data']['nickname']

    @allure.story("用户昵称设置相同场景")
    @allure.title("test_set_user_nickname_same")
    def test_set_user_nickname_same(self, before_func):
        """
        1:user2设置same_nickname,断言user2设置same_name成功code=0
        2：user1设置和user2一样的名字,断言设置失败code=1，断言设置的失败的message = '昵称已经被使用'
        3:断言查询出来的user1的昵称不等于same_nickname
        :param before_func:
        :return:
        """
        token_1 = before_func
        res = user_base_info_set(self.token_2, nickname=self.same_nickname)
        assert res['code'] == "0"
        ret = user_base_info_set(token_1, nickname=self.same_nickname)
        my_log('test_set_user_nickname_same',
               {"nickname": self.same_nickname}, ret)
        assert ret['code'] == "1"
        assert ret["error"]["message"] == '昵称已经被使用'
        assert self.same_nickname != user_detail(token_1, user1_info['user_id'])['data']['nickname']

    @allure.story("设置用户头像场景")
    @allure.title("test_set_user_avatar")
    @pytest.mark.parametrize("in_data,reps_data",
                             get_excel_data('../data/im/ZXIM接口测试用例-v1.0.xls',
                                            '用户管理模块',
                                            'test_set_user_avatar'))
    def test_set_user_avatar(self, in_data, reps_data, before_func):
        """
        1:user1设置用户的头像，断言设置的结果等于预期，
          如果设置成功，断言查询到的用户头像等于设置的头像
        :param in_data:
        :param reps_data:
        :param before_func:
        :return:
        """
        token_1 = before_func
        reps = user_base_info_set(token_1, avatar=json.loads(in_data)["avatar"])
        my_log("test_set_user_avatar",
               {"avatar": json.loads(in_data)["avatar"]}, reps)
        assert reps['msg'] == json.loads(reps_data)['msg']
        if reps['msg'] == "SUCCESS":
            assert json.loads(in_data)["avatar"] == user_detail(token_1, user1_info['user_id'])['data']['avatar']

    @allure.story("设置用户手机号码场景")
    @allure.title("test_set_user_phone")
    @pytest.mark.parametrize("in_data,reps_data",
                             get_excel_data('../data/im/ZXIM接口测试用例-v1.0.xls',
                                            '用户管理模块',
                                            'test_set_user_phone'))
    def test_set_user_phone(self, in_data, reps_data, before_func):
        """
        1:对用户的手机号码phone字段进行设置，断言上设置的结果等于预期的结果，
           如果设置手机号码成功断言设置成功的手机号码等于查询用户详细信息的手机号码
        :param in_data:
        :param reps_data:
        :param before_func:
        :return:
        """
        token_1 = before_func
        reps = user_base_info_set(token_1, phone=json.loads(in_data)["phone"])
        my_log("test_set_user_phone",
               {"phone": json.loads(in_data)["phone"]}, reps)
        assert reps['msg'] == json.loads(reps_data)['msg']
        if reps['msg'] == "SUCCESS":
            assert json.loads(in_data)["phone"] == user_detail(token_1, user1_info['user_id'])['data']['phone']

    @allure.story("设置用户性别场景")
    @allure.title("test_set_user_sex")
    @pytest.mark.parametrize("in_data,reps_data",
                             get_excel_data('../data/im/ZXIM接口测试用例-v1.0.xls',
                                            '用户管理模块',
                                            'test_set_user_sex'))
    def test_set_user_sex(self, in_data, reps_data, before_func):
        """
        1:user1设置一个默认的初始化性别sex1，断言user1默认的性别等于初始化的sex1
        2:把user1从sex1设置成sex2，断言设置性别接口的返回值等于预期，断言设置成功后的性别等于sex2
        :param in_data:
        :param reps_data:
        :param before_func:
        :return:
        """
        token_1 = before_func
        user_base_info_set(token_1, sex=json.loads(in_data)["sex1"])
        assert json.loads(in_data)["sex1"] == user_detail(token_1, user_id=user1_info['user_id'])['data']['sex']
        reps = user_base_info_set(token_1, sex=json.loads(in_data)["sex2"])
        my_log('test_set_user_sex', in_data, reps)
        assert reps["msg"] == json.loads(reps_data)['msg']
        assert json.loads(in_data)["sex2"] == user_detail(token_1, user_id=user1_info['user_id'])['data']['sex']

    @allure.story("一次性设置用户全部信息场景")
    @allure.title("test_set_user_full_detail")
    @pytest.mark.parametrize("in_data,reps_data",
                             get_excel_data('../data/im/ZXIM接口测试用例-v1.0.xls',
                                            '用户管理模块',
                                            'test_set_user_full_detail'))
    def test_set_user_full_detail(self, in_data, reps_data, before_func):
        """
        1:user1用户一次性设置所有信息：头像，昵称，手机，sex性别
        2:断言用户信息接口设置后的返回值等于预期
        3：断言所有设置的信息成功，等于用户信息接口查询出来的结果
        :param in_data:
        :param reps_data:
        :param before_func:
        :return:
        """
        token_1 = before_func
        reps = user_base_info_set(token_1,
                                  nickname=json.loads(in_data)["nickname"],
                                  avatar=json.loads(in_data)["avatar"],
                                  phone=json.loads(in_data)["phone"],
                                  sex=json.loads(in_data)["sex"])
        my_log('test_set_user_full_detail', in_data, reps)
        assert reps['msg'] == json.loads(reps_data)['msg']
        ret = user_detail(token_1, user_id=user1_info['user_id'])['data']
        assert json.loads(in_data)["nickname"] == ret["nickname"]
        assert json.loads(in_data)["avatar"] == ret["avatar"]
        assert json.loads(in_data)["phone"] == ret["phone"]
        assert json.loads(in_data)["sex"] == ret["sex"]