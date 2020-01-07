
"""
日常换品
"""
import decimal
import json
from  decimal import Decimal
import datetime,pymysql
import os,django,math,copy
from goods.third_tools.dingtalk import send_message
from goods.choose_goods.choose_goods_version_01.item_cf import ItemBasedCF

import main.import_django_settings
from django.db import connections
from django.db import close_old_connections

class DailyChangeGoods:
    """
    目前只是非日配的日常换品逻辑
    """

    def __init__(self,shop_id,template_shop_ids,batch_id,uc_shopid,topn_ratio=0.6,days=28):
        self.category_goods_list = []    # 结构品
        self.template_shop_ids = template_shop_ids.split(',')
        self.shop_id = shop_id
        self.uc_shopid = uc_shopid
        self.batch_id = batch_id
        self.topn_ratio = Decimal(topn_ratio)  # 取累计psd金额的百分之多少作为畅销品
        self.ab_ratio = 0.8     # 某三级分类下累计前多少是a+b类
        self.days = days     # 取数周期
        self.all_third_category_mch_dict = []      # 三级分类的列表
        self.first_category_goods_count_dict = {}     # 一级分类选品预估的数量
        self.supplier_id_list = []     # 供应商id
        self.debug = True
        self.can_order_mch_code_dict = {}    # 可订货的7位得mch_goods_code的字典，value为配送类型，k为店内码,从saas查询
        self.can_order_list = []    # 可订货的7位得mch_goods_code的列表
        self.all_goods_len = 0    # 本店台账已有len
        self.taizhang_goods_mch_code_list = []
        self.third_category_mch_dict = {}  # 本店有的，陈列三级分类的字典，k为mch，v为mch字符串，逗号隔开
        self.all_rank_list = []    # 本店所有关联品的分值，里边是元组，第一个为mch，第二个为总的关联分值

        # self.not_move_goods = []  # 没有变动的品
        # self.must_up_goods = []  # 必须上架的品
        # self.optional_up_goods = []  # 可选上架的品
        # self.must_out_goods = []  # 必须下架的品
        # self.optional_out_goods = []  # 可选下架的品


        # conn = pymysql.connect('123.103.16.19', 'readonly', password='fxiSHEhui2018@)@)', database='dmstore',charset="utf8", port=3300, use_unicode=True)
        # self.cursor = conn.cursor()
        close_old_connections()
        self.cursor = connections['dmstore'].cursor()
        self.cursor_ucenter = connections['ucenter'].cursor()

    def __del__(self):
        self.cursor.close()
        self.cursor_ucenter.close()

    def get_shop_sales_data(self, shop_id):
        """
        获取该店有销量的商品的psd金额的排序列表
        :param shop_id:
        :return:
        """
        now = datetime.datetime.now()
        now_date = now.strftime('%Y-%m-%d %H:%M:%S')
        week_ago = (now - datetime.timedelta(days=self.days)).strftime('%Y-%m-%d %H:%M:%S')
        # 这个三级分类没用
        sql = "select sum(p.amount),g.upc,g.saas_third_catid,g.neighbor_goods_id,g.price,p.name,sum(p.number) from dmstore.payment_detail as p left join dmstore.goods as g on p.goods_id=g.id where p.create_time > '{}' and p.create_time < '{}' and p.shop_id = {} group by g.upc order by sum(p.amount) desc;"
        self.cursor.execute(sql.format(week_ago, now_date, shop_id))
        results = self.cursor.fetchall()
        return results

    def get_mch_psd_data(self, mch, shop_ids):
        """
        获取某些门店的这些品按照psd金额排序的列表数据
        :param third_category: 三级分类
        :param shop_ids: 门店的ids
        :return:
        """
        # 按照陈列分类
        now = datetime.datetime.now()
        now_date = now.strftime('%Y-%m-%d %H:%M:%S')
        week_ago = (now - datetime.timedelta(days=self.days)).strftime('%Y-%m-%d %H:%M:%S')
        if type(shop_ids) is list and len(shop_ids) > 0:  # 多个门店
            # print('list,third_category',shop_ids,third_category)
            shop_ids = ",".join(shop_ids)
            sql = "select sum(p.amount),g.upc,g.third_cate_id,g.neighbor_goods_id,g.price,p.name,COUNT(DISTINCT p.shop_id) from dmstore.payment_detail as p left join dmstore.goods as g on p.goods_id=g.id where p.create_time > '{}' and p.create_time < '{}' and p.shop_id in ({}) and g.neighbor_goods_id in ({}) group by g.neighbor_goods_id order by sum(p.amount) desc;"
        elif type(shop_ids) is str or type(shop_ids) is int:  # 单个门店
            # print('str',shop_ids,type(shop_ids))
            sql = "select sum(p.amount),g.upc,g.third_cate_id,g.neighbor_goods_id,g.price,p.name from dmstore.payment_detail as p left join dmstore.goods as g on p.goods_id=g.id where p.create_time > '{}' and p.create_time < '{}' and p.shop_id = {} and g.neighbor_goods_id in ({}) group by g.neighbor_goods_id order by sum(p.amount) desc;"
        else:
            print('none', shop_ids, type(shop_ids))
            return []
        self.cursor.execute(sql.format(week_ago, now_date, shop_ids, mch))
        results = self.cursor.fetchall()

        # print(results)
        # print(len(results))
        return results

    def get_all_third_category_mch_dict(self):
        """
        获取所有陈列三级分类的code的字典，k为分类，v为mch字符串，逗号隔开
        :return:
        """
        all_third_category_mch_dict = {}
        # 注意：and c.display_third_cat_id>0 类型是字符串
        sql = "select c.display_third_cat_id,GROUP_CONCAT(a.supplier_goods_code) from uc_supplier_goods a LEFT JOIN uc_merchant_goods c on a.supplier_goods_code=c.mch_goods_code where a.supplier_id in ({}) and a.order_status = 1 and c.width > 0 and c.height > 0 and c.depth > 0 and c.mch_goods_code is not NULL and c.mch_goods_code !='' and c.display_third_cat_id>0 GROUP BY c.display_third_cat_id"
        try:
            self.cursor_ucenter.execute(sql.format(','.join(self.supplier_id_list)))
            all_data = self.cursor_ucenter.fetchall()
            for data in all_data:
                all_third_category_mch_dict[data[0]] = data[1]
            return all_third_category_mch_dict
        except:
            return dict()

    def get_taizhang_goods(self):
        """
        获取当前台账的商品列表
        :return:
        """
        # uc_conn = connections['ucenter']
        # self.cursor_ucenter = uc_conn.cursor()
        # 获取当前的台账
        select_sql_02 = "select t.id, t.shelf_id, td.batch_no,td.display_shelf_info, td.display_goods_info,t.mch_id from sf_shop_taizhang st, sf_taizhang t, sf_taizhang_display td where st.taizhang_id=t.id and td.taizhang_id=t.id and td.status=2 and td.approval_status=1 and st.shop_id = {}".format(self.uc_shopid)
        try:
            self.cursor_ucenter.execute(select_sql_02)
            all_data = self.cursor_ucenter.fetchall()
            taizhang_data_list = []
            for data in all_data:
                for goods_info in json.loads(data[4]):
                    for layer in goods_info['layerArray']:
                        for goods in layer:
                            # goods_upc = goods['goods_upc']
                            taizhang_data_list.append(goods)
            # print('台账：',taizhang_data_list)
            # print('台账mch：',[i['mch_goods_code'] for i in taizhang_data_list])
            self.taizhang_goods_mch_code_list = list(set([i['mch_goods_code'] for i in taizhang_data_list]))  # 去重
            print('台账mch去重：', self.taizhang_goods_mch_code_list)
            return taizhang_data_list, all_data[0][5]
        except Exception as e:
            print('pos店号是{},查询该店台账报错,{}'.format(self.shop_id, e))
            return [],None

    def get_third_category_mch_dict(self, mch_code_list):
        """
        获取陈列三级分类的字典，k为mch，v为mch字符串，逗号隔开
        :param mch_code:
        :return:
        """
        third_category_mch_dict = {}
        # 注意：and c.display_third_cat_id>0 类型是字符串
        sql = "select c.display_third_cat_id,GROUP_CONCAT(a.supplier_goods_code) from uc_supplier_goods a LEFT JOIN uc_merchant_goods c on a.supplier_goods_code=c.mch_goods_code where a.supplier_id in ({}) and a.order_status = 1 and c.width > 0 and c.height > 0 and c.depth > 0 and c.mch_goods_code in ({}) and c.display_third_cat_id>0 GROUP BY c.display_third_cat_id"
        try:
            # print(sql.format(','.join(self.supplier_id_list),",".join(mch_code_list)))
            self.cursor_ucenter.execute(sql.format(','.join(self.supplier_id_list),",".join(mch_code_list)))
            all_data = self.cursor_ucenter.fetchall()
            for data in all_data:
                third_category_mch_dict[data[0]] = data[1]
            return third_category_mch_dict
        except Exception as e:
            print('pos店号是{},查询该店三级分类报错,{}'.format(self.shop_id, e))
            return dict()


    def calculate_quick_seller(self):
        """
        获取该组多个门店的畅销品和结构品（目前是每三级分类下psd金额top1）
        同组门店中每个三级分类下： 4周的psd金额或psd /（门店数*在售天数）的累计前60-70%
        目前门店数是根据取数周期内的有销售的门店进行统计的，因为该品在该店是否上架的数据不准
        在售天数则默认一直在售
        :param topn:
        :return:
        """

        self.all_third_category_mch_dict = self.get_all_third_category_mch_dict()
        print('可订货的所有三级分类len', len(self.all_third_category_mch_dict))
        category_dict = {}    # k为三级分类，v为分类下的商品列表
        for third_category,mch in self.all_third_category_mch_dict.items():      # 遍历每个三级分类
            all_shop_data = self.get_mch_psd_data(mch, self.template_shop_ids)
            if not all_shop_data:    # 说明这个分类下的品都没有销量
                continue

            third_category_has_psd_list = list()
            for data in all_shop_data:     # psd金额除以商店数
                # try:
                    # template_shop_ids,upc,code,predict_sales_amount,mch_goods_code,predict_sales_num,name
                    # temp_list = [','.join(self.template_shop_ids), data[1], data[2], data[0]/(upc_time[data[1]]*self.days), data[3],data[0]/(upc_time[data[1]]*self.days*data[4]), data[5]]
                    temp_list = [','.join(self.template_shop_ids), data[1], third_category, data[0]/(data[6]*self.days), data[3],data[0]/(data[6]*self.days*data[4]), data[5]]

                    third_category_has_psd_list.append(temp_list)
                # except:
                #     print('11111')
            category_dict[third_category] = third_category_has_psd_list

        quick_seller_list = []
        structure_goods_list = []
        other_goods_list = []     # 有销量，但非结构非畅销
        for category, goods_list in category_dict.items():
            if goods_list == []:
                break
            goods_list.sort(key=lambda x: x[3], reverse=True)  # 基于psd金额排序
            # print('goods_list',goods_list)


            # --以下是把第一个加进去，算的是结构品
            structure_goods_list.append(goods_list[0])

            # --以下是求累计
            amount = 0  # 分类下psd金额的总额
            for goods in goods_list:
                amount += goods[3]
            temp_amount = 0
            for index,goods in enumerate(goods_list):  # 将累计前占比60%psd金额的商品选出来，遇到边界少选策略
                # quick_seller_list.append(goods[0])   # 遇到边界多选策略
                temp_amount += goods[3]
                if temp_amount > amount * self.topn_ratio:
                    break
                if index != 0:          # 现在结构品是从三级分类top1选的，这是为了不重复
                    quick_seller_list.append(goods)   # 遇到边界少选策略

            for goods in goods_list:
                if goods not in structure_goods_list and goods not in quick_seller_list:
                    other_goods_list.append(goods)

        structure_goods_list.sort(key=lambda x: x[3], reverse=True)  # 基于psd金额排序
        quick_seller_list.sort(key=lambda x: x[3], reverse=True)  # 基于psd金额排序
        other_goods_list.sort(key=lambda x: x[3], reverse=True)  # 基于psd金额排序
        return structure_goods_list, quick_seller_list,other_goods_list

    def get_can_order_dict(self):
        """
        获取可订货的7位得mch_goods_code的字典，value为配送类型，k为店内码,从saas查询
        :return:
        """

        self.cursor.execute("SELECT erp_shop_id from erp_shop_related WHERE shop_id ={} AND erp_shop_type=1;".format(self.shop_id))
        try:
            erp_shop_id = self.cursor.fetchone()[0]
            print("erp_shop_id",erp_shop_id)
        except Exception as e:
            print('pos店号是{},erp_shop_id获取失败:{}'.format(self.shop_id,e))
            send_message('pos店号是{},erp_shop_id获取失败:{}'.format(self.shop_id,e))
            return []

        # 获取商品的 可定 配送类型
        can_order_list = []  # 可订货列表
        delivery_type_dict = {}    # 店内码是key，配送类型是value
        try:
            # cursor_ucenter.execute("select id from uc_supplier where supplier_code in ({})".format(','.join(supplier_code)))
            # (supplier_id,) = cursor_ucenter.fetchone()
            # self.supplier_id = supplier_id

            self.cursor_ucenter.execute("SELECT supplier_id from uc_warehouse_supplier_shop WHERE warehouse_id={}".format(erp_shop_id))
            all_supplier_id_data = self.cursor_ucenter.fetchall()
            for supplier_data in all_supplier_id_data:
                self.supplier_id_list.append(str(supplier_data[0]))
            print("supplier_id_list",self.supplier_id_list)

            if not self.supplier_id_list:
                send_message("pos店号是{},查询supplier_id为空，sql为'SELECT supplier_id from uc_warehouse_supplier_shop WHERE warehouse_id={}'".format(self.shop_id,erp_shop_id))
            self.cursor_ucenter.execute(
                # "select supplier_goods_code,delivery_type from uc_supplier_goods where supplier_id = {} and order_status = 1 ".format(supplier_id))
                # "select a.supplier_goods_code,b.delivery_attr from uc_supplier_goods a LEFT JOIN uc_supplier_delivery b on a.delivery_type=b.delivery_code where a.supplier_id = {} and order_status = 1".format(supplier_id))
                # 有尺寸数据
                "select DISTINCT a.supplier_goods_code,b.delivery_attr,c.display_second_cat_id from uc_supplier_goods a LEFT JOIN uc_supplier_delivery b on a.delivery_type=b.delivery_code LEFT JOIN uc_merchant_goods c on a.supplier_goods_code=c.supplier_goods_code where a.supplier_id in ({}) and order_status = 1 and c.width > 0 and c.height > 0 and c.depth > 0 and c.display_third_cat_id > 0".format(','.join(self.supplier_id_list)))
            all_data = self.cursor_ucenter.fetchall()
            # print("可订货数据：",all_data)
            for data in all_data:
                can_order_list.append(data[0])
                if data[2] == "104":    #  巧克力分类 ,按照非日配逻辑来处理
                    delivery_type_dict[data[0]] = 2
                    continue
                delivery_type_dict[data[0]] = data[1]
        except Exception as e:
            print('pos店号是{},查询是否可订货和配送类型失败,{}'.format(self.shop_id,e))
            send_message('pos店号是{},查询是否可订货和配送类型失败,{}'.format(self.shop_id,e))
        if not can_order_list:
            send_message('pos店号是{},查询是否可订货数据为空'.format(self.shop_id))
        return can_order_list,delivery_type_dict

    def calculate_not_move_goods(self):
        """
        计算保护品列表
        :return:
        """
        shop_protect_goods_mch_code_list = []
        for category,mch in self.third_category_mch_dict.items():
            category_protect_goods_list = []    # 保护品
            # 新品期的品
            new_goods = []   # TODO

            # select sum(p.amount),g.upc,g.corp_classify_code,g.neighbor_goods_id,g.price,p.name from dmstore.payment_detail as p left join dmstore.goods as g on p.goods_id=g.id where p.create_time > '{}' and p.create_time < '{}' and p.shop_id = {} and g.corp_classify_code={} group by g.upc order by sum(p.amount) desc;"
            category_goods_tuple = self.get_mch_psd_data(mch, self.shop_id)     # 获取该分类下有销量的数据
            # template_shop_ids,upc,code,predict_sales_amount,mch_goods_code,predict_sales_num,name,is_structure,is_qiuck_seller,is_relation,ranking

            ab_quick_seller_list = []
            if category_goods_tuple:
                # --以下是求累计
                amount = 0  # 分类下psd金额的总额
                for goods in category_goods_tuple:
                    amount += goods[0]
                temp_amount = 0
                for index, goods in enumerate(category_goods_tuple):  # 将累计前占比80%psd金额的商品选出来
                    if str(goods[3]) in self.taizhang_goods_mch_code_list:
                        # print('yes0')
                        ab_quick_seller_list.append(str(goods[3]))   # 遇到边界多选策略,neighbor_goods_id
                    temp_amount += goods[0]
                    if temp_amount > float(amount) * self.ab_ratio:
                    # if temp_amount > float(amount) * 1:
                    #     print('不可能！！')
                        break
                        # ab_quick_seller_list.append(goods)  # 遇到边界少选策略,neighbor_goods_id
                category_protect_goods_list.extend(ab_quick_seller_list)
            else:
                if not new_goods:
                    all_category_goods_tuple = self.get_mch_psd_data(mch, self.template_shop_ids)  # 获取同组门店该分类下有销量的数据
                    if all_category_goods_tuple:
                        for goods in all_category_goods_tuple:
                            if str(goods[3]) in self.taizhang_goods_mch_code_list:
                                # print('yes1')
                                category_protect_goods_list.append(str(goods[3]))
                                break
                    if not category_protect_goods_list:
                        profit_max = self.profit_max(mch)
                        if profit_max:
                            # print('yes2')
                            category_protect_goods_list.append(profit_max)
                        else:
                            print('{}保留毛利最大那个,但是没找到'.format(category))                # 保留毛利最大那个

            shop_protect_goods_mch_code_list.extend(category_protect_goods_list)
        return shop_protect_goods_mch_code_list

    def profit_max(self,mch):
        """
        分类下毛利最大那个商品得mch_code
        :param category:
        :return:
        """
        sql = "SELECT neighbor_goods_id,price-purchase_price as p from goods where neighbor_goods_id in ({}) ORDER BY p desc"
        self.cursor.execute(sql.format(mch))
        all_data = self.cursor.fetchall()
        for data in all_data:
            if str(data[0]) in self.taizhang_goods_mch_code_list:
                return str(data[0])
        return None

    def must_up_add_ranking(self,must_up_goods):
        """
        添加ranking的值,
        策略1-结构品，为必备品，选出商品后，排名分值赋予psd金额*100000
        策略2-畅销品，为必备品，选出商品后，排名分值赋予psd金额*10000
        策略2-关联品，为必备品，选出商品后，排名分值赋予psd金额*1000
        之后加入了其他关联品等策略后，排名分值根据策略再去设定
        :param must_up_goods:
        :return:
        """
        for goods in must_up_goods:
            if goods[-1] == 0:   # 结构品
                goods.append(goods[3]*100000)
            elif goods[-1] == 1:   # 畅销品
                goods.append(goods[3]*10000)
            elif goods[-1] == 2:   # 关联品
                goods.append(goods[3]*1000)
            else:
                # raise Exception("必上品列表出现异常数据！")
                print("必上品列表出现异常数据！")
        return must_up_goods

    def calculate_relation_goods(self,must_up_goods,optional_up_goods):
        """
        计算关联品
        :param must_up_goods: 已然算出的畅销品和结构品
        :param optional_up_goods: 可选上，不含0销量的
        :return:
        """
        print("must_up_goods长度",len(must_up_goods))
        print("optional_up_goods长度",len(optional_up_goods))
        print(optional_up_goods)
        # candidate_mch_goods_list = [goods[4] for goods in candidate_up_goods_list]
        must_up_mch_goods_list = [str(goods[4]) for goods in must_up_goods]
        optional_up_mch_goods_dict = {}
        for goods in optional_up_goods:
            # print(goods)
            optional_up_mch_goods_dict[str(goods[4])] = goods

        # print('哈哈')
        # print(optional_up_mch_goods_dict)
        # print(self.can_order_mch_code_dict)
        # print(self.taizhang_goods_mch_code_list)
        # print(must_up_mch_goods_list)
        itemCF = ItemBasedCF(self.shop_id,100,2.4,self.can_order_list)   # 协同过滤
        rank_list,self.all_rank_list = itemCF.recommend_02()   #列表形式，里边是元组，第一个为mch，第二个为总的关联分值

        for mch_goods, score in rank_list:
            if mch_goods not in self.taizhang_goods_mch_code_list and mch_goods not in must_up_mch_goods_list:
                # print(mch_goods)
                # print(type(mch_goods))
                if str(mch_goods) in self.can_order_mch_code_dict:
                    delivery_type = self.can_order_mch_code_dict[str(mch_goods)]
                    if delivery_type != 2:     # 把非日配的挑出来
                        continue
                    # if delivery_type == 2 and str(mch_goods) in optional_up_mch_goods_dict:
                    #     print("从可选上架里挑选出一个关联品00000！")

                    must_up_mch_goods_list.append(mch_goods)
                    if str(mch_goods) in optional_up_mch_goods_dict:
                        print("从可选上架里挑选出一个关联品,,mch为{}".format(mch_goods))
                        temp_data = optional_up_mch_goods_dict[mch_goods]
                        temp_data[-1] = 2
                        temp_data[-2] = score
                        temp_data[-3] = 1
                        # temp_data.apeend(score)
                        must_up_goods.append(optional_up_mch_goods_dict[mch_goods])
                    else:
                        # print("123456789")
                        sql = "SELECT upc,goods_name from uc_merchant_goods WHERE mch_goods_code='{}' and upc > 0"
                        self.cursor_ucenter.execute(sql.format(mch_goods))
                        psd_data = self.get_mch_psd_data(mch_goods,self.template_shop_ids)
                        print('psd_data',psd_data)
                        if psd_data:
                            psd_amount = psd_data[0][0]/(self.days*psd_data[0][6])
                        else:
                            psd_amount = 0
                        try:
                            d = self.cursor_ucenter.fetchone()
                            must_up_goods.append([','.join(self.template_shop_ids), d[0], None, psd_amount, mch_goods, None, d[1], 0, 0, 1,score, 2])
                        except:
                            print("mch为{}的商品获取upc和name失败".format(mch_goods))

        # 把可选上架里转移到必上的品，给导过来
        optional_up_goods = []
        for mch in optional_up_mch_goods_dict:
            if not mch in must_up_mch_goods_list:
                optional_up_goods.append(optional_up_mch_goods_dict[mch])

        print("must_up_goods长度2", len(must_up_goods))
        print("optional_up_goods长度2", len(optional_up_goods))
        return must_up_goods,optional_up_goods


    def recommend_03(self):

        not_move_goods = []   # 没有变动的品
        must_up_goods = []  # 必须上架的品
        optional_up_goods = []  # 可选上架的品
        must_out_goods = []  # 必须下架的品
        optional_out_goods = []  # 可选下架的品
        temp_optional_out_goods = []  # 临时可选下架
        third_category_mch_dict = []   # 本店已有三级分类


        # 0、列表可订货
        self.can_order_list,self.can_order_mch_code_dict = self.get_can_order_dict()
        print('可订货len：', len(self.can_order_mch_code_dict))

        #   1.1、获取本店有销量的商品
        sales_data = self.get_shop_sales_data(self.shop_id)
        sales_goods_mch_code_dict = {}
        print('本店有销量的品len', len(sales_data))
        # have_sale_category_code = []
        for s in sales_data:
            sales_goods_mch_code_dict[str(s[3])] = s
            # have_sale_category_code.append(str(s[2]))
        # print("有销量的三级分类的code",len(set(have_sale_category_code)),sorted(list(set(have_sale_category_code))))

        #   1.2、获取当前台账的商品
        taizhang_goods, mch_code = self.get_taizhang_goods()  # 获取当前台账的商品
        self.taizhang_goods_mch_code_list = list(set([i['mch_goods_code'] for i in taizhang_goods]))  # 去重
        self.all_goods_len = len(self.taizhang_goods_mch_code_list)
        print('去重台账goods', self.all_goods_len)

        # 1.3 获取本店的保护品，即不动的品
        if self.all_goods_len == 0:
            self.third_category_mch_dict = {}
        else:
            self.third_category_mch_dict = self.get_third_category_mch_dict(self.taizhang_goods_mch_code_list)

        print('本店已有三级分类', len(self.third_category_mch_dict), self.third_category_mch_dict)

        not_move_goods, optional_out_goods = self.calculate_this_shop_old_goods_data(taizhang_goods,mch_code,sales_goods_mch_code_dict)   #得出下架品、不动品和可选下架品

        self.calculate_this_shop_new_goods_data(mch_code,not_move_goods,optional_out_goods)



    def calculate_this_shop_old_goods_data(self,taizhang_goods,mch_code,sales_goods_mch_code_dict):
        # 得出下架品、不动品和可选下架品
        not_move_goods = []  # 没有变动的品
        must_out_goods = []  # 必须下架的品
        optional_out_goods = []  # 可选下架的品
        temp_optional_out_goods = []  # 临时可选下架






        not_move_goods_mch_code_list = self.calculate_not_move_goods()

        print("本店保护品len",len(not_move_goods_mch_code_list),len(set(not_move_goods_mch_code_list)))


        # 1.4、遍历货架,得出下架品、不动品和可选下架品

        for data in taizhang_goods:
            if not data['mch_goods_code'] in self.can_order_mch_code_dict:    # 不可订货即必须下架
                # template_shop_ids,upc,code,predict_sales_amount,mch_goods_code,predict_sales_num,name,is_structure,is_qiuck_seller,is_relation,relation_score,which_strategy,delivery_type,ranking
                # must_out_goods.append((None, data['goods_upc'], None, None, data['mch_goods_code'], None, data['name'], 0, 0, 0, None, self.can_order_mch_code_dict[str(data['mch_goods_code'])], None))
                must_out_goods.append((None, data['goods_upc'], None, None, data['mch_goods_code'], None, data['name'], 0, 0, 0,None, None, None))

            elif data['mch_goods_code'] in not_move_goods_mch_code_list:    # 保护品即为不动的品
                # print('有销量即为不动的品')
                # not_move_goods.append((None, data['goods_upc'],None, None,data['mch_goods_code'], None, data['name'], 0, 0, 0, None, self.can_order_mch_code_dict[str(data['mch_goods_code'])], None))
                not_move_goods.append((None, data['goods_upc'],None, None,data['mch_goods_code'], None, data['name'], 0, 0, 0, None, None, None))
            else:    # 剩下的是可选下架的
                if data['mch_goods_code'] in sales_goods_mch_code_dict.keys():    # 有销量的进行排序
                    # print('有销量即为不动的品')
                    # tem_list = [None, data['goods_upc'],None, sales_goods_mch_code_dict[data['mch_goods_code']][0],data['mch_goods_code'], None, data['name'], 0, 0, 0, self.can_order_mch_code_dict[str(data['mch_goods_code'])], None]
                    tem_list = [None, data['goods_upc'],None, sales_goods_mch_code_dict[data['mch_goods_code']][0],data['mch_goods_code'], None, data['name'], 0, 0, 0,None, None]
                    if not tem_list in temp_optional_out_goods:
                        temp_optional_out_goods.append(tem_list)
                else:       # 剩下没销量的为可选下架品的第一优先级
                    # optional_out_goods.append((None, data['goods_upc'], None, None, data['mch_goods_code'], None, data['name'], 0, 0, 0, None, self.can_order_mch_code_dict[str(data['mch_goods_code'])], 10000))  # FIXME 分类code为空
                    optional_out_goods.append((None, data['goods_upc'], None, None, data['mch_goods_code'], None, data['name'], 0, 0, 0,None, None, 10000))  # FIXME 分类code为空

        optional_out_goods = list(set(optional_out_goods))
        temp_optional_out_goods.sort(key=lambda x: x[3], reverse=True)  # 基于psd金额排序
        for index,goods in enumerate(temp_optional_out_goods):
            goods.append(index+1)
            optional_out_goods.append(tuple(goods))

        not_move_goods = list(set(not_move_goods))
        must_out_goods = list(set(must_out_goods))
        optional_out_goods = list(set(optional_out_goods))

        print('保护品',len(not_move_goods))
        print('必须下架',len(must_out_goods))
        print('可选下架',len(optional_out_goods))

        self.save_data(not_move_goods, 0, mch_code)
        self.save_data(must_out_goods, 2, mch_code)
        self.save_data(optional_out_goods, 4, mch_code)

        return not_move_goods,optional_out_goods

    def calculate_this_shop_new_goods_data(self,mch_code,not_move_goods,optional_out_goods):

        must_up_goods = []  # 必须上架的品
        optional_up_goods = []  # 可选上架的品

        # 2、计算新增品
        # must_up_goods_len = math.ceil(self.all_goods_len * 0.03)
        must_up_goods_len = 10000


        all_structure_goods_list, all_quick_seller_list,other_goods_list = self.calculate_quick_seller()  # 获取同组门店的结构品和畅销品
        print("模板店有销量的结构品len",len(all_structure_goods_list))
        print("模板店畅销品len",len(all_quick_seller_list))


        if self.debug:
            print('================')
            structure_goods_list_test = []  # 该店没有该三级分类的结构品列表，并且可订货
            for data in all_structure_goods_list:
                structure_goods_list_test.append(data[4])

            quick_seller_list_test = []  # 该店没有的畅销品，并且可订货
            for data in all_quick_seller_list:
                quick_seller_list_test.append(data[4])
            print(structure_goods_list_test)
            print(quick_seller_list_test)
            print('================')

        candidate_up_goods_list = []     # 上架候选列表，依次是本店没有的结构品、畅销品

        # 该店没有该三级分类的结构品列表，并且可订货
        for data in all_structure_goods_list:
            if not data[2] in self.third_category_mch_dict and str(data[4]) in self.can_order_mch_code_dict and not str(data[4]) in self.taizhang_goods_mch_code_list:
                # print(data[2],self.third_category_mch_dict)
                # data.extend([1,1,0,0, self.can_order_mch_code_dict[str(data[4])]])       # is_structure,is_qiuck_seller,is_relation,which_strategy,delivery_type
                data.extend([1,1,0,None,0])       # is_structure,is_qiuck_seller,is_relation,relation_score,which_strategy,delivery_type
                candidate_up_goods_list.append(data)

        print("本店没有分类的结构品len",len(candidate_up_goods_list))

        # 该店有该三级分类,并且可订货,并且本店本来是没有的
        for data in all_structure_goods_list:
            if data[2] in self.third_category_mch_dict and str(data[4]) in self.can_order_mch_code_dict and not str(data[4]) in self.taizhang_goods_mch_code_list:
                print('???')
                # data.extend([0, 1, 0, 1, self.can_order_mch_code_dict[str(data[4])]])  # is_structure,is_qiuck_seller,is_relation,which_strategy,delivery_type
                data.extend([0, 1, 0,None, 1])  # is_structure,is_qiuck_seller,is_relation,which_strategy,delivery_type
                candidate_up_goods_list.append(data)

        # 该店没有的畅销品，并且可订货
        for data in all_quick_seller_list:
            if not str(data[4]) in self.taizhang_goods_mch_code_list and str(data[4]) in self.can_order_mch_code_dict:
                # data.extend([0, 1, 0, 1, self.can_order_mch_code_dict[str(data[4])]])      # is_structure,is_qiuck_seller,is_relation,which_strategy,delivery_type
                data.extend([0, 1, 0,None, 1])      # is_structure,is_qiuck_seller,is_relation,which_strategy,delivery_type
                candidate_up_goods_list.append(data)

        # candidate_up_goods_list = self.calculate_relation_goods(candidate_up_goods_list)

        # 非结构非畅销，有销量的，该店没有的品，并且可订货
        for data in other_goods_list:
            if not str(data[4]) in self.taizhang_goods_mch_code_list and str(data[4]) in self.can_order_mch_code_dict:
                # data.extend([0, 0, 0, None, self.can_order_mch_code_dict[str(data[4])]])  # is_structure,is_qiuck_seller,is_relation,which_strategy,delivery_type
                data.extend([0, 0, 0,None, None])  # is_structure,is_qiuck_seller,is_relation,which_strategy,delivery_type
                candidate_up_goods_list.append(data)




        # 非日配选出来
        temp_number = 0    # 上架品选到candidate_up_goods_list候选集的第几个啦
        for goods in candidate_up_goods_list:

            if len(must_up_goods) == must_up_goods_len:
                break
            try:
                if str(goods[4]) in self.can_order_mch_code_dict:
                    delivery_type = self.can_order_mch_code_dict[str(goods[4])]
                    if delivery_type == 2:
                        if goods[-1] is not None:    # 目前，畅销品和结构品都为必上品
                            must_up_goods.append(goods)
                    else:
                        # print("怎么回事？")
                        optional_up_goods.append(goods)
            except:
                print("怎么回事啊啊啊啊啊啊啊啊啊？")
                optional_up_goods.append(goods)

            temp_number += 1
        optional_up_goods += candidate_up_goods_list[temp_number:]

        # 添加必上的关联品
        must_up_goods, optional_up_goods = self.calculate_relation_goods(must_up_goods,optional_up_goods)
        # print('must_up_goods000',must_up_goods)


        must_up_goods = self.must_up_add_ranking(must_up_goods)  # 添加ranking的值
        # print('must_up_goods', must_up_goods)

        optional_up_goods.sort(key=lambda x: x[3], reverse=False)  # 基于psd金额排序
        for index,goods in enumerate(optional_up_goods):    # 添加ranking的值
            goods.append(index+1)

        must_up_goods = [tuple(goods) for goods in must_up_goods]
        optional_up_goods = [tuple(goods) for goods in optional_up_goods]

        # print('must_up_goods', must_up_goods)
        # print()
        # print('optional_up_goods', optional_up_goods)


        # 3、保存至数据库

        self.save_data(must_up_goods, 1,mch_code)
        # self.save_data(optional_up_goods, 3,mch_code)


        # 把可订货的都存到可选上架
        all_data = not_move_goods + optional_out_goods + must_up_goods + optional_up_goods
        all_data_mch = []
        optional_up_goods_order = []    # 在模板店没销量的可订货的
        for data in all_data:
            all_data_mch.append(str(data[4]))
        for mch in self.can_order_mch_code_dict:
            if not mch in all_data_mch:
                # optional_up_goods_order.append((None, None, None, None, mch, None, None, 0, 0, 0, None,self.can_order_mch_code_dict[mch], 0))
                optional_up_goods_order.append((None, None, None, None, mch, None, None, 0, 0, 0,None, None, 0))
        optional_up_goods.extend(optional_up_goods_order)


        self.save_data(optional_up_goods, 3, mch_code)



    def save_data(self,data,goods_role,mch_code):
        """
        保存选品的数据
        :param data:
        :param goods_role: 商品角色
        :param mch_code:
        :return:
        """

        tuple_data = tuple(data)

        conn = connections['default']
        cursor = conn.cursor()

        # insert_sql_01 = "insert into goods_firstgoodsselection(shopid,template_shop_ids,upc,code,predict_sales_amount,mch_code,mch_goods_code,predict_sales_num,name,batch_id,uc_shopid) values (%s,%s,%s,%s,%s,2,%s,%s,%s,'{}','{}')"
        insert_sql_02 = "insert into goods_goodsselectionhistory(shopid,template_shop_ids,upc,code,predict_sales_amount,mch_code,mch_goods_code,predict_sales_num,name,batch_id,uc_shopid,goods_role,is_structure,is_qiuck_seller,is_relation,relation_score,which_strategy,ranking,handle_goods_role) values ({},%s,%s,%s,%s,{},%s,%s,%s,'{}','{}',{},%s,%s,%s,%s,%s,%s,{})"
        delete_sql_02 = "delete from goods_goodsselectionhistory where uc_shopid={} and batch_id='{}' and goods_role={}"
        select_sql = "select batch_id from goods_goodsselectionhistory where uc_shopid={} and batch_id='{}' and goods_role={}"
        # try:
        print('batch_id', self.batch_id, type(self.batch_id))
        print('len',len(tuple_data))
        cursor.execute(select_sql.format(self.uc_shopid, self.batch_id,goods_role).replace('=None', ' is NULL'))  # 查询有该批次，没有的话，插入，有的话，先删再插入
        # print('history_batch_id', history_batch_id,type(history_batch_id))
        if cursor.fetchone():
            cursor.execute(delete_sql_02.format(self.uc_shopid, self.batch_id,goods_role).replace('=None', ' is NULL'))
            print("删掉{}该批次之前的数据".format(self.batch_id))
        print('开始入库')
        print(tuple_data[:5])
        cursor.executemany(insert_sql_02.format(self.shop_id,mch_code,self.batch_id, self.uc_shopid,goods_role,goods_role).replace('None', 'NULL'), tuple_data[:])

        # except:
        #     # 如果发生错误则回滚
        #     conn.rollback()
        #     cursor.close()
        #     conn.close()
        #     print('error')

        if goods_role == 3:
            for data in self.all_rank_list:
                try:
                    cursor.execute("UPDATE goods_goodsselectionhistory SET relation_score={} WHERE mch_goods_code='{}' and batch_id='{}'".format(data[1],data[0],self.batch_id))
                except Exception as e:
                    print("mch为{}，保存relation_score时，报错：{}".format(data[0],e))
        conn.commit()
        conn.close()
        print('ok')



def start_choose_goods(batch_id,uc_shop_id,pos_shopid):
    # f = DailyChangeGoods(pos_shopid, "88,3156,3238",batch_id,uc_shop_id)
    f = DailyChangeGoods(pos_shopid, "1284,3955,3779,1925,4076,1924,3598",batch_id,uc_shop_id)
    f.recommend_03()




if __name__ == '__main__':

    # f = DailyChangeGoods(1284, "1284,3955,3779,1925,4076,1924,3598,223,4004",'lishu_test_010',806)
    # f = DailyChangeGoods(1284, "223",'lishu_test_010',806)
    f = DailyChangeGoods(88, "223",'lishu_test_01',806)
    f.recommend_03()
    # start_choose_goods('lishu_test_01',806,88)
    # f.get_taizhang_goods()
    # print(len(f.get_can_order_dict()))






