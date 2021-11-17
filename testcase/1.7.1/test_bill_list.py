import time

import allure

from lib.paas_lib.paas_user import PaasUser
from lib.platform_lib.platform_user import Manager
from common.my_log import my_log
from config.conf import PAAS_USER, MANAGER_USER, APP_NAME


@allure.feature('对比运营管理平台和paas平台的账单详情数据')
class TestBillList:

    def setup_class(self):
        self.paas_user = PaasUser(*PAAS_USER)
        self.manager = Manager(*MANAGER_USER)
        self.app_info = self.paas_user.get_app_info_by_name(APP_NAME)

    @allure.story('检查对比昨天到当前的账单详情数据')
    def test_001(self):
        current_date = time.strftime('%Y-%m-%d')
        yesterday = time.strftime('%Y-%m-%d', time.localtime(time.time() - 86400))
        paas_ans = self.paas_user.get_bill_detail_full(app_id=self.app_info['id'], start_date=yesterday, end_date=current_date)
        platform_ans = self.manager.get_bill_detail_full(company_account=self.paas_user.phone, app_id=self.app_info['appKey'], start_date=yesterday, end_date=current_date)
        my_log('paas_ans', paas_ans)
        my_log('platform_ans', platform_ans)
        assert len(paas_ans) == len(platform_ans)
        paas_ans_ = sorted(paas_ans, key=lambda x: (x['productName'], x['fee']))
        platform_ans_ = sorted(platform_ans, key=lambda x: (x['productName'], x['fee']))
        n = len(platform_ans)
        for i in range(n):
            assert paas_ans_[i]['productName'] == platform_ans_[i]['productName']
            assert abs(paas_ans_[i]['fee'] - platform_ans_[i]['fee']) < 0.01
            assert paas_ans_[i]['usage'] == platform_ans_[i]['usage']
