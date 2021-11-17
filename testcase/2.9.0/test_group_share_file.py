from random import choice
import json
# import time
import os

import requests
import pytest
import allure

from lib.im_socket_lib.sync_im_user import IMUser
from common.my_log import my_log


from config.conf import USER_INFO


def get_group_all_share_file(user, group_id):
    file_info_list = []
    res = user.group_share_files_list(group_id, count=20)
    assert res['code'] == '0'
    file_info_list.extend(res['data']['fileList'])

    while len(res['data']['fileList']) == 20:
        res = user.group_share_files_list(group_id, count=20, create_time=res['data']['cursor'])
        assert res['code'] == '0'
        file_info_list.extend(res['data']['fileList'])

    return file_info_list


@allure.feature('群文件共享测试用例')
class TestGroupShareFile:

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

    # @pytest.mark.skip('')
    @allure.title('群主上传群文件')
    def test_001(self):
        file_path = '../data/im/upload_file/IM项目周报-20210108.pdf'
        upload_res = self.group_owner.group_share_files_upload(self.group_id, file_path)
        my_log('test_001[群主上传群文件]', file_path, upload_res)
        assert upload_res['code'] == '0'
        assert upload_res['data']['fileName'] == os.path.split(file_path)[-1]
        # time.sleep(10)

        file_list = get_group_all_share_file(self.group_owner, self.group_id)

        is_in_file_list = False
        for file in file_list:
            if file['fileID'] == upload_res['data']['fileID']:
                is_in_file_list = True
                assert file == upload_res['data']
        assert is_in_file_list

    # @pytest.mark.skip('')
    @allure.title('管理员上传群文件')
    def test_002(self):
        manager_id = self.member_list.pop()
        
        set_manager_res = self.group_owner.set_group_manager(self.group_id, manager_id, 'add')
        my_log('test_002[群主设置管理员]', manager_id, set_manager_res)
        assert set_manager_res['code'] == '0'
        
        group_manager_list_res = self.group_owner.get_group_manager_list(self.group_id)
        my_log('test_002[管理员列表]', '', group_manager_list_res)
        assert manager_id in [i['userId'] for i in group_manager_list_res['data']]
        
        manager = self.users[manager_id]
        
        file_path = '../data/im/upload_file/IM项目周报-20210108.pdf'
        upload_res = manager.group_share_files_upload(self.group_id, file_path)
        my_log('test_002[管理员上传群文件]', file_path, upload_res)
        assert upload_res['code'] == '0'
        assert upload_res['data']['fileName'] == os.path.split(file_path)[-1]
        # time.sleep(10)
        
        file_list = get_group_all_share_file(manager, self.group_id)

        is_in_file_list = False
        for file in file_list:
            if file['fileID'] == upload_res['data']['fileID']:
                is_in_file_list = True
                assert file == upload_res['data']
        assert is_in_file_list

    # @pytest.mark.skip('')
    @allure.title('普通成员上传群文件')
    def test_003(self):
        normal_id = choice(self.member_list)
        
        normal_user = self.users[normal_id]
        
        file_path = '../data/im/upload_file/IM项目周报-20210108.pdf'
        upload_res = normal_user.group_share_files_upload(self.group_id, file_path)
        my_log('test_003[普通成员上传群文件]', file_path, upload_res)
        assert upload_res['code'] == '0'
        assert upload_res['data']['fileName'] == os.path.split(file_path)[-1]
        # time.sleep(10)
        
        file_list = get_group_all_share_file(normal_user, self.group_id)
        
        is_in_file_list = False
        for file in file_list:
            if file['fileID'] == upload_res['data']['fileID']:
                is_in_file_list = True
                assert file == upload_res['data']
        assert is_in_file_list

    # @pytest.mark.skip('')
    @allure.title('禁言用户上传群文件')
    def test_004(self):
        mute_id = choice(self.member_list)
        
        set_mute_res = self.group_owner.set_group_mute(self.group_id, mute_id, 'add')
        my_log('test_004[将成员加到禁言列表]', mute_id, set_mute_res)
        assert set_mute_res['code'] == '0'
        
        group_mute_list_res = self.group_owner.get_group_mute_list(self.group_id)
        my_log('test_004[群禁言列表]', '', group_mute_list_res)
        assert group_mute_list_res['code'] == '0'
        assert mute_id in [i['userId'] for i in group_mute_list_res['data']]
        
        mute_user = self.users[mute_id]
        
        file_path = '../data/im/upload_file/IM项目周报-20210108.pdf'
        upload_res = mute_user.group_share_files_upload(self.group_id, file_path)
        my_log('test_004[禁言成员上传群文件]', file_path, upload_res)
        assert upload_res['code'] == '0'
        assert upload_res['data']['fileName'] == os.path.split(file_path)[-1]
        # time.sleep(10)
        file_list = get_group_all_share_file(mute_user, self.group_id)
        
        is_in_file_list = False
        for file in file_list:
            if file['fileID'] == upload_res['data']['fileID']:
                is_in_file_list = True
                assert file == upload_res['data']
        assert is_in_file_list

    # @pytest.mark.skip('')
    @allure.title('黑名单用户上传群文件')
    def test_005(self):
        black_id = choice(self.member_list)
        
        set_black_list_res = self.group_owner.set_group_black_list(self.group_id, black_id, 'add')
        my_log('test_005[设置黑名单]', black_id, set_black_list_res)
        assert set_black_list_res['code'] == '0'
        
        group_black_list_res = self.group_owner.get_group_black_list(self.group_id)
        my_log('test_005[黑名单列表]', '', group_black_list_res)
        assert black_id in [i['userId'] for i in group_black_list_res['data']]
        
        black_user = self.users[black_id]
        
        file_path = '../data/im/upload_file/IM项目周报-20210108.pdf'
        upload_res = black_user.group_share_files_upload(self.group_id, file_path)
        my_log('test_005[黑名单成员上传群文件]', file_path, upload_res)
        assert upload_res['code'] == '0'
        assert upload_res['data']['fileName'] == os.path.split(file_path)[-1]
        # time.sleep(10)
        
        file_list = get_group_all_share_file(black_user, self.group_id)

        is_in_file_list = False
        for file in file_list:
            if file['fileID'] == upload_res['data']['fileID']:
                is_in_file_list = True
                assert file == upload_res['data']
        assert is_in_file_list

    # @pytest.mark.skip('')
    @allure.title('上传各种大小群文件')
    @pytest.mark.parametrize('file_path', ['../data/im/upload_file/10mb', '../data/im/upload_file/10485759', '../data/im/upload_file/10485761'])
    def test_006(self, file_path):
        with open(file_path, 'rb') as f:
            file_size = len(f.read())
        
        upload_res = self.group_owner.group_share_files_upload(self.group_id, file_path)
        my_log('test_006[群主上传群文件]', file_path, upload_res)
        if file_size <= 10*1024*1024:
            assert upload_res['code'] == '0'
            assert upload_res['data']['fileName'] == os.path.split(file_path)[-1]
        else:
            assert upload_res['code'] == '1' and 'error' in upload_res and upload_res['error']['code'] == 1406 and upload_res['error']['message'] == '文件体积过大'
        
        file_list = get_group_all_share_file(self.group_owner, self.group_id)
        
        is_in_file_list = False
        
        if file_size <= 10*1024*1024:
            for file in file_list:
                if file['fileID'] == upload_res['data']['fileID']:
                    is_in_file_list = True
                    assert file == upload_res['data']
            assert is_in_file_list
        else:
            for file in file_list:
                if file['fileID'] == upload_res['data']['fileID']:
                    is_in_file_list = True
            assert is_in_file_list is False

    # @pytest.mark.skip('')
    @allure.title('上传各种格式群文件')
    @pytest.mark.parametrize('file_path', ['../data/im/upload_file/test.mp4',
                                           '../data/im/upload_file/会合专信交流对接项目组.pptx',
                                           '../data/im/upload_file/会合APP需求说明书_20200619(1)(1).doc',
                                           '../data/im/upload_file/问题汇总.txt', '../data/im/upload_file/新建文件夹.zip',
                                           '../data/im/upload_file/1.mp3', '../data/im/upload_file/.log.1'])
    def test_007(self, file_path):
        upload_res = self.group_owner.group_share_files_upload(self.group_id, file_path)
        my_log('test_007[上传各种格式群文件]', file_path, upload_res)
        assert upload_res['code'] == '0'
        assert upload_res['data']['fileName'] == os.path.split(file_path)[-1]
        # time.sleep(10)
        
        file_list = get_group_all_share_file(self.group_owner, self.group_id)

        is_in_file_list = False
        for file in file_list:
            if file['fileID'] == upload_res['data']['fileID']:
                is_in_file_list = True
                assert file == upload_res['data']
        assert is_in_file_list
        
    @allure.title('上传超过群文件容量上限的文件、群文件共享已达上限，删除文件再上传')
    def test_008(self):
        # todo 确认获取完整的列表
        dst = 1024*1024*1024    # 1GB
        base_dir = '../data/im/upload_file'
        file_size = {}  # 记录文件大小

        for file_name in os.listdir(base_dir):
            file_path = os.path.join(base_dir, file_name)
            if os.path.isfile(file_path):
                if file_name == 'ly.mp3':
                    pass
                else:
                    size = os.path.getsize(file_path)
                    if size <= 1024*1024*10:
                        file_size[file_path] = size

        size_to_file = {v: k for k, v in file_size.items()}  # 大小对应的文件

        count = {k: 0 for k in file_size}   # 记录每个大小文件要上传的数量

        price = sorted([k for k in size_to_file])   # 所有的文件大小，从大到小排序

        while dst > 0 and len(price) > 0:
            _p = price[-1]
            if dst >= _p:
                count[size_to_file[_p]] += (dst // _p)
                dst = dst % _p
            price.pop()

        assert dst == 0

        my_log('test_008', '', count)
        already_upload_size = 0
        already_upload_file_info = []
        for file_path in count:
            if count[file_path] > 0:
                for i in range(count[file_path]):
                    upload_res = self.group_owner.group_share_files_upload(self.group_id, file_path)
                    my_log('test_008[上传群文件]', file_path, upload_res)
                    assert upload_res['code'] == '0'
                    already_upload_size += upload_res['data']['fileSize']
                    print(already_upload_size)
                    already_upload_file_info.append(upload_res['data'])
                    
        assert already_upload_size == 1024*1024*1024

        price = sorted([k for k in size_to_file])
        file_path = size_to_file[choice(price)]
        upload_res = self.group_owner.group_share_files_upload(self.group_id, file_path)
        my_log('test_008[上传超过群文件容量上限的文件]', file_path, upload_res)
        assert upload_res['code'] == '1' and 'error' in upload_res and upload_res['error']['code'] == 1638 and upload_res['error']['message'] == '群共享文件容量限制'
        
        file_list = get_group_all_share_file(self.group_owner, self.group_id)
        
        my_log('test_008[本地记录文件列表]', '', already_upload_file_info)
        my_log('test_008[服务端文件列表]', '', file_list)
        assert already_upload_file_info[::-1] == file_list    # 断言自己上传的文件顺序与服务端是否一致,按时间降序排列
        assert len(file_list) == sum([v for k, v in count.items() if v > 0])
        
        """
        从服务器文件列表中选中一个删除
        """
        del_file_info = choice(file_list)   # fileID, fileName
        
        del_file_res = self.group_owner.group_share_files_del(self.group_id, del_file_info['fileID'])
        my_log('test_008[群文件上限后删除文件]', del_file_info['fileID'], del_file_res)
        assert del_file_res['code'] == '0'
        
        """
        删除成功后再次获取服务端文件列表，确定已经被删除的文件不在服务器列表中
        """
        file_list = get_group_all_share_file(self.group_owner, self.group_id)
        
        assert del_file_info['fileID'] not in {info['fileID']: '' for info in file_list}
        assert len(file_list) == sum([v for k, v in count.items() if v > 0]) - 1
        """
        再次继续上传刚刚删除的文件
        """
        file_path = os.path.join(base_dir, del_file_info['fileName'])
        upload_res = self.group_owner.group_share_files_upload(self.group_id, file_path)
        my_log('test_008[群文件上限后删除再上传]', file_path, upload_res)
        assert upload_res['code'] == '0'
        
        """
        再次确认刚刚上传的文件在服务器列表中
        """
        file_list = get_group_all_share_file(self.group_owner, self.group_id)
            
        assert upload_res['data']['fileID'] in {info['fileID']: '' for info in file_list}
        assert len(file_list) == sum([v for k, v in count.items() if v > 0])

        is_exists = False
        for file_info in file_list:
            if file_info['fileID'] == upload_res['data']['fileID']:
                assert file_info == upload_res['data']
                is_exists = True
                break
        assert is_exists
        """
        群文件上限后删除再上传达到上限之后再上传
        """
        upload_res = self.group_owner.group_share_files_upload(self.group_id, file_path)
        my_log('test_008[群文件上限后删除再上传达到上限之后再上传]', file_path, upload_res)
        assert upload_res['code'] == '1' and 'error' in upload_res and upload_res['error']['code'] == 1638 and upload_res['error']['message'] == '群共享文件容量限制'

    # @pytest.mark.skip('')
    @allure.title('上传包含敏感词汇的群文件')
    def test_009(self):
        file_path = '../data/im/upload_file/ly.mp3'
        upload_res = self.group_owner.group_share_files_upload(self.group_id, file_path)
        my_log('test_009[群主上传包含敏感词汇的群文件]', file_path, upload_res)
        assert upload_res['code'] == '1' and 'error' in upload_res and upload_res['error']['code'] == 1640 and upload_res['error']['message'] == '群共享文件名字包含敏感词汇，请重新设置'
        
        file_list = get_group_all_share_file(self.group_owner, self.group_id)

        assert file_list == []

    # @pytest.mark.skip('')
    @allure.title('删除上传的群文件')
    @pytest.mark.parametrize('identity, is_self_file', [
                            [0, False],
                            [0, True],
                            [1, False],
                            [1, True],
                            [2, False],
                            [2, True]
                            ])
    def test_010(self, identity, is_self_file):
        """
        删除上传的群文件
        :param identity: 删除者身份，0:'群主', 1:'管理员', 2:'普通成员'
        :param is_self_file: 被删除的文件是否为自己上传，False:'其他人', True:'自己'
        """
        file_path = '../data/im/upload_file/1.mp3'
        identitys = {0: '群主', 1: '管理员', 2: '普通成员'}
        who_upload_file = {False: '其他人', True: '自己'}
        print(identitys[identity] + '删除' + who_upload_file[is_self_file] + '上传的文件')
        if identity == 0:
            current_user = self.group_owner
        elif identity == 1:
            manager_id = self.member_list.pop()
            set_manager_res = self.group_owner.set_group_manager(self.group_id, manager_id, 'add')
            my_log('test_010[群主设置管理员]', manager_id, set_manager_res)
            assert set_manager_res['code'] == '0'
            group_manager_list_res = self.group_owner.get_group_manager_list(self.group_id)
            my_log('test_010[管理员列表]', '', group_manager_list_res)
            assert manager_id in [i['userId'] for i in group_manager_list_res['data']]
            current_user = self.users[manager_id]
        else:
            normal_user_id = self.member_list.pop()
            current_user = self.users[normal_user_id]
            
        if is_self_file is True:
            upload_res = current_user.group_share_files_upload(self.group_id, file_path)
        else:
            other_id = self.member_list.pop()
            other_user = self.users[other_id]
            upload_res = other_user.group_share_files_upload(self.group_id, file_path)
            
        assert upload_res['code'] == '0'
        assert upload_res['data']['fileName'] == os.path.split(file_path)[-1]
        
        file_list = get_group_all_share_file(self.group_owner, self.group_id)
            
        assert upload_res['data']['fileID'] in {info['fileID']: '' for info in file_list}
        
        for file_info in file_list:
            if file_info['fileID'] == upload_res['data']['fileID']:
                assert file_info == upload_res['data']
                break
                
        del_file_res = current_user.group_share_files_del(self.group_id, upload_res['data']['fileID'])
        my_log(f'test_010[{identitys[identity]}删除{who_upload_file[is_self_file]}上传的群文件]', upload_res['data']['fileID'], del_file_res)
        if identity == 2 and is_self_file is False:
            assert del_file_res['code'] == '1' and 'error' in del_file_res and del_file_res['error']['code'] == 1604 and del_file_res['error']['message'] == '没有权限进行该操作'
        else:
            assert del_file_res['code'] == '0'
        
        file_list = get_group_all_share_file(self.group_owner, self.group_id)
            
        if identity == 2 and is_self_file is False:
            assert upload_res['data']['fileID'] in {info['fileID']: '' for info in file_list}
        else:
            assert upload_res['data']['fileID'] not in {info['fileID']: '' for info in file_list}


# @pytest.mark.skip('')
@allure.feature('多个群上传同一个文件，再删除')
class TestGroupsDeleteSameFile:
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
        
        self.group_owner_id = choice(self.user_id_list)
        member_list = self.user_id_list[:]
        member_list.remove(self.group_owner_id)
        
        self.group_owner = self.users[self.group_owner_id]
        
        self.group1_id = self.group_owner.create_group(','.join(member_list))['data']['communicationId']
        self.group2_id = self.group_owner.create_group(','.join(member_list))['data']['communicationId']
        self.member_list = member_list
        
    def teardown_class(self):
        self.group_owner.remove_group(self.group1_id)
        self.group_owner.remove_group(self.group2_id)
        for k, v in self.users.items():
            v.logout()
    
    @allure.title('多个群上传同一个文件，再删除')
    def test_001(self):
        file_path = '../data/im/upload_file/1.mp3'
        
        with open(file_path, 'rb') as f:
            file_bin = f.read()
        
        """
        群组1，群组2分别上传该文件
        """
        upload_res1 = self.group_owner.group_share_files_upload(self.group1_id, file_path)
        upload_res2 = self.group_owner.group_share_files_upload(self.group2_id, file_path)

        my_log('test_001[群组1上传文件]', file_path, upload_res1)
        my_log('test_001[群组2上传文件]', file_path, upload_res2)
        assert upload_res1['code'] == '0'
        assert upload_res2['code'] == '0'
        assert upload_res1['data']['fileName'] == os.path.split(file_path)[-1]
        assert upload_res2['data']['fileName'] == os.path.split(file_path)[-1]
        
        file1_uri = upload_res1['data']['fileUri']
        file2_uri = upload_res2['data']['fileUri']
        
        """
        上传完毕后断言能正常下载
        """
        for uri in (file1_uri, file2_uri):
            r = requests.get(uri)
            my_log('test_001[上传完毕后断言能正常下载]', '', r.status_code)
            assert r.status_code == 200, r.status_code
            assert r.content == file_bin
        
        """
        获取完整的群组文件列表，判断刚刚上传的文件在其中
        """
        file_info_list1 = get_group_all_share_file(self.group_owner, self.group1_id)
        file_info_list2 = get_group_all_share_file(self.group_owner, self.group2_id)
        
        assert upload_res1['data']['fileID'] in {v['fileID']: '' for v in file_info_list1}
        assert upload_res2['data']['fileID'] in {v['fileID']: '' for v in file_info_list2}
        
        """
        删除群组1的文件
        """
        del_file_res1 = self.group_owner.group_share_files_del(self.group1_id, upload_res1['data']['fileID'])
        my_log('test_001[删除群组1的文件]', upload_res1['data']['fileID'], del_file_res1)
        assert del_file_res1['code'] == '0'
        
        """
        判断群组1没有这个文件，群组2有这个文件
        """
        file_info_list1 = get_group_all_share_file(self.group_owner, self.group1_id)
        file_info_list2 = get_group_all_share_file(self.group_owner, self.group2_id)
        
        assert upload_res1['data']['fileID'] not in {v['fileID']: '' for v in file_info_list1}
        assert upload_res2['data']['fileID'] in {v['fileID']: '' for v in file_info_list2}
        
        """
        删除群组1的文件后，再次下载群组2的文件，确保能正常下载
        """
        r = requests.get(file2_uri)
        my_log('test_001[删除群组1的文件后，再次下载群组2的文件，确保能正常下载]', '', r.status_code)
        assert r.status_code == 200, r.status_code
        assert r.content == file_bin


# @pytest.mark.skip('')
@allure.feature('群主删除其他群的文件')
class TestGroupOwnerDeleteOtherGroupFile:

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
            
        member_list = self.user_id_list[:]
        
        self.group1_owner_id = choice(member_list)
        member_list.remove(self.group1_owner_id)
        
        self.group2_owner_id = choice(member_list)
        member_list.remove(self.group2_owner_id)
        
        self.group1_owner = self.users[self.group1_owner_id]
        self.group2_owner = self.users[self.group2_owner_id]
        
        self.group1_id = self.group1_owner.create_group(','.join(member_list))['data']['communicationId']
        self.group2_id = self.group2_owner.create_group(','.join(member_list))['data']['communicationId']
        self.member_list = member_list
        
    def teardown_class(self):
        self.group1_owner.remove_group(self.group1_id)
        self.group2_owner.remove_group(self.group2_id)
        for k, v in self.users.items():
            v.logout()
        
    @allure.title('群主删除其他群的文件')
    def test_001(self):
        file_path1 = '../data/im/upload_file/1.mp3'
        file_path2 = '../data/im/upload_file/IM项目周报-20210108.pdf'
        
        upload_res1 = self.group1_owner.group_share_files_upload(self.group1_id, file_path1)
        upload_res2 = self.group2_owner.group_share_files_upload(self.group2_id, file_path2)

        my_log('test_001[群组1上传文件]', file_path1, upload_res1)
        my_log('test_001[群组2上传文件]', file_path2, upload_res2)
        assert upload_res1['code'] == '0'
        assert upload_res2['code'] == '0'
        assert upload_res1['data']['fileName'] == os.path.split(file_path1)[-1]
        assert upload_res2['data']['fileName'] == os.path.split(file_path2)[-1]
        
        file1_uri = upload_res1['data']['fileUri']
        file2_uri = upload_res2['data']['fileUri']
        
        """
        上传完毕后断言能正常下载
        """
        for uri in (file1_uri, file2_uri):
            r = requests.get(uri)
            my_log('test_001[上传完毕后断言能正常下载]', '', r.status_code)
            assert r.status_code == 200, r.status_code
            # assert r.content == file_bin
        
        """
        获取完整的群组文件列表，判断刚刚上传的文件在其中
        """
        file_info_list1 = get_group_all_share_file(self.group1_owner, self.group1_id)
        file_info_list2 = get_group_all_share_file(self.group2_owner, self.group2_id)
        
        assert upload_res1['data']['fileID'] in {v['fileID']: '' for v in file_info_list1}
        assert upload_res2['data']['fileID'] in {v['fileID']: '' for v in file_info_list2}
        
        del_file_res = self.group1_owner.group_share_files_del(self.group2_id, upload_res2['data']['fileID'])
        my_log('test_001[群主1删除群组2的文件]', upload_res2['data']['fileID'], del_file_res)
        assert del_file_res['code'] == '1' and 'error' in del_file_res and del_file_res['error']['code'] == 1604 and del_file_res['error']['message'] == '没有权限进行该操作'

        del_file_res = self.group1_owner.group_share_files_del(self.group1_id, upload_res2['data']['fileID'])
        my_log('test_001[群主1删除群组2的文件, groupId为群组1的]', upload_res2['data']['fileID'], del_file_res)
        assert del_file_res['code'] == '1'
        
        del_file_res = self.group1_owner.group_share_files_del(self.group2_id, upload_res1['data']['fileID'])
        my_log('test_001[群主1删除群组1的文件, groupId为群组2的]', upload_res1['data']['fileID'], del_file_res)
        assert del_file_res['code'] == '1'
        
        file_info_list1 = get_group_all_share_file(self.group1_owner, self.group1_id)
        file_info_list2 = get_group_all_share_file(self.group2_owner, self.group2_id)
        
        assert upload_res1['data']['fileID'] in {v['fileID']: '' for v in file_info_list1}
        assert upload_res2['data']['fileID'] in {v['fileID']: '' for v in file_info_list2}

        for uri in (file1_uri, file2_uri):
            r = requests.get(uri)
            my_log('test_001[异常操作后再断言能正常下载]', '', r.status_code)
            assert r.status_code == 200, r.status_code
