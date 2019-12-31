import decimal
import json
from  decimal import Decimal
import datetime,pymysql
import os,django,math,copy
from goods.third_tools.dingtalk import send_message

import main.import_django_settings
from django.db import connections

class DataProcess():

    def __init__(self,pos_shop_id):
        self.pos_shop_id = pos_shop_id
        self.days = 28
        self.supplier_id_list = []       # 供应商id，可以多个
        self.can_order_mch_list = []
        self.dmstore_cursor = connections['dmstore'].cursor()


    def get_data(self):
        can_order_mch_list, _ = self.get_can_order_dict()
        now = datetime.datetime.now()
        now_date = now.strftime('%Y-%m-%d %H:%M:%S')
        week_ago = (now - datetime.timedelta(days=self.days)).strftime('%Y-%m-%d %H:%M:%S')
        sql = "select p.payment_id,GROUP_CONCAT(g.neighbor_goods_id) n from dmstore.payment_detail as p left join dmstore.goods as g on p.goods_id=g.id where p.create_time > '{}' and p.create_time < '{}' and g.neighbor_goods_id in ({}) GROUP BY p.payment_id having COUNT(g.neighbor_goods_id) >1"
        self.dmstore_cursor.execute(sql.format(week_ago, now_date,','.join(can_order_mch_list)))
        all_data = self.dmstore_cursor.fetchall()
        print(len(all_data))
        # for data in all_data:




    def get_can_order_dict(self):
        """
        获取可订货的7位得mch_goods_code的字典，value为配送类型，k为店内码,从saas查询
        :return:
        """
        self.dmstore_cursor.execute("SELECT erp_shop_id from erp_shop_related WHERE shop_id ={} AND erp_shop_type=0;".format(self.pos_shop_id))
        try:
            erp_shop_id = self.dmstore_cursor.fetchone()[0]
        except:
            print('erp_shop_id获取失败！')
            return []
        try:
            ms_conn = connections["erp"]
            ms_cursor = ms_conn.cursor()
            ms_cursor.execute("SELECT authorized_shop_id FROM ms_relation WHERE is_authorized_shop_id IN (SELECT authorized_shop_id FROM	ms_relation WHERE is_authorized_shop_id = {} AND STATUS = 1) AND STATUS = 1".format(erp_shop_id))
            all_data = ms_cursor.fetchall()
            supplier_code = []
            for data in all_data:
                supplier_code.append(str(data[0]))
        except:
            print('supplier_code获取失败！')
            return []


        # 获取商品的 可定 配送类型
        conn_ucenter = connections['ucenter']
        cursor_ucenter = conn_ucenter.cursor()
        delivery_type_dict = {}    # 店内码是key，配送类型是value
        can_order_list = []   #可订货列表
        try:
            cursor_ucenter.execute("select id from uc_supplier where supplier_code in ({})".format(','.join(supplier_code)))
            all_supplier_id_data = cursor_ucenter.fetchall()
            for supplier_data in all_supplier_id_data:
                self.supplier_id_list.append(str(supplier_data[0]))

            cursor_ucenter.execute(
                "select supplier_goods_code from uc_supplier_goods where supplier_id in ({}) and order_status = 1 ".format(','.join(self.supplier_id_list)))
                # "select a.supplier_goods_code,b.delivery_attr from uc_supplier_goods a LEFT JOIN uc_supplier_delivery b on a.delivery_type=b.delivery_code where a.supplier_id = {} and order_status = 1".format(supplier_id))
                # 有尺寸数据
                # "select DISTINCT a.supplier_goods_code,b.delivery_attr from uc_supplier_goods a LEFT JOIN uc_supplier_delivery b on a.delivery_type=b.delivery_code LEFT JOIN uc_merchant_goods c on a.supplier_goods_code=c.supplier_goods_code where a.supplier_id = {} and order_status = 1 and c.width > 0 and c.height > 0 and c.depth > 0".format(supplier_id))
            all_data = cursor_ucenter.fetchall()
            for data in all_data:
                delivery_type_dict[data[0]] = data[1]
                can_order_list.append(data[0])
        except:
            print('pos店号是{},查询是否可订货和配送类型失败'.format(self.pos_shop_id))
        return can_order_list,delivery_type_dict

if __name__ == '__main__':
    p = DataProcess(1284)
    p.get_data()