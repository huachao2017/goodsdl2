

import pymysql


def get_data():
    sql = "select sum(p.amount),g.upc from dmstore.payment_detail as p left join dmstore.goods as g on p.goods_id=g.id where p.create_time > '2019-10-14 00:00:00' and p.create_time < '2019-10-17 00:00:00' and p.shop_id=3598 group by g.upc order by sum(p.amount) desc;"
    conn = pymysql.connect('123.103.16.19', 'readonly', password='fxiSHEhui2018@)@)', database='dmstore',
                           charset="utf8", port=3300, use_unicode=True)
    cursor = conn.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    print(results)
    data = []
    for result in results:
        list = [1284,'3598']
        list.append(result[1])
        list.append(0)
        list.append(int(result[0]))
        if result[1] != '6901028062008':
            data.append(tuple(list))

        if len(data) == 2:
            break
    print(len(data))
    conn.close()
    return tuple(data)

def save_data(val):
    conn = pymysql.connect('10.19.68.63', 'gpu_rw', password='jyrMnQR1NdAKwgT4', database='goodsdl',
                           charset="utf8", port=3306, use_unicode=True)
    cursor = conn.cursor()
    sql = "insert into goods_firstgoodsselection(shop_id,template_shop_ids,upc,code,predict_sales_amount) values (%s,%s,%s,%s,%s)"
    try:
        # 执行sql语句
        cursor.executemany(sql, val)
        # 提交到数据库执行
        conn.commit()
        print('ok')
    except:
        # 如果发生错误则回滚
        conn.rollback()
        # 关闭数据库连接
        conn.close()
        print('error')



if __name__ == '__main__':

    a = get_data()
    print(a)
    save_data(a)