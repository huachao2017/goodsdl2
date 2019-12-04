import main.import_django_settings

# from django.db import connection
# cursor=connection.cursor()

from django.db import connections
cursor=connections['default'].cursor()

class DjangoMysql:
    cursor = None
    def __init__(self,name):
        self.cursor = connections[name].cursor()
    def selectOne(self,sql):
        self.cursor.execute(sql)
        # 获取所有记录列表
        result = self.cursor.fetchone()
        # for row in results:
        #     uuid_list.append(str(row[0]))
        return result

    def selectAll(self,sql):
        self.cursor.execute(sql)
        # 获取所有记录列表
        results = self.cursor.fetchall()
        # for row in results:
        #     uuid_list.append(str(row[0]))
        return results

    def close(self):
        self.cursor.close()

if __name__=='__main__':
    dj_ins = DjangoMysql("ucenter")
    dj_ins.selectOne("select display_goods_info from sf_taizhang_display where id = 25")