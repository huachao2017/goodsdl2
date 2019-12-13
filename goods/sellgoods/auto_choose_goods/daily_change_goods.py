
"""
日常换品
"""
import decimal
import json
from  decimal import Decimal
import datetime,pymysql
import os,django,math

import main.import_django_settings
from django.db import connections

class DailyChangeGoods:
    """
    目前只是非日配的日常换品逻辑
    """

    def __init__(self,shop_id,template_shop_ids,batch_id,topn_ratio=0.6,days=28):
        self.category_goods_list = []    # 结构品
        self.template_shop_ids = template_shop_ids.split(',')
        self.shop_id = shop_id
        self.uc_shopid = None
        self.batch_id = batch_id
        self.topn_ratio = Decimal(topn_ratio)  # 取累计psd金额的百分之多少作为畅销品
        self.days = days     # 取数周期
        self.third_category_list = []      # 三级分类的列表
        self.first_category_goods_count_dict = {}     # 一级分类选品预估的数量

        conn = pymysql.connect('123.103.16.19', 'readonly', password='fxiSHEhui2018@)@)', database='dmstore',charset="utf8", port=3300, use_unicode=True)
        self.cursor = conn.cursor()
        # self.cursor = connections['dmstore'].cursor()

    def get_shop_sales_data(self, shop_id):
        """
        获取该店有销量的商品的psd金额的排序列表
        :param shop_id:
        :return:
        """
        now = datetime.datetime.now()
        now_date = now.strftime('%Y-%m-%d %H:%M:%S')
        week_ago = (now - datetime.timedelta(days=self.days)).strftime('%Y-%m-%d %H:%M:%S')
        sql = "select sum(p.amount),g.upc,g.corp_classify_code,g.neighbor_goods_id,g.price,p.name from dmstore.payment_detail as p left join dmstore.goods as g on p.goods_id=g.id where p.create_time > '{}' and p.create_time < '{}' and p.shop_id = {} group by g.upc order by sum(p.amount) desc;"
        self.cursor.execute(sql.format(week_ago, now_date, shop_id))
        results = self.cursor.fetchall()
        return results

    def get_third_category_data(self, third_category, shop_ids):
        """
        获取某些门店的某三级分类下的按照psd金额排序的列表数据
        :param third_category: 三级分类
        :param shop_ids: 门店的ids
        :return:
        """
        # print(shop_ids)

        now = datetime.datetime.now()
        now_date = now.strftime('%Y-%m-%d %H:%M:%S')
        week_ago = (now - datetime.timedelta(days=self.days)).strftime('%Y-%m-%d %H:%M:%S')
        if type(shop_ids) is list:       # 多个门店
            print('list,third_category',shop_ids,third_category)
            shop_ids = tuple(shop_ids)
            sql = "select sum(p.amount),g.upc,g.corp_classify_code,g.neighbor_goods_id,g.price,p.name from dmstore.payment_detail as p left join dmstore.goods as g on p.goods_id=g.id where p.create_time > '{}' and p.create_time < '{}' and p.shop_id in {} and g.corp_classify_code={} group by g.upc order by sum(p.amount) desc;"
        elif type(shop_ids) is str:     # 单个门店
            print('str',shop_ids,type(shop_ids))
            sql = "select sum(p.amount),g.upc,g.corp_classify_code,g.neighbor_goods_id,g.price,p.name from dmstore.payment_detail as p left join dmstore.goods as g on p.goods_id=g.id where p.create_time > '{}' and p.create_time < '{}' and p.shop_id = {} and g.corp_classify_code={} group by g.upc order by sum(p.amount) desc;"
        else:
            print('none', shop_ids,type(shop_ids))
            return None
        self.cursor.execute(sql.format(week_ago, now_date, shop_ids,third_category))
        results = self.cursor.fetchall()
        # cursor.close()

        print(results)
        print(len(results))
        return results

    def get_third_category_list(self):
        """
        获取一段取数周期内，所有模板店的有销量的品的所有三级分类的code的列表
        :return:
        """
        now = datetime.datetime.now()
        now_date = now.strftime('%Y-%m-%d %H:%M:%S')
        week_ago = (now - datetime.timedelta(days=self.days)).strftime('%Y-%m-%d %H:%M:%S')
        sql = "select distinct g.corp_classify_code from dmstore.payment_detail as p left join dmstore.goods as g on p.goods_id=g.id where p.create_time > '{}' and p.create_time < '{}' and p.shop_id in {};"
        template_shop_ids_tuple = tuple(self.template_shop_ids)
        self.cursor.execute(sql.format(week_ago, now_date, template_shop_ids_tuple))
        results = self.cursor.fetchall()
        print('get_third_category_list',results)
        return [i[0] for i in results if len(i[0]) == 6]    #存在空的情况，所以if len(i[0]) == 6

    def get_sale_goods(self):
        """
        获取该店在售的商品
        :return:
        """
        sql = "SELECT upc,name FROM shop_goods WHERE shop_id = {} AND STATUS=10;"   # TODO 要哪些字段
        self.cursor.execute(sql.format(self.shop_id))
        results = self.cursor.fetchall()
        return results

    def get_taizhang_goods(self):
        """
        获取当前台账的商品列表
        :return:
        """
        uc_conn = connections['ucenter']
        uc_cursor = uc_conn.cursor()
        # 获取台账系统的uc_shopid
        uc_cursor.execute('select id from uc_shop where mch_shop_code = {}'.format(self.shop_id))
        self.uc_shopid = uc_cursor.fetchone()[0]
        # 获取当前的台账
        select_sql_02 = "select t.id, t.shelf_id, td.batch_no,td.display_shelf_info, td.display_goods_info from sf_shop_taizhang st, sf_taizhang t, sf_taizhang_display td where st.taizhang_id=t.id and td.taizhang_id=t.id and td.status=2 and td.approval_status=1 and st.shop_id = {}".format(self.uc_shopid)
        uc_cursor.execute(select_sql_02)
        all_data = uc_cursor.fetchall()
        taizhang_data_list = []
        for data in all_data:
            for goods_info in json.loads(data[4]):
                for layer in goods_info['layerArray']:
                    for goods in layer:
                        # goods_upc = goods['goods_upc']
                        taizhang_data_list.append(goods)
        return taizhang_data_list

    def get_third_category(self,mch_code):
        pass


    def calculate_first_category_goods_count(self):
        """
        计算一级分类需要选品的预估数量
        :return:
        """
        # 1、获取该店有哪些一级分类可售

        # 2、获取每个一级分类分配的货架面积

        # 3、计算每个一级分类下的平均商品面积

        # 4、计算每个一级分类的预估选品数
        pass

    def calculate_quick_seller(self):
        """
        获取该组多个门店的畅销品和结构品（目前是每三级分类下psd金额top1）
        同组门店中每个三级分类下： 4周的psd金额或psd /（门店数*在售天数）的累计前60-70%
        目前门店数是根据取数周期内的有销售的门店进行统计的，因为该品在该店是否上架的数据不准
        在售天数则默认一直在售
        :param topn:
        :return:
        """
        # template_shop_ids_list = self.template_shop_ids.split(',')
        #
        # all_goods = []  # 每个店的畅销品的去重汇总
        # quick_seller_list_all = []  # 每个店的畅销品列表是其值
        # for template_shop_id in template_shop_ids_list:
        #     data = self.get_data(template_shop_id)
        #     quick_seller_list = data[:int(len(data) * self.topn_ratio)]
        #     quick_seller_list_all.append(quick_seller_list)
        #     for d in quick_seller_list:
        #         if not d in all_goods:
        #             all_goods.append(d)
        # goods_time_dict = {}  # 商品出现在各模板店畅销品列表的次数，k为goods，v为次数
        # for goods in all_goods:
        #     temp_num = 0
        #     for quick_seller_list in quick_seller_list_all:
        #         for quick_seller in quick_seller_list:
        #             if goods[1] == quick_seller[1]:
        #                 temp_num += 1
        #     goods_time_dict[goods[1]] = temp_num
        # print(goods_time_dict)
        # return goods_time_dict

        self.third_category_list = self.get_third_category_list()
        print('self.third_category_list',self.third_category_list)
        category_dict = {}    # k为三级分类，v为分类下的商品列表
        for third_category in self.third_category_list[:]:      # 遍历每个三级分类
            all_shop_data = self.get_third_category_data(third_category, self.template_shop_ids)
            # 以下14行代码主要是统计upc取数周期内在各店出现的次数
            all_one_shop_data_list = []
            for template_shop_id in self.template_shop_ids:
                one_shop_data = self.get_third_category_data(third_category, template_shop_id)
                all_one_shop_data_list.append(one_shop_data)
            all_upc = [i[1] for i in all_shop_data]   #FIXME
            upc_time = {}           # upc在各店出现的次数，k为upc，v为次数
            for upc in all_upc:
                temp_num = 0
                for one_shop_data in all_one_shop_data_list:
                    for data in one_shop_data:
                        if upc == data[1]: #FIXME
                            temp_num += 1
                if temp_num > 2:    # 将出现大于2次的都加进去
                    upc_time[upc] = temp_num


            print('upc_time',upc_time)
            third_category_quick_seller_list = []
            for data in all_shop_data:     # psd金额除以商店数
                try:
                    # template_shop_ids,upc,code,predict_sales_amount,mch_goods_code,predict_sales_num,name
                    third_category_quick_seller_list.append([','.join(self.template_shop_ids), data[1], data[2], data[0]/(upc_time[data[1]]*self.days), data[3],data[0]/(upc_time[data[1]]*self.days*data[4]), data[5]])
                except:
                    print('11111')
            category_dict[third_category] = third_category_quick_seller_list

        quick_seller_list = []
        structure_goods_list = []
        for category, goods_list in category_dict.items():
            goods_list.sort(key=lambda x: x[3], reverse=True)  # 基于psd金额排序
            print('goods_list',goods_list)


            # --以下是把第一个加进去，算的是结构品
            structure_goods_list.append(goods_list[0])

            # --以下是求累计
            amount = 0  # 分类下psd金额的总额
            for goods in goods_list:
                amount += goods[1]
            temp_amount = 0
            for goods in goods_list:  # 将累计前占比60%psd金额的商品选出来，遇到边界少选策略
                # quick_seller_list.append(goods[0])   # 遇到边界多选策略
                temp_amount += goods[1]
                if temp_amount > amount * self.topn_ratio:
                    break
                quick_seller_list.append(goods)   # 遇到边界少选策略

        structure_goods_list.sort(key=lambda x: x[3], reverse=True)  # 基于psd金额排序
        quick_seller_list.sort(key=lambda x: x[3], reverse=True)  # 基于psd金额排序
        return structure_goods_list, quick_seller_list

    def get_can_order_list(self):
        """
        获取可订货的mch_code的列表
        :return:
        """
        sql = "SELECT erp_shop_id from erp_shop_related WHERE shop_id='{}' and erp_shop_type=2"
        self.cursor.execute(sql.format(self.shop_id))
        erp_shop_id = self.cursor.fetchone()[0]

        ms_conn = connections['erp']     # 魔兽系统库
        ms_cursor = ms_conn.cursor()
        sql_02 = "SELECT p.model_id,p.party_code from ls_prod p, ms_sku_relation ms WHERE ms.prod_id=p.prod_id AND  p.shop_id='{}' AND ms.status=1;"
        ms_cursor.execute(sql_02.format(erp_shop_id))
        results = ms_cursor.fetchall()
        return [i[1] for i in results]

    def calculate_optional_out_goods(self,category_03_list):
        """
        计算可选下架的品
        :return:
        """
        for category in category_03_list:
            data = self.get_third_category_data(category,self.shop_id)
            pass



    def recommend(self):

        # 1、遍历一级分类
        # 2、计算畅销品，检查是否可订货
        # 3、计算结构品，检查是否可订货和是否在畅销品列表里，进行删减去重
        # 4、其他候补品，检查是否可订货，最终加起来是预估选品的120%
        # 4.1、先根据‘预估选品减去畅销和结构’计算出剩余该选的数量
        # 4.2、计算一级分类下psd金额排序列表，依次选出检查是否在畅销品、结构品、可订货列表中，然后加到候补品列表中，加满为止

        quick_seller = self.calculate_quick_seller()
        print('quick_seller',quick_seller)
        print('quick_seller',len(quick_seller))







        # print('quick_seller_list',quick_seller_list)
        # print('quick_seller_list长度',len(quick_seller_list))
        # TODO 畅销品列表计算

        self.calculate_category_goods()   #计算结构品的数据

        sale_goods = self.get_sale_goods()  # 在售的商品
        sale_goods_upc_list = [i[0] for i in sale_goods]
        print('sale_goods',sale_goods)
        print('sale_goods',len(sale_goods))
        print('sale_goods_upc_list',sale_goods_upc_list)
        recommend_list = []
        for goods in self.category_goods_list:
            if goods not in sale_goods:        #FIXME goods是一回事吗
                recommend_list.append(goods)

        # for goods in quick_seller_list:
        #     if goods not in sale_goods_upc_list and goods not in recommend_list:
        #         recommend_list.append(goods)

        return recommend_list

    def recommend_02(self):
        """
        计算得出汰换的必须陈列列表、可选陈列列表
        :return:
        """
        must_display_old_goods = []     # 必须陈列的旧品
        optional_display_goods = []     # 可选陈列列表
        must_display_new_goods = []     # 必须的陈列的新加的品

        # 1、计算本店a+b类品和结构品
        #   1.1、获取本店有销量的商品
        sales_data = self.get_shop_sales_data(self.shop_id)
        sales_goods_mch_code_dict = {}
        for s in sales_data:
            sales_goods_mch_code_dict[s[3]] = s
        print(len(sales_data))

        #   1.2、获取当前台账的商品
        taizhang_goods = self.get_taizhang_goods()  # 获取当前台账的商品
        taizhang_goods_mch_code_list = [i['mch_goods_code'] for i in taizhang_goods]
        all_goods_len = len(taizhang_goods)

        #   1.3、遍历台账商品,得出必须陈列的旧品和可选陈列
        for data in taizhang_goods:
            if data['mch_goods_code'] in sales_goods_mch_code_dict:
                # template_shop_ids,upc,code,predict_sales_amount,mch_goods_code,predict_sales_num,name
                must_display_old_goods.append((None,data['goods_upc'],sales_goods_mch_code_dict[data['mch_goods_code']][2],None,data['mch_goods_code'],None,data['name']))
            else:
                optional_display_goods.append((None,data['goods_upc'],None,None,data['mch_goods_code'],None,data['name'])) #FIXME 分类code为空

        # 2、计算新增品
        selected_quick_seller_len = math.ceil(all_goods_len * 0.03)
        quick_seller = self.calculate_quick_seller()    # 获取同组门店的畅销品
        for data in quick_seller:
            if not data[3] in taizhang_goods_mch_code_list:
                must_display_new_goods.append(data)
                if len(must_display_new_goods) == selected_quick_seller_len:
                    break

        # 3、保存至数据库
        self.save_data(must_display_old_goods, 0, 1, 0)
        self.save_data(optional_display_goods, 0, 0, 0)
        self.save_data(must_display_new_goods, 1, 1, 0)

    def recommend_03(self):


        not_move_goods = []   # 没有变动的品

        must_up_goods = []  # 必须上架的品
        optional_up_goods = []  # 可选上架的品
        must_out_goods = []  # 必须下架的品
        optional_out_goods = []  # 可选下架的品

        category_03_list = []   # 本店已有三级分类的code列表


        # 1、计算本店a+b类品和结构品
        #   1.1、获取本店有销量的商品
        sales_data = self.get_shop_sales_data(self.shop_id)
        sales_goods_mch_code_dict = {}
        for s in sales_data:
            sales_goods_mch_code_dict[str(s[3])] = s
        # print('sales_goods_mch_code_dict',sales_goods_mch_code_dict)

        #   1.2、获取当前台账的商品
        taizhang_goods = self.get_taizhang_goods()  # 获取当前台账的商品
        taizhang_goods_mch_code_list = [i['mch_goods_code'] for i in taizhang_goods]
        all_goods_len = len(taizhang_goods)
        print('台账goods',all_goods_len)

        #   1.3、遍历货架,得出每个货架的三级分类和该店所有的三级分类
        can_order_mch_code_list = self.get_can_order_list()
        print('可订货len：',len(can_order_mch_code_list))
        for data in taizhang_goods:
            if not data['mch_goods_code'] in can_order_mch_code_list:    # 不可订货即必须下架
                # template_shop_ids,upc,code,predict_sales_amount,mch_goods_code,predict_sales_num,name,ranking
                must_out_goods.append((None, data['goods_upc'], None, None, data['mch_goods_code'], None, data['name'],None))
            elif data['mch_goods_code'] in sales_goods_mch_code_dict.keys():    # 有销量即为不动的品
                print('有销量即为不动的品')
                not_move_goods.append((None, data['goods_upc'],sales_goods_mch_code_dict[data['mch_goods_code']][2], None,data['mch_goods_code'], None, data['name'],None))
            else:       # 剩下没销量的为可选下架的品
                optional_out_goods.append((None, data['goods_upc'], None, None, data['mch_goods_code'], None, data['name'],1))  # FIXME 分类code为空

        # # 2、计算新增品
        # must_up_goods_len = math.ceil(all_goods_len * 0.03)
        # all_structure_goods_list, all_quick_seller_list = self.calculate_quick_seller()  # 获取同组门店的结构品和畅销品
        # structure_goods_list = []     # 该店没有该三级分类的结构品列表
        # for data in all_structure_goods_list:
        #     if not data[2] in category_03_list:
        #         structure_goods_list.append(data)
        #
        # quick_seller_list = []     # 该店没有的畅销品
        # for data in all_quick_seller_list:
        #     if not data[3] in taizhang_goods_mch_code_list:
        #         quick_seller_list.append(data)
        #
        # candidate_up_goods_list = structure_goods_list + quick_seller_list     #FIXME  怎么综合一下
        # must_up_goods = candidate_up_goods_list[:must_up_goods_len]
        # optional_up_goods = candidate_up_goods_list[must_up_goods_len:]
        # # 以下4行时添加ranking的值
        # for goods in must_up_goods:
        #     goods.append(None)
        # for index,goods in enumerate(optional_up_goods):
        #     goods.append(index+1)






        # 3、保存至数据库

        not_move_goods = list(set(not_move_goods))
        must_out_goods = list(set(must_out_goods))
        optional_out_goods = list(set(optional_out_goods))

        print(len(not_move_goods))
        print(len(must_out_goods))
        print(len(optional_out_goods))

        self.save_data(not_move_goods, 0, 2, None)
        self.save_data(must_out_goods, 0, 1, None)
        self.save_data(optional_out_goods, 0, 0, None)
        # self.save_data(must_up_goods, 1, None, 1)
        # self.save_data(optional_up_goods, 1, None, 0)

    def save_data(self,data,is_new_goods,goods_out_status,goods_add_status):
        """
        保存选品的数据
        :param batch_id: 批次号
        :param is_new_goods: 是否是新增的品，1代表是，0代表否
        :param goods_out_status:下架状态，0：可选下架，1：必须下架，2：不动的品
        :param goods_add_status:新增上架状态，0：可选上架，1：必须上架
        :return:
        """
        tuple_data = tuple(data)

        conn = connections['default']
        cursor = conn.cursor()

        # insert_sql_01 = "insert into goods_firstgoodsselection(shopid,template_shop_ids,upc,code,predict_sales_amount,mch_code,mch_goods_code,predict_sales_num,name,batch_id,uc_shopid) values (%s,%s,%s,%s,%s,2,%s,%s,%s,'{}','{}')"
        insert_sql_02 = "insert into goods_goodsselectionhistory(shopid,template_shop_ids,upc,code,predict_sales_amount,mch_code,mch_goods_code,predict_sales_num,name,batch_id,uc_shopid,is_new_goods,goods_out_status,goods_add_status,ranking) values ({},%s,%s,%s,%s,2,%s,%s,%s,'{}','{}',{},{},{},s%)"
        delete_sql_02 = "delete from goods_goodsselectionhistory where uc_shopid={} and batch_id='{}'"
        select_sql = "select batch_id from goods_goodsselectionhistory where uc_shopid={} and batch_id='{}'"
        # try:
        print('batch_id', self.batch_id, type(self.batch_id))
        print('len',len(tuple_data))
        cursor.execute(select_sql.format(self.uc_shopid, self.batch_id))  # 查询有该批次，没有的话，插入，有的话，先删再插入
        # print('history_batch_id', history_batch_id,type(history_batch_id))
        if cursor.fetchone():
            cursor.execute(delete_sql_02.format(self.uc_shopid, self.batch_id))
            print("删掉{}该批次之前的数据".format(self.batch_id))
        cursor.executemany(insert_sql_02.format(self.shop_id,self.batch_id, self.uc_shopid,is_new_goods,goods_out_status,goods_add_status), tuple_data[:])
        conn.commit()
        conn.close()
        print('ok')
        # except:
        #     # 如果发生错误则回滚
        #     conn.rollback()
        #     cursor.close()
        #     conn.close()
        #     print('error')




def start_choose_goods(batch_id,uc_shop_id,pos_shopid):
    pass

if __name__ == '__main__':

    f = DailyChangeGoods(1284, "3955,3779,1925,4076,1924",'lishu_test_001')
    # data = first_choose_goods.recommend()
    # # data = add_goods.get_third_category_list()
    # print('最终增品',data)
    # print('最终增品长度',len(data))
    f.recommend_03()





# quick_seller {'070303': [['6932697610221', Decimal('6050')], ['6932697610344', Decimal('4216.666666666666666666666667')], ['6931760312192', Decimal('6760')]], '100203': [['6926265313386', Decimal('35575')], ['6921286902335', Decimal('21567.5')], ['4710199086506', Decimal('20712.5')], ['089686727050', Decimal('25155')], ['6936605800063', Decimal('13750')], ['4710543613501', Decimal('11250')], ['089686727036', Decimal('14250')], ['4711162821322', Decimal('11550')], ['4710543613600', Decimal('7500')], ['6926265324955', Decimal('10260')], ['4711162821575', Decimal('4400')], ['8809027556390', Decimal('2200')], ['8801728105167', Decimal('4600')]], '050301': [['6921168593804', Decimal('43200')], ['8850025001023', Decimal('26100')], ['6921168593880', Decimal('23200')]], '100504': [['6940935200264', Decimal('29617.5')], ['6948004700400', Decimal('22057.5')], ['6921716523840', Decimal('8730')], ['4809010272010', Decimal('11925')], ['6953663024132', Decimal('4220')], ['8936050230178', Decimal('4500')], ['8858185000764', Decimal('7840')], ['6958247450567', Decimal('3810')], ['4897043062722', Decimal('4320')]], '100304': [['8801039280027', Decimal('16617.5')], ['6924160714017', Decimal('18950')]], '010102': [['6907992822723', Decimal('33110')], ['6918551804593', Decimal('20527.5')], ['6918551807884', Decimal('20266.66666666666666666666667')], ['6909493401025', Decimal('19500')], ['6909493632443', Decimal('18056.66666666666666666666667')], ['6918551812161', Decimal('27025')], ['6907868581587', Decimal('16433.33333333333333333333333')], ['6918551811423', Decimal('15376.66666666666666666666667')], ['6970377573077', Decimal('18995')], ['6909493200208', Decimal('12466.66666666666666666666667')], ['6909493400998', Decimal('11833.33333333333333333333333')], ['6909493401001', Decimal('11666.66666666666666666666667')], ['6909493200277', Decimal('11433.33333333333333333333333')], ['4710131176210', Decimal('16875')], ['6909493401018', Decimal('32000')], ['6909493401032', Decimal('10333.33333333333333333333333')], ['6909493400981', Decimal('8666.666666666666666666666667')], ['6970747541118', Decimal('8216.666666666666666666666667')], ['6907868581181', Decimal('7650')], ['6907868581389', Decimal('7650')], ['6909493200505', Decimal('10300')]], '070204': [['6902083880781', Decimal('15212.5')], ['6902083881559', Decimal('10167.5')]], '030201': [['6923644268497', Decimal('65020')], ['6907992512938', Decimal('51970')], ['6910442944289', Decimal('46507.5')]], '140101': [['6901845040968', Decimal('31350')], ['6947929617183', Decimal('24050')], ['6901845040951', Decimal('22070')], ['6947929617398', Decimal('19997.5')], ['6947929617176', Decimal('19835')], ['6901845045062', Decimal('18322.5')], ['6946050100106', Decimal('17995')], ['6919892633101', Decimal('17850')], ['8993175537469', Decimal('16200')], ['6901668054746', Decimal('14402.5')], ['084501814311', Decimal('18450')], ['6901845042986', Decimal('12387.5')], ['4714221811227', Decimal('16180')], ['084501446314', Decimal('12055')], ['6946050100120', Decimal('12035')], ['6901668004772', Decimal('15250')], ['6901180993387', Decimal('13353.33333333333333333333333')], ['6901668007773', Decimal('17280')], ['8410376017595', Decimal('8235')], ['6902227011897', Decimal('8145')], ['5410126716016', Decimal('10080')], ['4897050172513', Decimal('9990')], ['8000380005918', Decimal('9966.666666666666666666666667')], ['8000380140541', Decimal('9966.666666666666666666666667')], ['4897050172490', Decimal('9366.666666666666666666666667')], ['6902227011880', Decimal('6340')], ['6901668007780', Decimal('8400')], ['6928362106038', Decimal('11550')], ['6972020777177', Decimal('10740')], ['6901668053510', Decimal('5630')], ['6954434300356', Decimal('5200')], ['6901668053527', Decimal('4930')], ['4897081031346', Decimal('4826.666666666666666666666667')], ['8996001303634', Decimal('7200')], ['8801204007954', Decimal('7150')], ['9556995110237', Decimal('4666.666666666666666666666667')], ['8000380142460', Decimal('4600')], ['9556995110220', Decimal('4470')], ['6901668002457', Decimal('4066.666666666666666666666667')], ['8000380005963', Decimal('5750')]], '070103': [['6917536014088', Decimal('24166.66666666666666666666667')], ['6917536014026', Decimal('20106.66666666666666666666667')], ['6925303770556', Decimal('17290')]], '100301': [['6922307718164', Decimal('15460')], ['6922145800526', Decimal('19360')], ['6922307718188', Decimal('13122.5')], ['6932089610013', Decimal('10816.66666666666666666666667')], ['6947392700054', Decimal('10463.33333333333333333333333')], ['6922145800021', Decimal('28260')], ['6922219815692', Decimal('13675')], ['6953663017462', Decimal('12120')], ['6944978700842', Decimal('11895')], ['6952675329938', Decimal('6600')], ['6901757301805', Decimal('9550')], ['6921922401567', Decimal('5216.666666666666666666666667')], ['6924160715229', Decimal('7750')], ['6952675319915', Decimal('4800')], ['6944978703782', Decimal('12560')], ['6901757300020', Decimal('5600')], ['6901757401109', Decimal('3436.666666666666666666666667')]], '160202': [['20455088', Decimal('83336.66666666666666666666667')], ['6944697600799', Decimal('75000')], ['6944697600744', Decimal('74333.33333333333333333333333')], ['6944697601048', Decimal('60733.33333333333333333333333')]], '070403': [['6938888888615', Decimal('13050')], ['6938888887502', Decimal('12413.33333333333333333333333')]], '150305': [['6946455300668', Decimal('31280')]], '050101': [['6921168509256', Decimal('267600')], ['6922255451427', Decimal('174687.5')], ['6925303721695', Decimal('74342.5')], ['6901285991219', Decimal('127650')], ['6921168593002', Decimal('31360')], ['6922279400265', Decimal('22782.5')]], '140301': [['6930639260640', Decimal('23400')], ['6930639260602', Decimal('23002.5')], ['6930639260619', Decimal('19680')], ['6946954300169', Decimal('14895')], ['6923450603550', Decimal('16913.33333333333333333333333')], ['6930639260626', Decimal('10875')], ['6946954300206', Decimal('13160')], ['6922024730036', Decimal('18625')], ['6930639271387', Decimal('7060')], ['6946954300190', Decimal('14100')], ['6931925871472', Decimal('9096.666666666666666666666667')], ['6931925871458', Decimal('6355')], ['6930639260633', Decimal('7590')], ['6923450605332', Decimal('6930')], ['6931925828032', Decimal('10050')], ['6931925871465', Decimal('6613.333333333333333333333333')], ['4902750396111', Decimal('9900')], ['6923450605318', Decimal('6270')], ['6904700051406', Decimal('6056.666666666666666666666667')], ['6930639264587', Decimal('6033.333333333333333333333333')], ['69028571', Decimal('5940')], ['6931925828001', Decimal('8700')], ['6923450666326', Decimal('8340')], ['6933368300298', Decimal('5506.666666666666666666666667')], ['4005292123501', Decimal('7800')], ['6923450666357', Decimal('7645')], ['6933368300335', Decimal('5056.666666666666666666666667')], ['6931925872547', Decimal('7145')], ['6901424286206', Decimal('6075')], ['6901424335904', Decimal('4016.666666666666666666666667')], ['6904468020379', Decimal('6000')], ['4897022620516', Decimal('5670')]], '070401': [['6917878045139', Decimal('8750')], ['6901447006652', Decimal('6666.666666666666666666666667')], ['6901447006683', Decimal('4500')], ['6901447007390', Decimal('3416.666666666666666666666667')], ['8935024141342', Decimal('4845')]], '020101': [['6907992103051', Decimal('86813.33333333333333333333333')], ['6907992103419', Decimal('81166.66666666666666666666667')], ['6934665082047', Decimal('75183.33333333333333333333333')], ['6907992102764', Decimal('74750')], ['6922577727156', Decimal('65733.33333333333333333333333')], ['6922577727163', Decimal('65100')], ['6922577722717', Decimal('62933.33333333333333333333333')], ['6936357411111', Decimal('62100')], ['6971897495467', Decimal('46800')], ['6932571026278', Decimal('44483.33333333333333333333333')], ['6970011880844', Decimal('40300')], ['6970011880820', Decimal('39750')], ['6934665083808', Decimal('39650')], ['6924810810007', Decimal('38730')], ['6952522800115', Decimal('31100')], ['6907992105086', Decimal('27766.66666666666666666666667')], ['6927321719173', Decimal('27450')], ['6928494806455', Decimal('26316.66666666666666666666667')], ['6901209212215', Decimal('24933.33333333333333333333333')], ['6928494805250', Decimal('22360')], ['6932571026285', Decimal('21750')], ['6941704412666', Decimal('21000')], ['6971897494521', Decimal('30725')], ['6928494805267', Decimal('20460')], ['6922577726258', Decimal('18760')], ['6932571026391', Decimal('18603.33333333333333333333333')], ['6941704418460', Decimal('17613.33333333333333333333333')], ['6952522800047', Decimal('17300')], ['6970399920880', Decimal('16400')], ['6927321719128', Decimal('16200')], ['6970399920958', Decimal('16113.33333333333333333333333')]], '140203': [['6920907800944', Decimal('25265')]], '020103': [['6932571031111', Decimal('44200')], ['6932571031241', Decimal('32400')], ['6932571031289', Decimal('28600')], ['6940211889602', Decimal('35625')], ['6932571031999', Decimal('20400')], ['6950418707562', Decimal('26660')]], '070206': [['6927462202060', Decimal('39900')], ['6902890022961', Decimal('42380')], ['6927462217279', Decimal('16910')], ['6941760901043', Decimal('19693.33333333333333333333333')], ['6902890229421', Decimal('11500')], ['6927462216074', Decimal('8206.666666666666666666666667')], ['6951648500022', Decimal('23400')]], '140402': [['80050278', Decimal('32200')], ['80177609', Decimal('32016.66666666666666666666667')], ['4000417019004', Decimal('22400')], ['4000417224002', Decimal('15950')], ['4000417931009', Decimal('14970')], ['5060621760603', Decimal('9400')], ['5060621760580', Decimal('8773.333333333333333333333333')], ['4000417013002', Decimal('7840')], ['4000417020000', Decimal('7840')], ['4000417933003', Decimal('10835')], ['4607109843376', Decimal('6550')], ['5060621760597', Decimal('5013.333333333333333333333333')], ['4000417023001', Decimal('7425')], ['4605504515188', Decimal('7045')], ['77958112', Decimal('4243.333333333333333333333333')], ['77953537', Decimal('3926.666666666666666666666667')], ['80927181', Decimal('5245')], ['4000417044303', Decimal('4800')]], '070102': [['6920698400378', Decimal('45530')], ['6920698400477', Decimal('32947.5')], ['6925303714840', Decimal('27733.33333333333333333333333')], ['6925303714857', Decimal('27733.33333333333333333333333')], ['6937962100742', Decimal('18967.5')]], '100102': [['6924743919211', Decimal('57447.5')], ['6924743919235', Decimal('21705')], ['6924743919259', Decimal('27446.66666666666666666666667')], ['6924743919266', Decimal('17705')], ['6924743923515', Decimal('20413.33333333333333333333333')], ['6924743919273', Decimal('18633.33333333333333333333333')], ['6924743923430', Decimal('24430')], ['6924743918658', Decimal('10812.5')], ['6924743923447', Decimal('13800')], ['653314503486', Decimal('11050')]], '170201': [['6943290504442', Decimal('94800')], ['6943290501632', Decimal('82350')], ['6921253814111', Decimal('60425')], ['6952447801938', Decimal('49065')], ['6943290503919', Decimal('63000')], ['6952447801952', Decimal('46110')], ['6943290511921', Decimal('56920')], ['6952447801914', Decimal('41457.5')], ['6922330913222', Decimal('54933.33333333333333333333333')], ['20455903', Decimal('53703.33333333333333333333333')], ['6943290508693', Decimal('53000')], ['6932005204074', Decimal('52966.66666666666666666666667')], ['6922330913062', Decimal('52733.33333333333333333333333')], ['6922330913307', Decimal('44300')], ['20449889', Decimal('40823.33333333333333333333333')], ['6943290508686', Decimal('39726.66666666666666666666667')], ['6932005201820', Decimal('38566.66666666666666666666667')], ['6922330913246', Decimal('37000')], ['6932005203077', Decimal('35400')], ['20449933', Decimal('33710')], ['6922330913260', Decimal('30173.33333333333333333333333')], ['6932005205897', Decimal('29196.66666666666666666666667')]], '020203': [['6970605360103', Decimal('84100')], ['8801121761823', Decimal('70000')], ['6970605360295', Decimal('58050')], ['6970605360097', Decimal('49783.33333333333333333333333')], ['6932571061286', Decimal('42666.66666666666666666666667')], ['6932571061453', Decimal('41580')]], '090501': [['6901236373958', Decimal('12133.33333333333333333333333')], ['6901236390610', Decimal('10500')]], '050302': [['6941067725571', Decimal('148990')], ['6933888212781', Decimal('38860')], ['6921581540515', Decimal('50500')], ['6921581540102', Decimal('47000')], ['6934024502216', Decimal('22962.5')], ['6927216920059', Decimal('28226.66666666666666666666667')], ['6925303754112', Decimal('25050')], ['6921581540140', Decimal('33000')], ['6956416206281', Decimal('21560')], ['6956416205956', Decimal('14795')], ['6927216920011', Decimal('18173.33333333333333333333333')], ['6971949918210', Decimal('23660')], ['6971207392011', Decimal('20790')], ['6905069200030', Decimal('13300')], ['6925303757472', Decimal('13266.66666666666666666666667')], ['6933888213023', Decimal('11910')], ['6971949918272', Decimal('15600')], ['898999000022', Decimal('10350')]], '050703': [['6938866531939', Decimal('103600')], ['4891028164395', Decimal('44867.5')]], '020102': [['6921355220070', Decimal('94733.33333333333333333333333')], ['6921355220094', Decimal('74060')], ['6921355220681', Decimal('50703.33333333333333333333333')], ['6921355220087', Decimal('38000')], ['6923644286019', Decimal('37756.66666666666666666666667')], ['6921355222265', Decimal('32000')]], '050204': [['6921581596048', Decimal('142305')], ['6921168593569', Decimal('62612.5')], ['6970399920132', Decimal('65083.33333333333333333333333')], ['6970399920514', Decimal('54750')], ['6971480640168', Decimal('27813.33333333333333333333333')]], '140401': [['6914973600072', Decimal('35136.66666666666666666666667')], ['6914973604032', Decimal('28800')], ['6914973610507', Decimal('28433.33333333333333333333333')], ['6914973105379', Decimal('20137.5')], ['6914973610484', Decimal('25870')], ['6914973601017', Decimal('24000')], ['6914973600041', Decimal('23793.33333333333333333333333')], ['6914973610521', Decimal('20550')], ['6914973603394', Decimal('20133.33333333333333333333333')], ['6914973600010', Decimal('19643.33333333333333333333333')], ['6914973602908', Decimal('19250')], ['6914973607125', Decimal('17166.66666666666666666666667')], ['6914973600164', Decimal('12873.33333333333333333333333')], ['6914973606340', Decimal('16455')], ['6901496888025', Decimal('10660')], ['6914973105386', Decimal('9530')]], '020202': [['6971599569183', Decimal('23760')], ['6931023280268', Decimal('14233.33333333333333333333333')], ['6931023280275', Decimal('13766.66666666666666666666667')]], '100501': [['6936030000786', Decimal('13387.5')], ['6922300664796', Decimal('16943.33333333333333333333333')], ['6913189335655', Decimal('11037.5')], ['6922279401866', Decimal('14516.66666666666666666666667')], ['6936030000243', Decimal('7087.5')], ['6925523902218', Decimal('5216.666666666666666666666667')], ['6923976110136', Decimal('4773.333333333333333333333333')], ['6948049503288', Decimal('11760')], ['6936030000489', Decimal('5600')], ['6948049503264', Decimal('5265')]], '020201': [['6932571040168', Decimal('71800')], ['6932571040007', Decimal('55600')], ['6932571040106', Decimal('49600')], ['6932571040267', Decimal('38800')], ['6932571040069', Decimal('37400')], ['6932571040878', Decimal('34000')], ['6932571040854', Decimal('32866.66666666666666666666667')], ['6932571040861', Decimal('32583.33333333333333333333333')], ['6932571040915', Decimal('31340')], ['6921168593460', Decimal('24005')]], '090504': [['6922266439148', Decimal('9900')], ['6922266438417', Decimal('6600')], ['6901236301081', Decimal('7775')], ['6922279400838', Decimal('6500')]], '050203': [['6921168558049', Decimal('122250')], ['6921168593552', Decimal('53055')]], '100202': [['4710199085707', Decimal('36830')], ['8994834005213', Decimal('22355')], ['6931286060836', Decimal('21480')], ['4710199085509', Decimal('14362.5')], ['8886013505181', Decimal('50440')], ['6931286060843', Decimal('14786.66666666666666666666667')], ['6935729400012', Decimal('13333.33333333333333333333333')]], '050501': [['6921168500956', Decimal('52520')], ['6902538004045', Decimal('49980')], ['6921168559244', Decimal('44985')], ['6902538005141', Decimal('38420')], ['6921168550098', Decimal('36195')], ['6921581540089', Decimal('30480')], ['6932529211107', Decimal('22397.5')], ['6921168550128', Decimal('20666.66666666666666666666667')], ['6972215667535', Decimal('19040')]], '721005': [['6920130971916', Decimal('5633.333333333333333333333333')], ['6920130971947', Decimal('4116.666666666666666666666667')], ['6970376393119', Decimal('11200')], ['6920130971930', Decimal('4550')], ['6970376393157', Decimal('9100')], ['6920130971923', Decimal('3900')]], '140302': [['69025143', Decimal('71190')], ['6923450656181', Decimal('45523.33333333333333333333333')], ['6923450601549', Decimal('15225')], ['6923450605288', Decimal('9000')], ['6924513908179', Decimal('6666.666666666666666666666667')], ['6924513908155', Decimal('5416.666666666666666666666667')], ['6924513908551', Decimal('5333.333333333333333333333333')], ['6923450658079', Decimal('4950')], ['69019388', Decimal('6280')], ['6923450658048', Decimal('4033.333333333333333333333333')], ['6923450665732', Decimal('9730')], ['6923450660195', Decimal('3200')], ['6924513908131', Decimal('2916.666666666666666666666667')], ['6924513908216', Decimal('4375')], ['69027086', Decimal('3850')], ['6924513908537', Decimal('3000')], ['6923450665701', Decimal('2780')], ['6923450662090', Decimal('2500')], ['6923450662106', Decimal('2500')]], '050502': [['6920202888883', Decimal('82000')], ['6920202866737', Decimal('46400')], ['4897036692202', Decimal('30793.33333333333333333333333')]], '140303': [['6940471601228', Decimal('8200')], ['6940471601211', Decimal('7200')], ['6926475201008', Decimal('9450')], ['6902934990362', Decimal('5400')], ['6926475200995', Decimal('6750')], ['4711931033130', Decimal('5840')], ['8809420331280', Decimal('4385')]], '100101': [['6924743915763', Decimal('21995')], ['6920907809909', Decimal('15795')], ['6924743915770', Decimal('14100')], ['6920907809862', Decimal('9247.5')], ['6924743923676', Decimal('11906.66666666666666666666667')], ['6924743923669', Decimal('9400')], ['6924743923652', Decimal('9086.666666666666666666666667')], ['6958652300013', Decimal('8115')], ['6958652300037', Decimal('7025')]], '090503': [['6901236374382', Decimal('60250')], ['6970343422767', Decimal('41400')]], '140102': [['4710801131419', Decimal('15600')], ['6930570700038', Decimal('10152.5')], ['6923250611243', Decimal('9562.5')], ['6930570700014', Decimal('9475')], ['8410376009392', Decimal('11116.66666666666666666666667')], ['6902227012085', Decimal('10506.66666666666666666666667')], ['6901668200013', Decimal('6553.333333333333333333333333')]], '050602': [['6917878030623', Decimal('285490')], ['6917878056197', Decimal('238006.6666666666666666666667')], ['6917878054780', Decimal('182800')], ['6921581540270', Decimal('84157.5')]], '020401': [['6922711403960', Decimal('43420')], ['6922711403977', Decimal('43195')], ['6902890234487', Decimal('18850')], ['6926640520767', Decimal('25116.66666666666666666666667')], ['6953158500585', Decimal('59340')], ['6926640510188', Decimal('19616.66666666666666666666667')], ['8801066310520', Decimal('20400')], ['6970725075512', Decimal('31670')], ['6926640521092', Decimal('15200')]], '100404': [['6944683368696', Decimal('30677.5')], ['6959479300316', Decimal('29700')], ['6959479300323', Decimal('23283.33333333333333333333333')], ['6947120968916', Decimal('11040')], ['6922504601146', Decimal('8505')], ['6920771612667', Decimal('8050')], ['8809022201660', Decimal('14850')], ['4897043061213', Decimal('13160')], ['6922504601436', Decimal('3313.333333333333333333333333')], ['6956511907885', Decimal('9080')]], '721002': [['6970376393522', Decimal('7000')]], '030101': [['6923644266066', Decimal('90250')], ['6923644269579', Decimal('89030')], ['6920584471017', Decimal('100133.3333333333333333333333')], ['6921355240030', Decimal('51235')], ['6901209258022', Decimal('67133.33333333333333333333333')], ['6921355240023', Decimal('45300')], ['6907992513607', Decimal('43050')], ['6921355240245', Decimal('57190')], ['6907992500942', Decimal('17833.33333333333333333333333')], ['93639125', Decimal('15250')]], '050205': [['4891028705949', Decimal('62400')], ['6938888889803', Decimal('59506.66666666666666666666667')], ['4891028164456', Decimal('50800')]], '140202': [['6924706700023', Decimal('38080')], ['6924706790154', Decimal('23030')], ['6942285400073', Decimal('14133.33333333333333333333333')], ['6924706700085', Decimal('19880')], ['6920731799605', Decimal('12223.33333333333333333333333')], ['6924706700047', Decimal('17690')], ['6942285400059', Decimal('11733.33333333333333333333333')], ['6919892111708', Decimal('8512.5')], ['6946079399710', Decimal('9920')], ['6950955901201', Decimal('14350')], ['6920731701103', Decimal('6720')]], '050402': [['6954767423579', Decimal('92625')], ['6954767412573', Decimal('64200')], ['6954767410586', Decimal('64125')], ['6906907401022', Decimal('34200')], ['6906907907012', Decimal('31875')], ['6954767460116', Decimal('30200')], ['6954767430836', Decimal('29000')], ['6954767410708', Decimal('28416.66666666666666666666667')], ['6954767432076', Decimal('14860')], ['6954767430461', Decimal('18150')], ['6954767425979', Decimal('15466.66666666666666666666667')]], '100403': [], '140204': [['6950955901225', Decimal('26775')], ['4713077250105', Decimal('17166.66666666666666666666667')], ['4711931012173', Decimal('12765')], ['6956320700066', Decimal('25380')], ['6958620700319', Decimal('11782.5')], ['8936063740039', Decimal('15050')], ['6950955901232', Decimal('22225')], ['4711931012166', Decimal('9417.5')], ['4711931012203', Decimal('6970')], ['6908314016943', Decimal('13440')], ['6908314017032', Decimal('13160')], ['6971533421300', Decimal('6826.666666666666666666666667')], ['6971533421331', Decimal('5600')], ['6928590207606', Decimal('4696.666666666666666666666667')], ['6911988014832', Decimal('4446.666666666666666666666667')], ['4894375015860', Decimal('6425')]], '721403': [['6921299762070', Decimal('11280')], ['6921299762063', Decimal('9840')]], '140304': [['6937451831249', Decimal('10150')], ['6937451811418', Decimal('4530')], ['4990327910037', Decimal('5560')]], '030301': [['6907992513645', Decimal('23682.5')], ['6907992512570', Decimal('16740')], ['6907992512853', Decimal('14425')]], '720702': [['6926410320214', Decimal('12000')], ['6971807590305', Decimal('8493.333333333333333333333333')], ['6926410338165', Decimal('21760')], ['6917878024929', Decimal('10000')], ['6970514610870', Decimal('19600')], ['6917878024967', Decimal('9200')], ['6971807590169', Decimal('8850')], ['6971807590039', Decimal('8820')]], '100201': [['6926265313010', Decimal('20355')], ['6957666001114', Decimal('9075')], ['6924743913721', Decimal('17050')], ['6923567880288', Decimal('10176.66666666666666666666667')], ['6924743913738', Decimal('13200')], ['6957666001503', Decimal('6505')], ['6923567880271', Decimal('12255')], ['8858702410823', Decimal('6300')], ['4710022036524', Decimal('5700')], ['6923775942327', Decimal('9600')]], '070406': [['6939947700169', Decimal('8400')]], '090301': [['6903244370950', Decimal('44586.66666666666666666666667')], ['6934660516714', Decimal('43413.33333333333333333333333')], ['6934660511917', Decimal('35600')], ['6934660559216', Decimal('34100')], ['6903244370974', Decimal('49000')], ['6934660528618', Decimal('31800')], ['6923589462400', Decimal('28750')], ['6922731800770', Decimal('27000')], ['6922731800695', Decimal('23200')], ['6903148137406', Decimal('23040')], ['6934660552118', Decimal('18360')], ['6923589466156', Decimal('17000')], ['4901301254283', Decimal('42900')], ['6903148258064', Decimal('36100')], ['6922731800121', Decimal('11116.66666666666666666666667')]], '050206': [['4891599338393', Decimal('18612.5')]], '080203': [['6937558000456', Decimal('19800')], ['6916999215216', Decimal('8970')], ['6923251810294', Decimal('16500')], ['4710367996712', Decimal('7800')], ['6943970200879', Decimal('9600')], ['6937436199005', Decimal('9500')], ['6937436197940', Decimal('9450')], ['6954272790036', Decimal('7500')], ['6926292511311', Decimal('5500')], ['6937436195212', Decimal('4950')], ['6933643302962', Decimal('4200')], ['6957332012482', Decimal('2560')], ['6957332016329', Decimal('1680')]], '100303': [['6935284412918', Decimal('31270')], ['6935284415650', Decimal('17470')], ['6952675337735', Decimal('9047.5')], ['6953567023330', Decimal('17265')], ['6935284415667', Decimal('8622.5')], ['6953567023194', Decimal('16125')], ['6918768000221', Decimal('14400')], ['6937623400204', Decimal('9560')]], '050102': [['6921168520015', Decimal('220700')]], '160201': [['6943290507283', Decimal('112400')], ['6943290510412', Decimal('105370')], ['20453237', Decimal('105266.6666666666666666666667')], ['6944697601161', Decimal('100780')], ['6943290507542', Decimal('90200')], ['6944697601154', Decimal('88520')], ['6970182591877', Decimal('87870')]], '090505': [['6970551560084', Decimal('14083.33333333333333333333333')], ['6952180316928', Decimal('35100')]], '100401': [['6924187828544', Decimal('28100')], ['6924187851160', Decimal('10400')], ['6922133606086', Decimal('5905')], ['6956511924967', Decimal('3090')]], '050704': [['6902083886455', Decimal('51166.66666666666666666666667')], ['6916196423834', Decimal('31933.33333333333333333333333')], ['6906791582555', Decimal('23796.66666666666666666666667')]], '090502': [['6901236341308', Decimal('103566.6666666666666666666667')], ['6932873820215', Decimal('16950')]], '020302': [['6932005203916', Decimal('36733.33333333333333333333333')], ['6932005204524', Decimal('31250')], ['6932005205149', Decimal('30083.33333333333333333333333')], ['6932005200632', Decimal('28343.33333333333333333333333')], ['6932005205484', Decimal('23666.66666666666666666666667')], ['6932005206719', Decimal('29640')], ['6932005205798', Decimal('19626.66666666666666666666667')], ['6932005206887', Decimal('18216.66666666666666666666667')], ['6932005206610', Decimal('18555')], ['6932005207068', Decimal('11870')]], '050202': [['6925303754952', Decimal('42400')], ['6921317905014', Decimal('34575')], ['6925303721398', Decimal('16195')], ['6921317944150', Decimal('19060')], ['6956416206090', Decimal('15946.66666666666666666666667')]], '170203': [['6970717330896', Decimal('74510')], ['6922330911174', Decimal('47116.66666666666666666666667')], ['20449940', Decimal('40906.66666666666666666666667')], ['20455910', Decimal('20746.66666666666666666666667')]], '080204': [['6901826888039', Decimal('21913.33333333333333333333333')], ['6901826888145', Decimal('26410')], ['6940735451446', Decimal('5000')], ['6940735451743', Decimal('4600')], ['6940735449917', Decimal('6450')], ['6901826001179', Decimal('10500')]], '090202': [['4895125934486', Decimal('3625')], ['6951348710912', Decimal('2350')], ['6970009908901', Decimal('1900')], ['6970009909090', Decimal('1500')]], '050201': [['6925303721367', Decimal('29275')], ['6921317905168', Decimal('23250')], ['4710154014254', Decimal('20843.33333333333333333333333')], ['4710154014247', Decimal('17910')], ['6901568020117', Decimal('14560')]], '160103': [['6954463410521', Decimal('36425')], ['6970182591853', Decimal('21675')], ['6959659500727', Decimal('13766.66666666666666666666667')], ['6970182590658', Decimal('11040')]], '050702': [['6925303730574', Decimal('99377.5')], ['4710094109676', Decimal('63880')], ['6925303783273', Decimal('82500')], ['4710094106118', Decimal('42200')]], '080401': [['6923251811031', Decimal('33600')], ['6912003003077', Decimal('22750')], ['6912003336144', Decimal('4900')]], '170202': [['6943290508426', Decimal('87333.33333333333333333333333')], ['6943290503674', Decimal('86666.66666666666666666666667')], ['6943290510634', Decimal('81276.66666666666666666666667')], ['6943290503698', Decimal('61416.66666666666666666666667')], ['6943290501793', Decimal('54600')], ['6922330913314', Decimal('33873.33333333333333333333333')]], '160401': [['6937131901026', Decimal('27650')], ['6937131900739', Decimal('17425')], ['6937131901910', Decimal('14800')]], '720703': [['6917878045566', Decimal('9450')], ['6917878045115', Decimal('5850')], ['8886392200769', Decimal('3383.333333333333333333333333')]], '140103': [['8888077102092', Decimal('4305')], ['4897092210143', Decimal('2640')], ['4897092210136', Decimal('3260')], ['6901668053916', Decimal('4960')], ['8888077108032', Decimal('2460')], ['6954432711086', Decimal('1725')], ['8888077110004', Decimal('1610')]], '720101': [['6907992810263', Decimal('19535')]], '410102': [], '721003': [['6925678100552', Decimal('12060')], ['6935284413960', Decimal('9730')], ['6935284411218', Decimal('8260')], ['6935490202228', Decimal('8000')], ['6935490202266', Decimal('7600')], ['6935284471076', Decimal('7490')], ['6935284413977', Decimal('6930')], ['6935490202211', Decimal('6000')], ['6944978703645', Decimal('11500')], ['6935284470031', Decimal('5460')], ['6925678100613', Decimal('5220')], ['6935284416152', Decimal('5180')], ['6925678102969', Decimal('3400')], ['6935284411768', Decimal('5040')], ['6931710030176', Decimal('4480')], ['6925678104635', Decimal('2900')], ['6925678104741', Decimal('2833.333333333333333333333333')], ['6925678100453', Decimal('3960')], ['6925678102686', Decimal('2500')]], '100502': [['6954627200050', Decimal('65960')], ['6920242100280', Decimal('11790')], ['6947954100872', Decimal('7082.5')], ['6947954100889', Decimal('6750')]], '050104': [['6970399920415', Decimal('144850')], ['6970399920057', Decimal('57945')], ['6954767460147', Decimal('47380')]], '160101': [['6970182590122', Decimal('95426.66666666666666666666667')], ['6970182590344', Decimal('91193.33333333333333333333333')], ['6970182590153', Decimal('88696.66666666666666666666667')], ['6970182590603', Decimal('85000')], ['20445645', Decimal('81740')], ['6970182590146', Decimal('81130')], ['6970182591747', Decimal('62210')]], '050401': [['6954767417684', Decimal('48415')], ['6972020770031', Decimal('37400')], ['6949843700149', Decimal('37800')], ['6972020770161', Decimal('11040')], ['6972156910011', Decimal('11146.66666666666666666666667')]], '070207': [['6971807590145', Decimal('19350')], ['6971284200001', Decimal('17000')], ['6957427661519', Decimal('15675')], ['6948343203259', Decimal('10300')], ['6937350205127', Decimal('22950')], ['6971284200087', Decimal('10500')], ['6926410330954', Decimal('7125')], ['6970514610887', Decimal('13720')]], '160402': [], '720502': [], '170102': [['6922330911402', Decimal('23640')]], '720909': [['6922266440106', Decimal('57720')], ['6922266446238', Decimal('43700')], ['6914068024486', Decimal('37000')], ['6914068019529', Decimal('9600')], ['6914068015361', Decimal('17100')], ['6914068020235', Decimal('10640')]], '030401': [['6941368621275', Decimal('7590')]], '160102': [['20447281', Decimal('58196.66666666666666666666667')]], '170101': [['6922330911358', Decimal('64970')], ['6922330911235', Decimal('40050')]], '050207': [], '721004': [['6971639280023', Decimal('2266.666666666666666666666667')], ['6920753635325', Decimal('5600')]], '050601': [['6921168594733', Decimal('19613.33333333333333333333333')]], '080301': [['6947503718022', Decimal('400')], ['6947503702410', Decimal('1050')], ['6947503716172', Decimal('700')], ['6947503798024', Decimal('480')]], '100302': [['6931792200030', Decimal('20240')], ['6925843402559', Decimal('6326.666666666666666666666667')], ['6958621306848', Decimal('4340')], ['6920382723202', Decimal('3150')]], '150301': [['20348076', Decimal('4500')]], '150106': [], '050103': [], '720201': [['6921355231274', Decimal('28875')], ['6921355231359', Decimal('27450')], ['6921355231472', Decimal('26100')], ['6921355231526', Decimal('25500')]], '721401': [['8993175540629', Decimal('21525')], ['8993175537445', Decimal('14525')], ['8850987358913', Decimal('7095')]], '100402': [['6925843404225', Decimal('27983.33333333333333333333333')], ['6922621129684', Decimal('26950')], ['6914913000214', Decimal('5415')]], '040102': [['6948960100078', Decimal('64600')], ['6900228381155', Decimal('39650')], ['6900228381124', Decimal('26600')], ['6921336821258', Decimal('22540')], ['4251402303022', Decimal('20580')], ['4016762825511', Decimal('16740')], ['4016762825528', Decimal('16480')], ['4016762822046', Decimal('14880')], ['6948960107695', Decimal('13950')]], '070203': [['6932583203155', Decimal('6450')]], '150201': [['20325893', Decimal('1250')], ['20325862', Decimal('2450')], ['20431396', Decimal('1050')], ['20407926', Decimal('1520')], ['20325909', Decimal('1500')], ['20454708', Decimal('1050')], ['20441203', Decimal('900')]], '060207': [['6915993300539', Decimal('2800')], ['6970227520015', Decimal('2100')]], '090102': [['6915324888385', Decimal('18000')], ['6955818204130', Decimal('14400')], ['8436097093519', Decimal('7000')], ['4909978139056', Decimal('6500')], ['6920999701730', Decimal('2935')]], '721402': [], '040401': [['6935145303034', Decimal('25200')], ['6935145303058', Decimal('42700')], ['6935145315020', Decimal('34800')], ['6935145315013', Decimal('32400')]], '150303': [['20410247', Decimal('5460')], ['6937977103097', Decimal('4400')], ['20433031', Decimal('3960')], ['20433024', Decimal('3000')]], '070202': [['6971860060395', Decimal('19000')], ['6971860060418', Decimal('7800')], ['6971860060920', Decimal('7600')], ['6949656160055', Decimal('12160')]], '020402': [['6970081712922', Decimal('13270')], ['6970725072351', Decimal('12150')], ['6970725074713', Decimal('10500')], ['6935036482633', Decimal('2475')], ['6919498504089', Decimal('4720')]], '020204': [], '720806': [['6970529180405', Decimal('4200')]], '070402': [['6970578345053', Decimal('5446.666666666666666666666667')], ['6970578345015', Decimal('5256.666666666666666666666667')], ['6971283060606', Decimal('9480')]], '720202': [['6948029419059', Decimal('14300')]], '070201': [['6971415832309', Decimal('26700')], ['6971885310307', Decimal('6810')]], '070408': [['6953949205026', Decimal('9520')], ['6944683369358', Decimal('2905')], ['6953949205064', Decimal('4720')]], '090105': [['6925911523452', Decimal('6300')], ['6925911500224', Decimal('4470')], ['6956741711115', Decimal('2670')]], '020403': [['6935036483630', Decimal('45000')], ['6935036483616', Decimal('43125')]], '070404': [], '020104': [['6971897497539', Decimal('10200')], ['6927321719081', Decimal('9900')], ['6934665091117', Decimal('4275')]], '040403': [['8801048921003', Decimal('53700')]], '720907': [], '080202': [['6902022135255', Decimal('30450')], ['6902022135514', Decimal('24450')], ['6902022134333', Decimal('23550')], ['6902088700558', Decimal('5780')], ['6921669800005', Decimal('4500')]], '090106': [['6903148082102', Decimal('33250')], ['6937746210872', Decimal('8400')], ['6903148144541', Decimal('7800')], ['6926799691462', Decimal('6400')]], '060205': [['6910160313350', Decimal('2700')]], '150101': [['20379865', Decimal('900')], ['20342869', Decimal('300')], ['20248925', Decimal('300')], ['20348441', Decimal('300')], ['20342838', Decimal('250')]], '080201': [['6901463980073', Decimal('2700')]], '090101': [['4891338011310', Decimal('61000')], ['6901070600173', Decimal('38400')], ['6901070600005', Decimal('31900')], ['4901616213210', Decimal('30600')], ['6903148247839', Decimal('28800')], ['6970128544547', Decimal('26400')], ['4901616007536', Decimal('20400')], ['6933179230043', Decimal('16800')], ['6902088605235', Decimal('14300')], ['6920354814051', Decimal('13800')], ['6920354817113', Decimal('12500')], ['6903148054215', Decimal('11050')], ['6907376821021', Decimal('9800')], ['6903148247587', Decimal('9730')], ['4901221800102', Decimal('8700')], ['6920354812552', Decimal('7500')]], '720904': [['6903148091432', Decimal('31800')]], '140201': [['6942542312866', Decimal('5650')]], '020301': [['6922477400227', Decimal('11300')], ['6922477401569', Decimal('8200')], ['6922477400722', Decimal('7960')]], '090104': [['6902088113723', Decimal('48000')], ['6903148044971', Decimal('45500')], ['6936000900061', Decimal('14700')], ['6903148091425', Decimal('12500')], ['6926799691776', Decimal('11700')]], '710701': [], '060203': [['6900958666652', Decimal('3300')], ['6920010300010', Decimal('1500')], ['6932850200122', Decimal('1100')]], '080101': [], '060204': [], '080104': [['6932662803252', Decimal('6000')], ['6933063027100', Decimal('5600')]], '720803': [['6937671628056', Decimal('1520')], ['6928947481543', Decimal('1000')], ['6957332016114', Decimal('500')]], '040101': [['6948960110145', Decimal('28750')], ['6948960107671', Decimal('20400')], ['5411681400310', Decimal('14400')], ['6948960109323', Decimal('10800')]], '720902': [['6915324847696', Decimal('8400')]], '040301': [['9310297005147', Decimal('17000')]], '720906': [['6902088311112', Decimal('25200')], ['6902088311174', Decimal('15300')]], '090204': [['6900068003033', Decimal('6000')]], '080103': [['6971342340335', Decimal('930')]], '090401': [['6923146107089', Decimal('2100')]], '720302': [], '120401': [], '070302': [], '050403': [['6954767413877', Decimal('22400')]], '720802': [['6903148078884', Decimal('700')]], '070101': [], '720801': [], '070104': [], '070301': [], '720908': [], '140404': [['8000500005026', Decimal('20800')]], '020404': [], '080105': [], '720901': [], '090602': [['6902088425741', Decimal('6580')], ['815601026072', Decimal('5800')]], '010103': [['6930692700473', Decimal('32400')], ['6909493200574', Decimal('18900')]], '070407': [['6947120969128', Decimal('8400')]], '010101': [['6920858211561', Decimal('11800')], ['6971057800018', Decimal('9600')], ['8801104900010', Decimal('8500')], ['8801062482801', Decimal('7900')]], '040502': [], '080302': [], '040503': [['6947523252506', Decimal('11640')], ['6971616511324', Decimal('11400')], ['6947523252513', Decimal('10600')], ['6943642007577', Decimal('3980')]], '720804': []}

