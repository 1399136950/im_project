import allure

from lib.paas_lib.paas_user import PaasUser
from lib.platform_lib.platform_user import Manager
from common.my_log import my_log
from config.conf import PAAS_USER, MANAGER_USER


@allure.feature('对比运营管理平台和paas平台的订单管理数据')
class TestOrderManagement:

    def setup_class(self):
        self.paas_user = PaasUser(*PAAS_USER)
        self.manager = Manager(*MANAGER_USER)

    @allure.story('检查对比昨天到当前的paas和平台的数据')
    def test_001(self):
        paas_ans = self.paas_user.order_management_full()
        platform_ans = self.manager.order_management_full(company_account=self.paas_user.phone)
        assert len(paas_ans) == len(platform_ans)
        paas_ans_ = sorted(paas_ans, key=lambda x: x['id'])
        platform_ans_ = sorted(platform_ans, key=lambda x: x['id'])
        my_log('paas_ans_', paas_ans_)
        my_log('platform_ans_', platform_ans_)
        n = len(paas_ans_)
        for i in range(n):
            assert platform_ans_[i]['productName'] == paas_ans_[i]['productName']
            assert platform_ans_[i]['payStatus'] == paas_ans_[i]['payStatus']
            assert platform_ans_[i]['id'] == paas_ans_[i]['id']
            assert platform_ans_[i]['orderCode'] == paas_ans_[i]['orderCode']
            assert platform_ans_[i]['remark'] == paas_ans_[i]['remark']
            assert platform_ans_[i]['amount'] == paas_ans_[i]['amount']
