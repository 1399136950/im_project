import time
import socket
import allure

from lib.paas_lib.paas_user import PaasUser
from lib.platform_lib.platform_user import Manager
from common.my_log import my_log
from lib.paas_lib import pass_api
from config.conf import OCR_HOST_ADDR, PAAS_USER, MANAGER_USER


@allure.feature('操作日志接口查询')
class TestOperateLog:

    def setup_class(self):
        self.manager = Manager(*MANAGER_USER)

    @allure.story('正常登录然后登出')
    def test_001(self):
        paas_user = PaasUser(*PAAS_USER)
        curr_time = time.time()
        time.sleep(10)
        log_res = self.manager.get_operate_log()
        info = log_res['data']['items'][0]
        my_log('info', info)
        assert info['mobile'] == paas_user.phone
        assert info['operate'] == '登录'
        assert info['status'] == '成功'
        assert curr_time - (time.mktime(time.strptime(info['time'], '%Y-%m-%dT%H:%M:%S.000+0000')) + 8 * 3600) < 15

        time.sleep(10)
        logout_rtv = paas_user.logout()
        my_log('logout_rtv', logout_rtv)
        curr_time = time.time()
        time.sleep(10)
        log_res = self.manager.get_operate_log()
        info = log_res['data']['items'][0]
        my_log('info', info)
        assert info['mobile'] == paas_user.phone
        assert info['operate'] == '登出'
        assert info['status'] == '成功'
        assert curr_time - (time.mktime(time.strptime(info['time'], '%Y-%m-%dT%H:%M:%S.000+0000')) + 8 * 3600) < 15

    @allure.story('密码登录, 验证码错误')
    def test_002(self):
        img_bin, code_id = pass_api.graphic_verify_code()
        login_res = pass_api.login(PAAS_USER[0], PAAS_USER[1], code_id, 'abcdef')
        curr_time = time.time()
        my_log('login_res', login_res)
        time.sleep(10)
        log_res = self.manager.get_operate_log()
        info = log_res['data']['items'][0]
        my_log('info', info)
        assert info['mobile'] == PAAS_USER[0]
        assert info['operate'] == '登录'
        assert info['status'] == '验证码错误'
        assert curr_time - (time.mktime(time.strptime(info['time'], '%Y-%m-%dT%H:%M:%S.000+0000')) + 8 * 3600) < 15

    @allure.story('密码登录, 密码错误')
    def test_003(self):
        img_bin, code_id = pass_api.graphic_verify_code()
        s = socket.socket()
        s.connect(OCR_HOST_ADDR)
        s.send(img_bin)
        verify_code = s.recv(4).decode('utf-8')
        login_res = pass_api.login(PAAS_USER[0], '123456', code_id, verify_code)
        curr_time = time.time()
        my_log('login_res', login_res)
        time.sleep(10)
        log_res = self.manager.get_operate_log()
        info = log_res['data']['items'][0]
        my_log('info', info)
        assert info['mobile'] == PAAS_USER[0]
        assert info['operate'] == '登录'
        assert info['status'] == '用户账号或密码错误'
        assert curr_time - (time.mktime(time.strptime(info['time'], '%Y-%m-%dT%H:%M:%S.000+0000')) + 8 * 3600) < 15

    @allure.story('密码登录, 账户错误')
    def test_004(self):
        img_bin, code_id = pass_api.graphic_verify_code()
        s = socket.socket()
        s.connect(OCR_HOST_ADDR)
        s.send(img_bin)
        verify_code = s.recv(4).decode('utf-8')
        login_res = pass_api.login('18682336309', PAAS_USER[1], code_id, verify_code)
        curr_time = time.time()
        my_log('login_res', login_res)
        time.sleep(10)
        log_res = self.manager.get_operate_log()
        info = log_res['data']['items'][0]
        my_log('info', info)
        assert info['mobile'] == '18682336309'
        assert info['operate'] == '登录'
        assert info['status'] == '用户不存在'
        assert curr_time - (time.mktime(time.strptime(info['time'], '%Y-%m-%dT%H:%M:%S.000+0000')) + 8 * 3600) < 15

    @allure.story('验证码快速登录，然后验证码错误')
    def test_005(self):
        fast_login_res = pass_api.fast_login(PAAS_USER[0], 'abcdef')
        my_log('fast_login_res', fast_login_res)
        assert fast_login_res['code'] == '1'
        curr_time = time.time()
        time.sleep(10)
        log_res = self.manager.get_operate_log()
        info = log_res['data']['items'][0]
        my_log('info', info)
        assert info['mobile'] == PAAS_USER[0]
        assert info['operate'] == '登录'
        assert info['status'] == '验证码无效'
        assert curr_time - (time.mktime(time.strptime(info['time'], '%Y-%m-%dT%H:%M:%S.000+0000')) + 8 * 3600) < 15
