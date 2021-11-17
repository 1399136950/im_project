import time

import mysql.connector


class MyDb:

    def __init__(self, host, user, password, database, table):
        if table == '':
            raise ValueError('table name is must')
        else:
            self.conn     = mysql.connector.connect(host=host, user=user, password=password, database=database);
            self.table    = table
            self.cursor   = self.conn.cursor()
            self.init_key()
            self.columns  = self.get_columns()
            self.last_sql = None
    
    def init_key(self):
        self.limitSql = ''
        self.orderSql = ''
        self.key_word = ''
    
    def get_columns(self):
        sql = "SELECT column_name FROM information_schema.columns WHERE table_name='{}'".format(self.table)
        self.cursor.execute(sql)
        res = self.cursor.fetchall()
        self.columns = []
        for info in res:
            self.columns.append(info[0])
        return self.columns
    
    def add(self, data, check_filed=''):
        filed = []
        res = []
        for key in data.keys():
            filed.append(key)
            res.append(data[key])
        filed_str = ''
        res_str = ''
        for i in range(len(filed)):
            if i == len(filed)-1:
                filed_str = '{}{}'.format(filed_str, filed[i])
                res_str = '{}"{}"'.format(res_str, res[i])
            else:
                filed_str = '{}{}{}'.format(filed_str, filed[i], ',')
                res_str = '{}{}{}{}{}'.format(res_str, '"', res[i], '"', ',')
        if check_filed == '':
            try:
                self.exec_sql( "INSERT INTO {} ({}) values ({})".format( self.table, filed_str, res_str ), True )
            except:
                print('err')
            else:
                print("insert into {} ({}) values ({})".format(self.table,filed_str,res_str))
                return True
                # self.conn.commit()
        else:   # 需要检查字段是否唯一
            filter = {}
            filter[check_filed] = data[check_filed]
            if not self.where(filter).select():
                try:
                    self.exec_sql("INSERT INTO {} ({}) values ({})".format(self.table,filed_str,res_str),True)
                except:
                    print('add err')
                else:
                    print("insert success")
                    return True
                    # self.conn.commit()
            else:
                print('exists')
                return False
            return False
        
    def exec_sql(self, sql, commit=False):
        try:
            self.cursor.execute(sql)
        except Exception as e:
            return e
        else:
            if commit:
                self.conn.commit()
            self.last_sql = sql
            return self.cursor.rowcount
    
    def select(self, *args):
        if len(args) > 0:
            columns = ''
            for i in range( len(args) ):
                columns = '{}{}'.format(columns, args[i])
                if i < len(args)-1:
                    columns = '{}{}'.format(columns, ',')
        else:
            raise Exception('key word is empty!')
        sql = "SELECT {} FROM {}".format(columns, self.table) + self.analyzeKeyWord()
        if self.orderSql != '':
            sql = sql + self.orderSql
        if self.limitSql != '':
            sql = sql + self.limitSql
        self.last_sql = sql
        self.cursor.execute(sql)
        self.init_key()
        res = self.cursor.fetchall()
        if len(res) > 0:
            return res
        else:
            return False

    def close(self):
        self.cursor.close()
        self.conn.close()
    
    def where(self, data):
        self.key_word = data
        return self    
    
    def analyzeKeyWord(self):
        if not self.key_word:
            sql = ''
        else:
            if isinstance(self.key_word, dict):
                sqls = []
                for key in self.key_word:
                    sqls.append("{}='{}'".format(key, self.key_word[key]))
                sql = ' WHERE '
                for i in range(len(sqls)):
                    sql = "{}{}".format(sql, sqls[i])
                    if i < len(sqls)-1:
                        sql = "{} AND ".format(sql)
            elif isinstance(self.key_word, str):
                sql = " {} {}".format('WHERE', self.key_word)
        return sql
    
    def delete(self):
        if self.analyzeKeyWord() == '':
            print("can't delete all")
        else:
            sql = 'DELETE FROM {} '.format(self.table) + self.analyzeKeyWord()
            self.exec_sql(sql, True)
            self.init_key()
        
    def analyzeData(self, data):
        sqls = []
        sql = ''
        for key in data:
            sqls.append("{}='{}'".format(key, data[key]))
        for i in range(len(sqls)):
            sql = "{}{}".format(sql, sqls[i])
            if i < len(sqls)-1:
                sql = "{}{}".format(sql, ',')
        return sql
    
    def update(self, data):
        if not self.key_word:
            return False
            self.init_key()
        else:
            sql='UPDATE {} SET {} '.format(self.table, self.analyzeData(data)) + self.analyzeKeyWord()
            self.init_key()
            return self.exec_sql(sql, True)
    
    def orderby(self, str1):
        if str1 != '':
            self.orderSql = " ORDER BY {}".format(str1)
        return self
    
    def limit(self, start, end=''):
        if end == '':
            self.limitSql = ' LIMIT {}'.format(start)
        else:
            self.limitSql = ' LIMIT {},{}'.format(start, end)
        return self


class IM(MyDb):
    
    def __init__(self, table):
        host = ''
        # 
        user = ''
        password = ''
        database = ''
        # table = table
        super().__init__(host, user, password, database, table)


def add_money(org_id, amount):
    a = IM('bill_org_account_entry')
    data = {
        'org_id': org_id,
        'create_time': time.strftime('%Y-%m-%d %H:%M:%S'),
        'deal_time': time.strftime('%Y-%m-%d %H:%M:%S'),
        'type': 1,
        'amount': amount,
        'status': 0,
        'remark': '测试充值',
        'name': '测试充值',
        'method': 3
    }
    res = a.add(data)
    print(res)
    a.close()
    
    
def custom_money(org_id, amount):
    a = IM('bill_org_account_entry')
    data = {
        'org_id': org_id,
        'create_time': time.strftime('%Y-%m-%d %H:%M:%S'),
        'deal_time': time.strftime('%Y-%m-%d %H:%M:%S'),
        'type': 2,
        'amount': -1 * amount,
        'status': 0,
        'remark': '测试消费',
        'name': '测试消费',
        'method': 3
    }
    res = a.add(data)
    print(res)
    a.close()
    

def set_resource_package_amount_max(_id):
    a = IM('org_resource_package')
    res = a.where({'id': _id}).select('total')
    total = res[0][0]
    res = a.where({'id': _id}).update({"used_amount": total})
    print(res)


def set_resource_package_amount_min(_id):
    a = IM('org_resource_package')
    res = a.where({'id': _id}).update({"used_amount": 0})
    print(res)

