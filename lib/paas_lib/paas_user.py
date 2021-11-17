import socket
import time
from base64 import b64encode
from common.aes import aes_encrypt
from . import pass_api
from lib.mysql.mydb import IM
from config.conf import OCR_HOST_ADDR, PAAS_AES_KEY, PAAS_AES_IV


class PaasUser:

    def __init__(self, phone, password):
        self.phone = phone
        password = b64encode(aes_encrypt(password, PAAS_AES_KEY, iv=PAAS_AES_IV)).decode('utf-8')
        img_bin, code_id = pass_api.graphic_verify_code()
        s = socket.socket()
        s.connect(OCR_HOST_ADDR)
        s.send(img_bin)
        verify_code = s.recv(4).decode('utf-8')
        s.close()
        login_res = pass_api.login(phone, password, code_id, verify_code)
        if login_res['code'] != '0':
            raise Exception(login_res)
        self.token = login_res['data']['accessToken']

    def add_sensitive_word(self, app_id, filter_type, word_list):
        """
        增加敏感词
        @param app_id:
        @param filter_type: 1-黑名单， 2-白名单
        @param word_list:
        @return:
        """
        res = pass_api.sensitive_word_add(self.token, app_id, filter_type, word_list)
        return res

    def activate_resource_package(self, app_id, res_id):
        """
        激活资源包并重新绑定
        @param app_id:
        @param res_id:
        @return:
        """
        a = IM('org_resource_package')
        data = {
            'app_id': '',
            'app_key': '',
            'status': 10,
            'used_amount': 0
        }
        a.where({'id': res_id}).update(data)
        res = self.bind_resource_package(app_id, res_id)
        return res

    def bind_resource_package(self, app_id, res_id):
        """
        绑定资源包
        @param app_id:
        @param res_id:
        @return:
        """
        res = pass_api.res_bind(self.token, app_id, res_id)
        return res

    def custom_money(self, money):
        """
        账户消费金额
        @param money:
        @return:
        """
        a = IM('bill_org_account_entry')
        data = {
            'org_id': self.get_org_id(),
            'create_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'deal_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'type': 2,
            'amount': -1 * money,
            'status': 0,
            'remark': '测试消费',
            'name': '测试消费',
            'method': 3
        }
        res = a.add(data)
        print(res)
        a.close()

    def deposit_money(self, money):
        """
        修改数据库模拟充值
        @param money:
        @return:
        """
        a = IM('bill_org_account_entry')
        data = {
            'org_id': self.get_org_id(),
            'create_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'deal_time': time.strftime('%Y-%m-%d %H:%M:%S'),
            'type': 1,
            'amount': money,
            'status': 0,
            'remark': '测试充值',
            'name': '测试充值',
            'method': 3
        }
        res = a.add(data)
        print(res)
        a.close()

    def del_sensitive_word_by_id(self, app_id, sensitive_word_id_list):
        """
        删除敏感词
        @param app_id:
        @param sensitive_word_id_list:
        @return:
        """
        res = pass_api.sensitive_word_remove(self.token, app_id, sensitive_word_id_list)
        return res

    def del_sensitive_word_by_word(self, app_id, sensitive_word):
        """
        找到敏感词并删除
        @param app_id:
        @param sensitive_word:
        @return:
        """
        all_sensitive_word_list = self.get_all_sensitive_word_list(app_id)
        for word_info in all_sensitive_word_list:
            if word_info['word'] == sensitive_word:
                res = self.del_sensitive_word_by_id(app_id, str(word_info['id']))
                return res
        return None

    def get_all_sensitive_word_list(self, app_id):
        """
        获取敏感词列表信息
        @param app_id:
        @return:
        """
        page_no = 0
        ans = []
        res = pass_api.sensitive_word_list(self.token, app_id, page_no=page_no)
        total_count = res['data']['totalCount']
        ans.extend(res['data']['list'])
        while len(ans) < total_count:
            page_no += 1
            res = pass_api.sensitive_word_list(self.token, app_id, page_no=page_no)
            ans.extend(res['data']['list'])
        return ans

    def get_account_balance(self):
        """
        获取账户余额信息
        @return:
        """
        res = pass_api.cost_center_deposit(self.token)
        return res

    def get_org_id(self):
        a = IM('org_user')
        rtv = a.where({"phone": self.phone}).select('org_id')
        a.close()
        return rtv[0][0]

    def logout(self):
        res = pass_api.account_login_out(self.token)
        return res

    def update_sensitive_word(self, app_id, filter_type, replace_word, word_id):
        """
        修改敏感词设置
        @param app_id:
        @param filter_type:
        @param replace_word:
        @param word_id:
        @return:
        """
        res = pass_api.sensitive_word_update(self.token, app_id, filter_type, replace_word, word_id)
        return res

    def set_app_func(self, app_id, active, function_type):
        """
        设置应用功能配置
        @param active: 1 or 0,表示启用/禁用
        @param app_id:
        @param function_type: 功能标识1=红包功能；2=表情包；3=音视频服务；4=阅后即焚服务；5=文件发送；6=位置发送;
        @return:
        """
        res = pass_api.app_func_toggle(self.token, active, app_id, function_type)
        return res

    def set_app_service_ext(self, app_id, enable_status, service_type):
        """
        设置服务开关
        @param app_id:
        @param enable_status:
        @param service_type: 服务类型, 17-敏感词
        @return:
        """
        res = pass_api.app_service_ext_toggle(self.token, app_id, enable_status, service_type)
        return res

    def register(self, app_id, user_id, password):
        """
        注册SDK用户
        @param app_id:
        @param user_id:
        @param password:
        @return:
        """
        res = pass_api.register(self.token, app_id, user_id, password)
        return res

    def get_app_ext_info(self, app_id):
        """
        获取应用的服务开关配置信息
        @param app_id:
        @return:
        """
        res = pass_api.app_service_ext_info(self.token, app_id)
        return res

    def get_trade_detail(self, trade_method: int = None, trade_type: int = None, start_date: str = None, end_date: str = None, page_no: int = 0, page_size: int = None, index: str = None):
        """
        交易明细
        @param trade_method: 交易方式： 0=全部；1=支付宝充值；2=微信充值；3=系统扣款；4=余额支付；5=支付宝支付；6=微信支付
        @param trade_type: 交易类型 0=全部；1=充值；2=消费
        @param start_date:
        @param end_date:
        @param page_no:
        @param page_size:
        @param index:
        @return:
        """
        res = pass_api.cost_center_trade_list(self.token, trade_method, trade_type, start_date, end_date, page_no, page_size, index)
        return res

    def get_trade_detail_full(self, trade_method: int = None, trade_type: int = None, start_date: str = None, end_date: str = None):
        """
        交易明细
        @param trade_method: 交易方式： 0=全部；1=支付宝充值；2=微信充值；3=系统扣款；4=余额支付；5=支付宝支付；6=微信支付
        @param trade_type: 交易类型 0=全部；1=充值；2=消费
        @param start_date:
        @param end_date:
        @return:
        """
        ans = []
        page_no = 0
        res = pass_api.cost_center_trade_list(self.token, trade_method, trade_type, start_date, end_date, page_no)
        ans.extend(res['data']['list'])
        total_count = res['data']['totalCount']
        while len(ans) < total_count:
            page_no += 1
            res = pass_api.cost_center_trade_list(self.token, trade_method, trade_type, start_date, end_date, page_no)
            ans.extend(res['data']['list'])
        return ans

    def get_bill_detail(self, app_id: int = 0, product_type: int = 0, start_date: str = None, end_date: str = None, page_no: int = 0, page_size: int = 20, index: int = None):
        """
        费用中心-账单详情
        @param app_id:
        @param product_type:
        @param start_date:
        @param end_date:
        @param page_no: 当前页码，默认pageNo=0 为第一页
        @param page_size:
        @param index:
        @return:
        """
        res = pass_api.cost_center_bill_list(self.token, app_id, product_type, start_date, end_date, page_no, page_size, index)
        return res

    def get_bill_detail_full(self, app_id: int = 0, product_type: int = 0, start_date: str = None, end_date: str = None):
        page = 0
        ans = []
        res = self.get_bill_detail(app_id, product_type, start_date, end_date, page_no=page)
        total = res['data']['totalCount']
        ans.extend(res['data']['list'])
        while len(ans) < total:
            page += 1
            res = self.get_bill_detail(app_id, product_type, start_date, end_date, page_no=page)
            ans.extend(res['data']['list'])
        return ans

    def order_management(self, pay_status: int = None, start_date: str = None, end_date: str = None, page_no: int = 0, page_size: int = None, order_code: str = None):
        """
        费用中心-订单管理
        @param pay_status:
        @param start_date:
        @param end_date:
        @param page_no:
        @param page_size:
        @param order_code:
        @return:
        """
        res = pass_api.cost_center_list(self.token, pay_status, start_date, end_date, page_no, page_size, order_code)
        return res

    def order_management_full(self, pay_status: int = None, start_date: str = None, end_date: str = None):
        """
        费用中心-订单管理
        @param pay_status:
        @param start_date:
        @param end_date:
        @return:
        """
        ans = []
        page_no = 0
        res = pass_api.cost_center_list(self.token, pay_status, start_date, end_date, page_no)
        total = res['data']['totalCount']
        ans.extend(res['data']['list'])
        while len(ans) < total:
            page_no += 1
            res = pass_api.cost_center_list(self.token, pay_status, start_date, end_date, page_no)
            ans.extend(res['data']['list'])
        return ans

    def get_app_info_by_name(self, app_name):
        """
        通过app_name查找应用信息
        @param app_name:
        @return:
        """
        r = pass_api.app_list(self.token)
        for info in r['data']:
            if info['appName'] == app_name:
                return info
        return None


class Application(PaasUser):

    def __init__(self, phone, password, app_name):
        super().__init__(phone, password)
        app_info = self.get_app_info_by_name(app_name)
        if not app_info:
            raise Exception('应用不存在')
        self.app_id = app_info['id']
        self.app_key = app_info['appKey']
        self.app_name = app_name

    def register(self, user_id, password, app_id=None):
        return super(Application, self).register(self.app_id, user_id, password)


if __name__ == '__main__':
    user = PaasUser('18682336386', 'pj0510')
