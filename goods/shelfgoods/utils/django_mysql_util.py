import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
django.setup()

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
        result = cursor.fetchone()
        # for row in results:
        #     uuid_list.append(str(row[0]))
        return result

    def selectAll(self,sql):
        self.cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        # for row in results:
        #     uuid_list.append(str(row[0]))
        return results

    def close(self):
        self.cursor.close()