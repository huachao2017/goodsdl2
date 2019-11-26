import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
django.setup()
from django.db import connections
from goods.sellgoods.salesquantity.bean import goods_config_disnums,goods_config_safedays,goods_config_shops
class ConfigTableUtil:
    # goods_config_disnums 表
    def select_all_disnums(self,shop_id):
        cursor_ai = connections['default'].cursor()
        cursor_ai.execute('select * from goods_config_disnums where shop_id = {}'.format(shop_id))
        results = cursor_ai.fetchall()
        disnums_inss = []
        if results != None and len(list(results))> 0:
            for row in list(results):
                disnums_ins = goods_config_disnums.ConfigDisnums()
                disnums_ins.id = row[0]
                disnums_ins.shop_id = row[1]
                disnums_ins.shelf_id = row[2]
                disnums_ins.shelf_type = row[3]
                disnums_ins.shelf_depth = row[4]
                disnums_ins.upc = row[5]
                disnums_ins.goods_name = row[6]
                disnums_ins.goods_depth = row[7]
                disnums_ins.single_face_min_disnums = row[8]
                disnums_ins.single_face_max_disnums = row[9]
                disnums_ins.create_time = row[10]
                disnums_ins.update_time = row[11]
                disnums_inss.append(disnums_ins)
        cursor_ai.close()
        return disnums_inss

    def insert_many_disnums(self,data):
        cursor_ai = connections['default'].cursor()
        sql = "insert into goods_config_disnums (shop_id,shelf_id,shelf_type,shelf_depth,upc,goods_name,goods_depth,create_time,update_time) values (%s,%s,%s,%s,%s,%s,%s,%s,%s) "
        cursor_ai.executemany(sql, data)
        cursor_ai.connection.commit()
        cursor_ai.close()

    def update_disnums(self,disnums_ins):
        cursor_ai = connections['default'].cursor()
        sql = "update goods_config_disnums set shelf_type={},shelf_depth={},goods_name={},goods_depth={},create_time={},update_time={} where id = {} "
        sql = sql.format(disnums_ins.shelf_type,disnums_ins.shelf_depth,disnums_ins.goods_name,disnums_ins.goods_depth,disnums_ins.create_time,disnums_ins.update_time,disnums_ins.id)
        cursor_ai.execute(sql)
        cursor_ai.connection.commit()
        cursor_ai.close()

    # goods_config_safedays 操作
    def select_all_safedays(self, shop_id):
        cursor_ai = connections['default'].cursor()
        cursor_ai.execute('select * from goods_config_safedays where shop_id = {}'.format(shop_id))
        results = cursor_ai.fetchall()
        safedays_inss = []
        if results != None and len(list(results)) > 0:
            for row in list(results):
                safedays_ins = goods_config_safedays.ConfigSafedayas()
                safedays_ins.shop_id = row[1]
                safedays_ins.upc = row[2]
                safedays_ins.safe_day_nums = row[3]
                safedays_ins.goods_name = row[4]
                safedays_ins.create_time = row[5]
                safedays_ins.update_time = row[6]
                safedays_inss.append(safedays_ins)
        return safedays_inss

    def insert_many_safedays(self,data):
        cursor_ai = connections['default'].cursor()
        sql = "insert into goods_config_safedays (shop_id,upc,goods_name,safe_day_nums,create_time,update_time) values (%s,%s,%s,%s,%s,%s) "
        cursor_ai.executemany(sql, data)
        cursor_ai.connection.commit()
        cursor_ai.close()



    # goods_config_shops
    def select_all_configshops(self):
        cursor_ai = connections['default'].cursor()
        cursor_ai.execute('select * from goods_config_shops where status = 0 ')
        results = cursor_ai.fetchall()
        cshops_inss  = []
        for row in results:
           cshops_ins =  goods_config_shops.ConfigShops()
           cshops_ins.shop_id = row[1]
           cshops_ins.order_type = row[2]
           cshops_ins.status = row[3]
           cshops_ins.hours_time = []
           cshops_ins.weekdays_time = []
           if  row[4] is not None and row[4] != '':
               if ',' in str(row[4]):
                   for hour in str(row[4]).split(","):
                       cshops_ins.hours_time.append(int(hour))
               else:
                   cshops_ins.hours_time.append(int(row[4]))

           if row[5] is not None and row[5] != '':
               if ',' in str(row[5]):
                   for day in str(row[5]).split(","):
                       cshops_ins.weekdays_time.append(int(day))
               else:
                   cshops_ins.weekdays_time.append(int(row[5]))
           cshops_inss.append(cshops_ins)


        return cshops_inss