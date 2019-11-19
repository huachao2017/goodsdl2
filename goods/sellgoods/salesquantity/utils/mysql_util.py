import pymysql
from set_config import config
class MysqlUtil:
    cursor = None
    conn = None
    def __init__(self,dbcontext=None):
        conn = pymysql.connect(
            host=dbcontext['host'],
            port=int(dbcontext['port']),
            user=dbcontext['user'],
            passwd=dbcontext['password'],
            db=dbcontext['database'],
            charset='utf8',
            connect_timeout = 3000,
            read_timeout=3000
        )
        self.conn = conn
        self.cursor = conn.cursor()
    #cursor
    def insert_many(self,data):
        cursor = self.cursor
        cursor.executemany('insert into ai_sales_goods (shop_id,class_three_id,day_sales,upc) value(%s,%s,%s,%s)',data)
        cursor.connection.commit()
        cursor.close()
        self.conn.close()

    def selectAll(self, sql):
        cursor = self.cursor
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchall()
        # for row in results:
        #     uuid_list.append(str(row[0]))
        return results

    def selectOne(self, sql):
        cursor = self.cursor
        cursor.execute(sql)
        # 获取所有记录列表
        results = cursor.fetchone()
        # for row in results:
        #     uuid_list.append(str(row[0]))
        return results

    def delete_sql(self,sql):
        cursor = self.cursor
        cursor.execute(sql)
        cursor.connection.commit()
        # cursor.close()
        # self.conn.close()

    def insert_many_sql(self,data,sql):
        cursor = self.cursor
        cursor.executemany(sql,data)
        cursor.connection.commit()
        # cursor.close()
        # self.conn.close()
if __name__=='__main__':
    mysql_ins = MysqlUtil(config.erp_dev)
    # data =  [(3220, 0, 155936, "1111111111111111111111")]
    # mysql_ins.insert_many(data)
    sql = "insert into ai_sales_goods (shop_id,upc,day_week,day,day_sales,next_day,nextday_predict_sales,nextdays_predict_sales) value(%s,%s,%s,%s,%s,%s,%s,%s)"

    del_sql = "delete from ai_sales_goods where next_day = {0}"

    data = [('3598','20449896','5','2019-10-18',100,'2019-10-19',200,'[2,3,4,5,6,7,8]')]
    del_sql = del_sql.format(data[0][5])
    mysql_ins.delete_sql(del_sql)
    print ("del predict sucess")
    mysql_ins.insert_many_sql(data,sql)
    print ("insert predict sucess")
    mysql_ins.cursor.close()
    mysql_ins.conn.close()

