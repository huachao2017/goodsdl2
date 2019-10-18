

import pymysql,time
# upc_data_sql="select sum(T2.t1_nums) as ai_nums,T2.t1_shop_id as ai_shop_id ,T3.upc as ai_upc,T2.t1_create_date as  ai_create_date,DATE_FORMAT( from_unixtime(unix_timestamp(DATE_FORMAT(T2.t1_create_date ,'%Y-%m-%d'))+24*3600),'%Y-%m-%d') as ai_next_date,DAYOFWEEK(DATE_FORMAT(from_unixtime(unix_timestamp(DATE_FORMAT(T2.t1_create_date ,'%Y-%m-%d'))-24*3600),'%Y-%m-%d')) as ai_week_date from ( "
# +               "select sum(T1.nums) as t1_nums,T1.shop_id as t1_shop_id,T1.shop_goods_id,T1.create_date as t1_create_date  from "
# +               "(select number nums,shop_id,shop_goods_id,DATE_FORMAT(create_time,'%Y-%m-%d') 	create_date from payment_detail "
# +        "where shop_id is not null and shop_id in {4} and goods_id is not null and number > 0 and create_time > '{0} 00:00:00' and create_time < '{1} 00:00:00' and "
# +       "payment_id in ( "
# +            "select distinct(payment.id) from payment where payment.type != 50  and create_time > '{2} 00:00:00' and create_time < '{3} 00:00:00' "
# +					") "
# +            ")  T1 "
# +               "group by T1.shop_id,T1.shop_goods_id,T1.create_date) T2 "
# +                   "left join  shop_goods T3 on T2.t1_shop_id= T3.shop_id and T2.shop_goods_id = T3.id "
# +                   "where T3.upc != '' and  T3.upc != '0' "
# +                   "group by T2.t1_create_date,T2.t1_shop_id,T3.upc "
# upc_data_sql.format()
def get_data():
    sql = "select sum(p.amount),g.upc,g.corp_classify_code,g.neighbor_goods_id from dmstore.payment_detail as p left join dmstore.goods as g on p.goods_id=g.id where p.create_time > '2019-10-14 00:00:00' and p.create_time < '2019-10-17 00:00:00' and p.shop_id=3598 group by g.upc order by sum(p.amount) desc;"
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
        list.append(result[2])
        list.append(int(result[0]))
        list.append(result[3])
        if result[1] != '6901028062008':
            data.append(tuple(list))

        # if len(data) == 2:
        #     break
    print(len(data))
    conn.close()
    return tuple(data)

def choose_goods(data,ratio=0.7):
    result = []
    goods_dict ={}
    for d in data:
        code = d[3]
        upc = d[1]
        first = code[:2]
        if not d in goods_dict:
            goods_dict[first] = {}
        second = code[2:4]
        if not second in goods_dict[first]:
            goods_dict[first][second] = {}
        third = code[4:6]
        if not third in goods_dict[first][second]:
            goods_dict[first][second][third] = []
        goods_dict[first][second][third].append(d)

    for f in goods_dict:
        for s in f:
            tem = []
            for t in s:
                upcs = goods_dict[f][s][t]
                l = len(upcs)
                if l > 2:
                    m = int(l*ratio)
                    upcs.sort(key=lambda x: x[4], reverse=True)    #基于销量排序
                    result += upcs[:m]
                else:
                    tem.extend(upcs)
            tem.sort(key=lambda x: x[4], reverse=True)
            n = int(len(tem)*ratio)
            result += tem[:n]

    result.sort(key=lambda x: x[4], reverse=True)
    return result




def save_data(data):
    conn = pymysql.connect('10.19.68.63', 'gpu_rw', password='jyrMnQR1NdAKwgT4', database='goodsdl',charset="utf8", port=3306, use_unicode=True)
    cursor = conn.cursor()
    # sql = "insert into goods_firstgoodsselection(shopid,template_shop_ids,upc,code,predict_sales_amount) values (%s,%s,%s,%s,%s)"
    update_sql = "update goods_firstgoodsselection set mch_goods_code={},mch_code=2 where upc={}"
    for i in data:
        cursor.executemany(update_sql.format(i[5],i[2]))
        conn.commit()
        time.sleep(0.5)





    # try:
    # 执行sql语句
    # cursor.executemany(sql, data)
    # conn.commit()
    print('ok')
    # except:
    #     # 如果发生错误则回滚
    #     conn.rollback()
    #     # 关闭数据库连接
    #     conn.close()
    #     print('error')



if __name__ == '__main__':

    a = get_data()
    print(a)
    b = choose_goods(a)

    # print(b)
    # print(len(a))
    # print(len(b))

    # save_data(a)
