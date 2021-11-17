import time

import allure

from lib.paas_lib.paas_user import PaasUser
from lib.platform_lib.platform_user import Manager
from common.my_log import my_log
from config.conf import PAAS_USER, MANAGER_USER


@allure.feature('对比运营管理平台和paas平台的交易明细数据')
class TestTradeDetail:

    def setup_class(self):
        self.paas_user = PaasUser(*PAAS_USER)
        self.manager = Manager(*MANAGER_USER)

    @allure.story('检查对比昨天到当前的交易明细')
    def test_001(self):
        end_date = time.strftime('%Y-%m-%d', time.localtime(time.time() - 86400))
        start_date = time.strftime('%Y-%m-%d', time.localtime(time.time() - 86400*2))

        paas_ans = self.paas_user.get_trade_detail_full(start_date=start_date, end_date=end_date)
        platform_ans = self.manager.get_trade_detail_full(company_account=self.paas_user.phone, start_date=start_date, end_date=end_date)

        assert len(paas_ans) == len(platform_ans)
        n = len(paas_ans)
        platform_ans_ = sorted(platform_ans, key=lambda x: x['tradeCode'])
        paas_ans_ = sorted(paas_ans, key=lambda x: x['id'])

        my_log('paas_ans', paas_ans_)
        my_log('platform_ans', platform_ans_)

        for i in range(n):
            assert platform_ans_[i]['tradeCode'] == paas_ans_[i]['id']
            assert platform_ans_[i]['name'] == paas_ans_[i]['name']
            assert platform_ans_[i]['amount'] == paas_ans_[i]['amount']
