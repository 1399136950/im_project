# -*- coding:utf-8 -*-
# @author  : ywt
# @file   : test_sensitive.py
# @ide    : PyCharm
# @time    : 2021/4/6 17:50
import pytest
import allure

from lib.im_api_lib.user import user_base_info_set
from lib.im_api_lib.user import user_detail
from lib.im_api_lib.group_management import group_create_with_users
from lib.im_api_lib.group_management import group_member_exit_all
from lib.im_api_lib.group_management import group_remove_all
from lib.im_api_lib.group_management import group_info_description_update
from lib.im_api_lib.group_management import group_info_update
from lib.im_api_lib.group_management import group_detail_list
from common.my_log import my_log
from config.conf import user1_info, user2_info, user3_info


@allure.feature("敏感词过滤功能测试")
class TestSensitive:
    @allure.story("用户昵称敏感词黑名单设置场景")
    @allure.title("test_nickname_set_sensitive")
    @pytest.mark.parametrize("msg", 
                            ['专业代理', '專業代理', 'SM', 'sm', '3P', '买卖64狗', 'GFW', 'GFw', 'GfW', 'Gfw', 'gFW', 'gFw', 'gfW', 
                            'gfw', 'tnt炸药配方', 'www2.92ri.com', 'GaY片', 'GAy片', 'Gay片', 'GAY片', 'gaY片', 'gAy片', 'gay片', 
                            'gAY片', '專业代理', '專業代理', '专业代理', '专業代理', '々﹟#﹩$﹠&﹪%*﹡﹢﹦全套', '￣¯―﹨ˆ˜﹍﹎+=<＿_-\ˇ~﹉﹊（sm', 
                            '信用卡提现ˆˇ﹕︰﹔﹖﹑•¨….¸;！', 'youxing•¨….¸;！´？！', '操（）〈〉‹›﹛﹜『』〖〗［］《》〔〕{}「」【】逼', 
                            '流血?‘’“”〝〞ˆˇ﹕︰﹔﹖冲突'])
    def test_nickname_set_sensitive(self, start_demo, msg):
        token = start_demo
        res = user_base_info_set(token, nickname=msg)
        my_log('test_nickname_set_sensitive', {"nickname": msg}, res)
        assert res['code'] == '1'
        assert res['error']['message'] == '用户昵称包含敏感词汇，请重新设置'
        assert msg != user_detail(token, user1_info["user_id"])["data"]["nickname"]

    @allure.story("用户昵称敏感词白名单设置场景")
    @allure.title("test_nickname_set_normal_sensitive")
    @pytest.mark.parametrize("msg", ['EARLY', 'small'])
    def test_nickname_set_normal_sensitive(self, start_demo, msg):
        token = start_demo
        res = user_base_info_set(token, nickname=msg)
        my_log('test_nickname_set_normal_sensitive', {"nickname": msg}, res)
        assert res['code'] == '0'
        assert user_detail(token, user1_info['user_id'])['data']['nickname'] == msg

    @allure.story("创建群组名称敏感词黑名单设置场景")
    @allure.title("test_group_name_set_sensitive")
    @pytest.mark.parametrize("msg", 
                            ['专业代理', '專業代理', 'SM', 'sm', '3P', '买卖64狗', 'GFW', 'GFw', 'GfW', 'Gfw', 'gFW', 'gFw', 'gfW', 
                            'gfw', 'tnt炸药配方', 'www2.92ri.com', 'GaY片', 'GAy片', 'Gay片', 'GAY片', 'gaY片', 'gAy片', 'gay片', 
                            'gAY片', '專业代理', '專業代理', '专业代理', '专業代理', '々﹟#﹩$﹠&﹪%*﹡﹢﹦全套', r'￣¯―﹨ˆ˜﹍﹎+=<＿_-\ˇ~﹉﹊（sm',
                            '信用卡提现ˆˇ﹕︰﹔﹖﹑•¨….¸;！', 'youxing•¨….¸;！´？！', '操（）〈〉‹›﹛﹜『』〖〗［］《》〔〕{}「」【】逼', 
                            '流血?‘’“”〝〞ˆˇ﹕︰﹔﹖冲突'])
    def test_group_name_set_sensitive(self, start_demo, msg):
        token = start_demo
        group_member_exit_all(token)
        group_remove_all(token)
        res = group_create_with_users(token,
                                      group_name=msg,
                                      user_ids=f'{user2_info["user_id"]},{user3_info["user_id"]}')
        my_log('test_group_name_set_sensitive',
               {"groupName": msg, "userIds": f'{user2_info["user_id"]},{user3_info["user_id"]}'}, res)
        assert res['code'] == '1'
        assert res["error"]["message"] == '群聊名称包含敏感词汇，请重新设置'
        group_member_exit_all(token)
        group_remove_all(token)

    @allure.story("创建群组名称敏感词白名单设置场景")
    @allure.title("test_group_name_set_normal_sensitive")
    @pytest.mark.parametrize("msg", ['EARLY', 'small'])
    def test_group_name_set_normal_sensitive(self, start_demo, msg):
        token = start_demo
        group_member_exit_all(token)
        group_remove_all(token)
        res = group_create_with_users(token,
                                      group_name=msg,
                                      user_ids=f'{user2_info["user_id"]},{user3_info["user_id"]}')
        my_log('test_group_name_set_sensitive',
               {"groupName": msg, "userIds": f'{user2_info["user_id"]},{user3_info["user_id"]}'}, res)
        assert res['code'] == '0'
        assert msg == res['data']['name']
        assert msg == group_detail_list(token, group_ids=res["data"]["communicationId"])["data"][0]["name"]
        group_member_exit_all(token)
        group_remove_all(token)

    @allure.story("创建群组描述敏感词黑名单设置场景")
    @allure.title("test_group_describe_set_sensitive")
    @pytest.mark.parametrize("msg", 
                            ['专业代理', '專業代理', 'SM', 'sm', '3P', '买卖64狗', 'GFW', 'GFw', 'GfW', 'Gfw', 'gFW', 'gFw', 'gfW', 
                            'gfw', 'tnt炸药配方', 'www2.92ri.com', 'GaY片', 'GAy片', 'Gay片', 'GAY片', 'gaY片', 'gAy片', 'gay片', 
                            'gAY片', '專业代理', '專業代理', '专业代理', '专業代理', '々﹟#﹩$﹠&﹪%*﹡﹢﹦全套', '￣¯―﹨ˆ˜﹍﹎+=<＿_-\ˇ~﹉﹊（sm', 
                            '信用卡提现ˆˇ﹕︰﹔﹖﹑•¨….¸;！', 'youxing•¨….¸;！´？！', '操（）〈〉‹›﹛﹜『』〖〗［］《》〔〕{}「」【】逼', 
                            '流血?‘’“”〝〞ˆˇ﹕︰﹔﹖冲突'])
    def test_group_describe_set_sensitive(self, start_demo, msg):
        token = start_demo
        group_member_exit_all(token)
        group_remove_all(token)
        res = group_create_with_users(token,
                                      description=msg,
                                      user_ids=f'{user2_info["user_id"]},{user3_info["user_id"]}')
        my_log('test_group_describe_set_sensitive',
               {"description": msg, "userIds": f'{user2_info["user_id"]},{user3_info["user_id"]}'}, res)
        assert res['code'] == '1'
        assert res['error']['message'] == '群描述内容包含敏感词汇，请重新设置'
        group_member_exit_all(token)
        group_remove_all(token)

    @allure.story("创建群组描述敏感词白名单设置场景")
    @allure.title("test_group_describe_set_normal_sensitive")
    @pytest.mark.parametrize("msg", ['EARLY', 'small'])
    def test_group_describe_set_normal_sensitive(self, start_demo, msg):
        token = start_demo
        group_member_exit_all(token)
        group_remove_all(token)
        res = group_create_with_users(token,
                                      description=msg,
                                      user_ids=f'{user2_info["user_id"]},{user3_info["user_id"]}')
        my_log('test_group_describe_set_normal_sensitive',
               {"description": msg, "userIds": f'{user2_info["user_id"]},{user3_info["user_id"]}'}, res)
        assert res['code'] == '0'
        assert msg == res['data']['description']
        assert msg == group_detail_list(token, group_ids=res["data"]["communicationId"])["data"][0]["description"]
        group_member_exit_all(token)
        group_remove_all(token)

    @allure.story("修改群组名称敏感词黑名单设置场景")
    @allure.title("test_modify_group_name_set_sensitive")
    @pytest.mark.parametrize("msg", 
                            ['专业代理', '專業代理', 'SM', 'sm', '3P', '买卖64狗', 'GFW', 'GFw', 'GfW', 'Gfw', 'gFW', 'gFw', 'gfW', 
                            'gfw', 'tnt炸药配方', 'www2.92ri.com', 'GaY片', 'GAy片', 'Gay片', 'GAY片', 'gaY片', 'gAy片', 'gay片', 
                            'gAY片', '專业代理', '專業代理', '专业代理', '专業代理', '々﹟#﹩$﹠&﹪%*﹡﹢﹦全套', '￣¯―﹨ˆ˜﹍﹎+=<＿_-\ˇ~﹉﹊（sm', 
                            '信用卡提现ˆˇ﹕︰﹔﹖﹑•¨….¸;！', 'youxing•¨….¸;！´？！', '操（）〈〉‹›﹛﹜『』〖〗［］《》〔〕{}「」【】逼', 
                            '流血?‘’“”〝〞ˆˇ﹕︰﹔﹖冲突'])
    def test_modify_group_name_set_sensitive(self, start_demo, msg):
        token = start_demo
        group_member_exit_all(token)
        group_remove_all(token)
        res = group_create_with_users(token, user_ids=f'{user2_info["user_id"]},{user3_info["user_id"]}')
        group_id = res['data']['communicationId']
        ret = group_info_update(token, group_id=group_id, group_name=msg)
        my_log('test_modify_group_name_set_sensitive',
               {"groupId": group_id, "groupName": msg}, ret)
        assert ret['code'] == '1'
        assert ret['error']['message'] == '群聊名称包含敏感词汇，请重新设置'
        assert msg != group_detail_list(token, group_ids=res["data"]["communicationId"])["data"][0]["name"]
        group_member_exit_all(token)
        group_remove_all(token)

    @allure.story("修改群组名称敏感词白名单设置场景")
    @allure.title("test_modify_group_name_set_normal_sensitive")
    @pytest.mark.parametrize("msg", ['EARLY', 'small'])
    def test_modify_group_name_set_normal_sensitive(self, start_demo, msg):
        token = start_demo
        group_member_exit_all(token)
        group_remove_all(token)
        res = group_create_with_users(token, user_ids=f'{user2_info["user_id"]},{user3_info["user_id"]}')
        group_id = res['data']['communicationId']
        ret = group_info_update(token, group_id=group_id, group_name=msg)
        my_log('test_modify_group_name_set_normal_sensitive', {"groupId": res, "groupName": msg}, ret)
        assert ret['code'] == '0'
        assert msg == group_detail_list(token, group_ids=group_id)['data'][0]['name']
        group_member_exit_all(token)                    # 退出所有的群组
        group_remove_all(token)                         # 删除所有的群组

    @allure.story("修改群组描述敏感词黑名单设置场景")
    @allure.title("test_modify_group_describe_set_sensitive")
    @pytest.mark.parametrize("msg", 
                            ['专业代理', '專業代理', 'SM', 'sm', '3P', '买卖64狗', 'GFW', 'GFw', 'GfW', 'Gfw', 'gFW', 'gFw', 'gfW', 
                            'gfw', 'tnt炸药配方', 'www2.92ri.com', 'GaY片', 'GAy片', 'Gay片', 'GAY片', 'gaY片', 'gAy片', 'gay片', 
                            'gAY片', '專业代理', '專業代理', '专业代理', '专業代理', '々﹟#﹩$﹠&﹪%*﹡﹢﹦全套', '￣¯―﹨ˆ˜﹍﹎+=<＿_-\ˇ~﹉﹊（sm', 
                            '信用卡提现ˆˇ﹕︰﹔﹖﹑•¨….¸;！', 'youxing•¨….¸;！´？！', '操（）〈〉‹›﹛﹜『』〖〗［］《》〔〕{}「」【】逼', 
                            '流血?‘’“”〝〞ˆˇ﹕︰﹔﹖冲突'])
    def test_modify_group_describe_set_sensitive(self, start_demo, msg):
        token = start_demo
        group_member_exit_all(token)                    # 退出所有的群组
        group_remove_all(token)                         # 删除所有的群组
        res = group_create_with_users(token, user_ids=f'{user2_info["user_id"]},{user3_info["user_id"]}')
        group_id = res['data']['communicationId']
        ret = group_info_description_update(token, group_id=group_id, description=msg)
        my_log('test_modify_group_describe_set_sensitive', {"groupId": res, "description": msg}, ret)
        assert ret['code'] == '1'
        assert ret['error']['message'] == '群描述内容包含敏感词汇，请重新设置'
        group_member_exit_all(token)                    # 退出所有的群组
        group_remove_all(token)                         # 删除所有的群组

    @allure.story("修改群组描述敏感词白名单设置场景")
    @allure.title("test_modify_group_describe_set_normal_sensitive")
    @pytest.mark.parametrize("msg", ['EARLY', 'small'])
    def test_modify_group_describe_set_normal_sensitive(self, start_demo, msg):
        token = start_demo
        group_member_exit_all(token)
        group_remove_all(token)
        res = group_create_with_users(token, user_ids=f'{user2_info["user_id"]},{user3_info["user_id"]}')
        group_id = res['data']['communicationId']
        ret = group_info_description_update(token, group_id=group_id, description=msg)
        my_log('test_modify_group_describe_set_normal_sensitive', {"groupId": res, "description": msg}, ret)
        assert ret['code'] == '0'
        assert msg == group_detail_list(token, group_ids=group_id)['data'][0]['description']
        group_member_exit_all(token)
        group_remove_all(token)
