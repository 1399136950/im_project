from . import platform_api


class Manager:
    def __init__(self, phone, pwd):
        self.phone = phone
        self.pwd = pwd
        login_res = platform_api.login(phone, pwd)
        self.token = login_res['data']['token']

    def get_trade_detail(self, company_account=None, name=None, pay_method=None, start_date=None, end_date=None, page_number=None, page_size=None):
        """
        费用管理-交易明细
        @param company_account:
        @param name:
        @param pay_method:
        @param start_date:
        @param end_date:
        @param page_number:
        @param page_size:
        @return:
        """
        res = platform_api.trade_query_for_page(self.token, company_account, name, pay_method, start_date, end_date, page_number, page_size)
        return res

    def get_trade_detail_full(self, company_account=None, name=None, pay_method=None, start_date=None, end_date=None):
        """
        费用管理-交易明细
        @param company_account:
        @param name:
        @param pay_method:
        @param start_date:
        @param end_date:
        @return:
        """
        page_number = 1
        ans = []
        res = platform_api.trade_query_for_page(self.token, company_account, name, pay_method, start_date, end_date, page_number)
        total_count = res['data']['totalCount']
        ans.extend(res['data']['items'])
        while len(ans) < total_count:
            page_number += 1
            res = platform_api.trade_query_for_page(self.token, company_account, name, pay_method, start_date, end_date, page_number)
            total_count = res['data']['totalCount']
            ans.extend(res['data']['items'])
        return ans

    def get_operate_log(self, ip: str = None, mobile: str = None, start_date: str = None, end_date: str = None, page_no: int = 1, page_size: int = None):
        """
        查询操作日志
        @param ip:
        @param mobile:
        @param start_date:
        @param end_date:
        @param page_no:
        @param page_size:
        @return:
        """
        res = platform_api.operate_log_query_for_page(self.token, ip, mobile, start_date, end_date, page_no, page_size)
        return res

    def order_management(self, company_account=None, company_name=None, pay_status: int = None, product_name=None, start_date: str = None, end_date: str = None, page_no: int = 1, page_size: int = None):
        """
        费用管理-订单管理
        @param company_account:
        @param company_name:
        @param pay_status:
        @param product_name:
        @param start_date:
        @param end_date:
        @param page_no:
        @param page_size:
        @return:
        """
        res = platform_api.order_query_for_page(self.token, company_account, company_name, pay_status, product_name, start_date, end_date, page_no, page_size)
        return res

    def order_management_full(self, company_account=None, company_name=None, pay_status: int = None, product_name=None, start_date: str = None, end_date: str = None):
        """
        费用管理-订单管理
        @param company_account:
        @param company_name:
        @param pay_status:
        @param product_name:
        @param start_date:
        @param end_date:
        @return:
        """
        page_no = 1
        ans = []
        res = platform_api.order_query_for_page(self.token, company_account, company_name, pay_status, product_name, start_date, end_date, page_no)
        total_count = res['data']['totalCount']
        ans.extend(res['data']['items'])
        while len(ans) < total_count:
            page_no += 1
            res = platform_api.order_query_for_page(self.token, company_account, company_name, pay_status, product_name, start_date, end_date, page_no)
            total_count = res['data']['totalCount']
            ans.extend(res['data']['items'])
        return ans

    def get_bill_detail(self, company_account: str = None, app_id: str = None, product_name: str = None, start_date: str = None, end_date: str = None, page_no: int = 1, page_size: int = 20):
        """
        费用管理-客户账单
        @param company_account:
        @param app_id:
        @param product_name:
        @param start_date:
        @param end_date:
        @param page_no:
        @param page_size:
        @return:
        """
        res = platform_api.bill_query_for_page(self.token, company_account, app_id, product_name, start_date, end_date, page_no, page_size)
        return res

    def get_bill_detail_full(self, company_account: str = None, app_id: str = None, product_name: str = None, start_date: str = None, end_date: str = None):
        """
        费用管理-客户账单
        @param company_account:
        @param app_id:
        @param product_name:
        @param start_date:
        @param end_date:
        @return:
        """
        ans = []
        page = 1
        res = self.get_bill_detail(company_account=company_account, app_id=app_id, product_name=product_name, start_date=start_date, end_date=end_date, page_no=page)
        total = res['data']['totalCount']
        ans.extend(res['data']['items'])
        while len(ans) < total:
            page += 1
            res = self.get_bill_detail(company_account=company_account, app_id=app_id, product_name=product_name, start_date=start_date, end_date=end_date, page_no=page)
            ans.extend(res['data']['items'])
        return ans
