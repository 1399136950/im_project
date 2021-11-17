from random import choice

import pytest
import allure

from lib.im_socket_lib.sync_im_user import IMUser
from common.my_log import my_log


from config.conf import USER_INFO


@allure.feature('群备注测试用例')
class TestGroupRemark:

    def setup_class(self):
        self.users = {}
        self.user_id_list = []
        for info in USER_INFO[:]:
            # info['app_id'] = AppID
            user_id = info['user_id']
            self.users[user_id] = IMUser(info)
            self.users[user_id].run()
            self.users[user_id].accept_friend_group()   # 设置自动加好友和加入群
            self.user_id_list.append(user_id)
    
    def teardown_class(self):
        for k, v in self.users.items():
            v.logout()
    
    def setup_method(self):
        self.group_owner_id = choice(self.user_id_list)
        member_list = self.user_id_list[:]
        member_list.remove(self.group_owner_id)
        
        self.group_owner = self.users[self.group_owner_id]
        
        self.group_id = self.group_owner.create_group(','.join(member_list))['data']['communicationId']
        self.member_list = member_list
        my_log('group_id', '', self.group_id)
        my_log('group_owner_id', '', self.group_owner_id)
        
    def teardown_method(self):
        self.group_owner.remove_group(self.group_id)

    @allure.title('修改群备注测试')
    def test_001(self):
        group_remark = '群备注测试'
        res = self.group_owner.set_group_remark(self.group_id, group_remark)
        assert res['code'] == '0'
        my_log(group_remark, res)
        group_info_res = self.group_owner.get_group_detail(self.group_id)
        my_log('', group_info_res)

        assert group_info_res['data']['groupRemarkName'] == group_remark

    @allure.title('修改群备注敏感词测试')
    @pytest.mark.parametrize("remark", ['专业代理', '專業代理', 'SM', 'sm', '3P', '买卖64狗', 'GFW', 'GFw', 'GfW', 'Gfw',
                                        'gFW', 'gFw', 'gfW', 'gfw', 'tnt炸药配方', 'www2.92ri.com', 'GaY片', 'GAy片',
                                        'Gay片', 'GAY片', 'gaY片', 'gAy片', 'gay片', 'gAY片', '專业代理', '專業代理',
                                        '专业代理', '专業代理', '々﹟#﹩$﹠&﹪%*﹡﹢﹦全套', r'￣¯―﹨ˆ˜﹍﹎+=<＿_-\ˇ~﹉﹊（sm',
                                        '信用卡提现ˆˇ﹕︰﹔﹖﹑•¨….¸;！', 'youxing•¨….¸;！´？！',
                                        '操（）〈〉‹›﹛﹜『』〖〗［］《》〔〕{}「」【】逼', '流血?‘’“”〝〞ˆˇ﹕︰﹔﹖冲突'])
    def test_sensitive(self, remark):
        res = self.group_owner.set_group_remark(self.group_id, remark)
        assert res['code'] == '1' and res['error']['message'] == '群备注名称包含敏感词汇，请重新设置'
        my_log(remark, res)

    @allure.title('修改群备注敏感词白名单测试')
    @pytest.mark.parametrize("remark", ['EARLY', 'small'])
    def test_sensitive_white_list(self, remark):
        res = self.group_owner.set_group_remark(self.group_id, remark)
        assert res['code'] == '0'
        my_log(remark, res)
