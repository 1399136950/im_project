# -*- coding:utf-8 -*-
# @author  : ywt
# @file   : test_user_detail.py
# @ide    : PyCharm
# @time    : 2021/3/31 17:25
import allure
import pytest

from lib.im_api_lib.user import user_detail
from config.conf import user1_info, user2_info
from common.my_log import my_log
from lib.im_api_lib.login import login
from lib.im_api_lib.user import user_base_info_set      # 设置基本信息接口


@allure.feature("单用户信息接口")
class TestUserDetail:
    def setup_class(self):
        self.error_user_id = "ddjtsshty4avjpkpqqyya"
        self.token_2 = login(user2_info)
        self.new_avatar = "http://img.jj20.com/up/allimg/911/091316135304/160913135304-8-1200.jpg"
        self.new_nickname = "这个就是美女迪丽热巴"
        self.new_phone = "19999999999"
        self.new_sex = 2
        self.default_avatar = "http://zx-sdk.zhuanxin.com/images/default_avatar.png"

    @pytest.fixture(scope="class", autouse=True)
    def after_step(self, start_demo):
        """
        类级别的清除：测试完成后把user1和user2的用户信息全部设置成默认
        :return:
        """
        pass
        yield
        token_1 = start_demo
        user_base_info_set(token_1,
                           avatar=self.default_avatar,
                           nickname="user1的默认名称",
                           phone="12618400001",
                           sex=1)
        user_base_info_set(self.token_2,
                           avatar=self.default_avatar,
                           nickname="user2的默认名称",
                           phone="12618400002",
                           sex=1)

    @allure.story("查看当前账户的用户信息场景")
    @allure.title("test_current_user_detail")
    def test_current_user_detail(self, start_demo):
        """
        1:当前用户user1自己查询自己的用户信息
        2：断言查询成功code=0，查询出来的用户信息里面的userId等于当前用户user1的id
        :param start_demo:
        :return:
        """
        token = start_demo
        reps = user_detail(token, user_id=user1_info["user_id"])
        my_log('test_current_user_detail',
               {"userId": user1_info["user_id"]}, reps)
        assert reps["code"] == "0"
        assert reps["data"]["userId"] == user1_info["user_id"]

    @allure.story("查看其他账户的用户信息场景")
    @allure.title("test_other_user_detail")
    def test_other_user_detail(self, start_demo):
        """
        1：user1用户查询其他用户user2的账户信息
        2：断言查询成功code=0，查询出来的用户信息里面的userId等于用户user2的id
        :param start_demo:
        :return:
        """
        token = start_demo
        reps = user_detail(token, user_id=user2_info["user_id"])
        my_log('test_other_user_detail',
               {"userId": user2_info["user_id"]}, reps)
        assert reps["code"] == "0"
        assert reps["data"]["userId"] == user2_info["user_id"]

    @allure.story("查看随机字段非用户的用户信息场景")
    @allure.title("test_non_users_user_detail")
    def test_non_users_user_detail(self, start_demo):
        """
        1：user1用户查询随机字段给用户的用户信息
        2：断言查询失败返回code=1，断言返回的error里面的message = '用户不存在'
        :param start_demo:
        :return:
        """
        token = start_demo
        reps = user_detail(token, user_id=self.error_user_id)
        my_log('test_non_users_user_detail',
               {"userId": self.error_user_id}, reps)
        assert reps["code"] == "1"
        assert reps["error"]["message"] == '用户不存在'

    @allure.story("user2修改用户信息后user1马上查询user2用户信息场景")
    @allure.title("test_after_user_update_info_user_detail")
    def test_after_user_update_info_user_detail(self, start_demo):
        """
        1:user2修改自身用户信息,然后user1去查询
        2:断言user1查询user2用户信息成功code=0，
          断言查询出来的nickname和avatar等信息和刚设置的相同
        :param start_demo:
        :return:
        """
        token = start_demo
        user_base_info_set(self.token_2,
                           avatar=self.new_avatar,
                           nickname=self.new_nickname,
                           phone=self.new_phone,
                           sex=self.new_sex)
        reps = user_detail(token, user_id=user2_info["user_id"])
        assert reps['code'] == "0"
        assert self.new_avatar == reps["data"]["avatar"]
        assert self.new_nickname == reps["data"]["nickname"]
        assert self.new_phone == reps["data"]["phone"]
        assert self.new_sex == int(reps["data"]["sex"])

