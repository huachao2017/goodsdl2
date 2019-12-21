
"""
日常换品
"""
import decimal
import json
from  decimal import Decimal
import datetime,pymysql
import os,django,math,copy
from goods.third_tools.dingtalk import send_message

import main.import_django_settings
from django.db import connections

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
        self.third_category_list = []      # 三级分类的列表
        self.first_category_goods_count_dict = {}     # 一级分类选品预估的数量
        self.debug = True

        # conn = pymysql.connect('123.103.16.19', 'readonly', password='fxiSHEhui2018@)@)', database='dmstore',charset="utf8", port=3300, use_unicode=True)
        # self.cursor = conn.cursor()
        self.cursor = connections['dmstore'].cursor()

    def get_shop_sales_data(self, shop_id):
        """
        获取该店有销量的商品的psd金额的排序列表
        :param shop_id:
        :return:
        """
        now = datetime.datetime.now()
        now_date = now.strftime('%Y-%m-%d %H:%M:%S')
        week_ago = (now - datetime.timedelta(days=self.days)).strftime('%Y-%m-%d %H:%M:%S')
        sql = "select sum(p.amount),g.upc,g.third_cate_id,g.neighbor_goods_id,g.price,p.name from dmstore.payment_detail as p left join dmstore.goods as g on p.goods_id=g.id where p.create_time > '{}' and p.create_time < '{}' and p.shop_id = {} group by g.upc order by sum(p.amount) desc;"
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
        if type(shop_ids) is list and len(shop_ids) > 0:       # 多个门店
            # print('list,third_category',shop_ids,third_category)
            shop_ids = ",".join(shop_ids)
            sql = "select sum(p.amount),g.upc,g.third_cate_id,g.neighbor_goods_id,g.price,p.name,COUNT(DISTINCT p.shop_id) from dmstore.payment_detail as p left join dmstore.goods as g on p.goods_id=g.id where p.create_time > '{}' and p.create_time < '{}' and p.shop_id in ({}) and g.third_cate_id={} group by g.upc order by sum(p.amount) desc;"
        elif type(shop_ids) is str or type(shop_ids) is int:     # 单个门店
            # print('str',shop_ids,type(shop_ids))
            sql = "select sum(p.amount),g.upc,g.third_cate_id,g.neighbor_goods_id,g.price,p.name from dmstore.payment_detail as p left join dmstore.goods as g on p.goods_id=g.id where p.create_time > '{}' and p.create_time < '{}' and p.shop_id = {} and g.third_cate_id={} group by g.upc order by sum(p.amount) desc;"
        else:
            print('none', shop_ids,type(shop_ids))
            return []
        self.cursor.execute(sql.format(week_ago, now_date, shop_ids,third_category))
        results = self.cursor.fetchall()
        # cursor.close()

        # print(results)
        # print(len(results))
        return results

    def get_third_category_list(self):
        """
        获取一段取数周期内，所有模板店的有销量的品的所有三级分类的code的列表
        :return:
        """
        now = datetime.datetime.now()
        now_date = now.strftime('%Y-%m-%d %H:%M:%S')
        week_ago = (now - datetime.timedelta(days=self.days)).strftime('%Y-%m-%d %H:%M:%S')
        sql = "select distinct g.third_cate_id from dmstore.payment_detail as p left join dmstore.goods as g on p.goods_id=g.id where p.create_time > '{}' and p.create_time < '{}' and p.shop_id in ({});"
        template_shop_ids = ",".join(self.template_shop_ids)
        self.cursor.execute(sql.format(week_ago, now_date, template_shop_ids))
        results = self.cursor.fetchall()
        print('get_third_category_list',results)
        results_list = []
        for i in results:
            try:
                if type(i[0]) is int:
                    results_list.append(i[0])
            except:
                continue
        return results_list

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
        # uc_cursor.execute('select id from uc_shop where mch_shop_code = {}'.format(self.shop_id))
        # self.uc_shopid = uc_cursor.fetchone()[0]
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

    def get_third_category(self,mch_code_list):
        """
        获取本店三级分类的code的列表
        :param mch_code:
        :return:
        """
        sql = "SELECT DISTINCT(third_cate_id) from goods WHERE neighbor_goods_id in ({})"
        self.cursor.execute(sql.format(",".join(mch_code_list)))
        all_data = self.cursor.fetchall()
        result = []
        for data in all_data:
            if type(data[0]) is int:
                if not data[0] is None:
                    result.append(data[0])
        return result

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
        print('self.third_category_list',len(self.third_category_list))
        category_dict = {}    # k为三级分类，v为分类下的商品列表
        for third_category in self.third_category_list[:]:      # 遍历每个三级分类
            all_shop_data = self.get_third_category_data(third_category, self.template_shop_ids)
            # # 以下14行代码主要是统计upc取数周期内在各店出现的次数
            # all_one_shop_data_list = []
            # for template_shop_id in self.template_shop_ids:
            #     one_shop_data = self.get_third_category_data(third_category, template_shop_id)
            #     all_one_shop_data_list.append(one_shop_data)
            # all_upc = [i[1] for i in all_shop_data]   # FIXME
            # upc_time = {}           # upc在各店出现的次数，k为upc，v为次数
            # for upc in all_upc:
            #     temp_num = 0
            #     for one_shop_data in all_one_shop_data_list:
            #         for data in one_shop_data:
            #             if upc == data[1]: # FIXME
            #                 temp_num += 1
            #     if temp_num > 0:    # 将出现大于N次的都加进去
            #         upc_time[upc] = temp_num


            # print('upc_time',upc_time)
            third_category_quick_seller_list = list()
            for data in all_shop_data:     # psd金额除以商店数
                # try:
                    # template_shop_ids,upc,code,predict_sales_amount,mch_goods_code,predict_sales_num,name
                    # temp_list = [','.join(self.template_shop_ids), data[1], data[2], data[0]/(upc_time[data[1]]*self.days), data[3],data[0]/(upc_time[data[1]]*self.days*data[4]), data[5]]
                    temp_list = [','.join(self.template_shop_ids), data[1], data[2], data[0]/(data[6]*self.days), data[3],data[0]/(data[6]*self.days*data[4]), data[5]]

                    third_category_quick_seller_list.append(temp_list)
                # except:
                #     print('11111')
            category_dict[third_category] = third_category_quick_seller_list

        quick_seller_list = []
        structure_goods_list = []
        for category, goods_list in category_dict.items():
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
        try:
            erp_shop_id = self.cursor.fetchone()[0]
        except:
            print('erp_shop_id获取失败！')
            return []

        ms_conn = connections['erp']     # 魔兽系统库ms_sku_relation
        ms_cursor = ms_conn.cursor()
        sql_02 = "SELECT p.model_id,p.party_code from ls_prod p, ms_sku_relation ms WHERE ms.prod_id=p.prod_id AND  p.shop_id='{}' AND ms.status=1;"
        ms_cursor.execute(sql_02.format(erp_shop_id))
        results = ms_cursor.fetchall()
        try:
            return [i[1] for i in results]
        except:
            return []

    def calculate_not_move_goods(self,category_03_list):
        """
        计算保护品列表
        :return:
        """
        shop_protect_goods_mch_code_list = []
        for category in category_03_list:
            category_protect_goods_list = []    # 保护品
            # 新品期的品
            new_goods = []   # TODO



            # select sum(p.amount),g.upc,g.corp_classify_code,g.neighbor_goods_id,g.price,p.name from dmstore.payment_detail as p left join dmstore.goods as g on p.goods_id=g.id where p.create_time > '{}' and p.create_time < '{}' and p.shop_id = {} and g.corp_classify_code={} group by g.upc order by sum(p.amount) desc;"
            category_goods_tuple = self.get_third_category_data(category,self.shop_id)     # 获取该分类下有销量的数据
            # template_shop_ids,upc,code,predict_sales_amount,mch_goods_code,predict_sales_num,name,is_structure,is_qiuck_seller,is_relation,ranking

            ab_quick_seller_list = []
            if category_goods_tuple:
                # --以下是求累计
                amount = 0  # 分类下psd金额的总额
                for goods in category_goods_tuple:
                    amount += goods[0]
                temp_amount = 0
                for index, goods in enumerate(category_goods_tuple):  # 将累计前占比80%psd金额的商品选出来
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
                    all_category_goods_tuple = self.get_third_category_data(category, self.shop_id)  # 获取同组门店该分类下有销量的数据
                    if all_category_goods_tuple:
                        category_protect_goods_list.append(all_category_goods_tuple[0][3])
                    else:
                        pass                # 保留毛利最大那个

            shop_protect_goods_mch_code_list.extend(category_protect_goods_list)
        return shop_protect_goods_mch_code_list


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
        temp_optional_out_goods = []  # 临时可选下架

        category_03_list = []   # 本店已有三级分类的code列表



        #   1.1、获取本店有销量的商品
        sales_data = self.get_shop_sales_data(self.shop_id)
        sales_goods_mch_code_dict = {}
        print('本店有销量的品len',len(sales_data))
        have_sale_category_code = []
        for s in sales_data:
            sales_goods_mch_code_dict[str(s[3])] = s
            have_sale_category_code.append(str(s[2]))
        print("有销量的三级分类的code",len(have_sale_category_code),sorted(list(set(have_sale_category_code))))
        # print('sales_goods_mch_code_dict',sales_goods_mch_code_dict)

        #   1.2、获取当前台账的商品
        taizhang_goods = self.get_taizhang_goods()  # 获取当前台账的商品
        taizhang_goods_mch_code_list = list(set([i['mch_goods_code'] for i in taizhang_goods]))    # 去重
        print('去重台账goods',len(taizhang_goods_mch_code_list))
        all_goods_len = len(taizhang_goods_mch_code_list)

        # 1.3 获取本店的保护品，即不动的品
        if all_goods_len == 0:
            category_03_list = []
        else:
            category_03_list = self.get_third_category(taizhang_goods_mch_code_list)
        print('本店已有三级分类', len(category_03_list),sorted(category_03_list))
        not_move_goods_mch_code_list = self.calculate_not_move_goods(category_03_list)
        print("本店保护品len",len(not_move_goods_mch_code_list),not_move_goods_mch_code_list)


        # 1.4、遍历货架,得出下架品、不动品和可选下架品
        can_order_mch_code_list = self.get_can_order_list()
        print('可订货len：',len(can_order_mch_code_list))
        for data in taizhang_goods:
            if not data['mch_goods_code'] in can_order_mch_code_list:    # 不可订货即必须下架
                # template_shop_ids,upc,code,predict_sales_amount,mch_goods_code,predict_sales_num,name,is_structure,is_qiuck_seller,is_relation,ranking
                must_out_goods.append((None, data['goods_upc'], None, None, data['mch_goods_code'], None, data['name'], 0, 0, 0, None))

            elif data['mch_goods_code'] in not_move_goods_mch_code_list:    # 保护品即为不动的品
                # print('有销量即为不动的品')
                not_move_goods.append((None, data['goods_upc'],None, None,data['mch_goods_code'], None, data['name'], 0, 0, 0, None))
            else:    # 剩下的是可选下架的
                if data['mch_goods_code'] in sales_goods_mch_code_dict.keys():    # 有销量的进行排序
                    # print('有销量即为不动的品')
                    temp_optional_out_goods.append([None, data['goods_upc'],None, sales_goods_mch_code_dict[data['mch_goods_code']][0],data['mch_goods_code'], None, data['name'], 0, 0, 0])
                else:       # 剩下没销量的为可选下架品的第一优先级
                    optional_out_goods.append((None, data['goods_upc'], None, None, data['mch_goods_code'], None, data['name'], 0, 0, 0, 10000))  # FIXME 分类code为空

        temp_optional_out_goods.sort(key=lambda x: x[3], reverse=True)  # 基于psd金额排序
        for index,goods in enumerate(temp_optional_out_goods):
            goods.append(index+1)
            optional_out_goods.append(tuple(goods))


        # 2、计算新增品
        must_up_goods_len = math.ceil(all_goods_len * 0.03)
        all_structure_goods_list, all_quick_seller_list = self.calculate_quick_seller()  # 获取同组门店的结构品和畅销品


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
            if not data[2] in category_03_list and str(data[4]) in can_order_mch_code_list:
                data.extend([1,1,0])       # is_structure,is_qiuck_seller,is_relation
                candidate_up_goods_list.append(data)

        # 该店有该三级分类,并且可订货
        for data in all_structure_goods_list:
            if data[2] in category_03_list and str(data[4]) in can_order_mch_code_list:
                data.extend([1, 1, 0])  # is_structure,is_qiuck_seller,is_relation
                candidate_up_goods_list.append(data)

        # 该店没有的畅销品，并且可订货
        for data in all_quick_seller_list:
            if not str(data[4]) in taizhang_goods_mch_code_list and str(data[4]) in can_order_mch_code_list:
                data.extend([0, 1, 0])      # is_structure,is_qiuck_seller,is_relation
                candidate_up_goods_list.append(data)



        # candidate_up_goods_list = structure_goods_list + quick_seller_list     #FIXME  怎么综合一下
        # candidate_up_goods_list = list(set(candidate_up_goods_list))
        # print('structure_goods_list',len(structure_goods_list))
        # print('quick_seller_list',len(quick_seller_list))

        # must_up_goods = candidate_up_goods_list[:must_up_goods_len]
        # optional_up_goods = candidate_up_goods_list[must_up_goods_len:]

        # 非日配选出来
        delivery_type_sql = "select delivery_type from uc_merchant_goods where mch_goods_code='{}' and delivery_type is not NULL;"
        conn_ucenter = connections['ucenter']
        cursor_ucenter = conn_ucenter.cursor()

        temp_number = 0    # 上架品选到candidate_up_goods_list候选集的第几个啦
        for goods in candidate_up_goods_list:

            if len(must_up_goods) == must_up_goods_len:
                break
            cursor_ucenter.execute(delivery_type_sql.format(goods[4]))
            try:
                delivery_type = cursor_ucenter.fetchone()[0]
                if delivery_type == 2:
                    must_up_goods.append(goods)
                else:
                    print("怎么回事？")
                    optional_up_goods.append(goods)
                    # send_message('pos店号为{}的店，获取mch_goods_code为{}的日配类型（delivery_type）异常：{}'.format(self.shop_id, goods[4],delivery_type), 1)
            except:
                print("怎么回事222？")
                optional_up_goods.append(goods)
                # send_message('pos店号为{}的店，获取不到mch_goods_code为{}的日配类型（delivery_type）'.format(self.shop_id,goods[4]), 1)
            temp_number += 1
        optional_up_goods += candidate_up_goods_list[temp_number:]






        # 以下4行时添加ranking的值
        print('must_up_goods',len(must_up_goods))
        print('optional_up_goods',len(optional_up_goods))
        for goods in must_up_goods:
            goods.append(None)

        optional_up_goods.sort(key=lambda x: x[3], reverse=False)  # 基于psd金额排序
        for index,goods in enumerate(optional_up_goods):
            goods.append(index+1)

        must_up_goods = [tuple(goods) for goods in must_up_goods]
        optional_up_goods = [tuple(goods) for goods in optional_up_goods]

        # print('must_up_goods', must_up_goods)
        print()
        # print('optional_up_goods', optional_up_goods)









        # 3、保存至数据库

        not_move_goods = list(set(not_move_goods))
        must_out_goods = list(set(must_out_goods))
        optional_out_goods = list(set(optional_out_goods))

        print(len(not_move_goods))
        print(len(must_out_goods))
        print(len(optional_out_goods))

        print(not_move_goods[:10])

        self.save_data(not_move_goods, 0)
        self.save_data(must_out_goods, 2)
        self.save_data(optional_out_goods,4)
        self.save_data(must_up_goods, 1)
        self.save_data(optional_up_goods, 3)

    def save_data(self,data,goods_role):
    # def save_data(self,data,is_new_goods,goods_out_status,goods_add_status):
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
        insert_sql_02 = "insert into goods_goodsselectionhistory(shopid,template_shop_ids,upc,code,predict_sales_amount,mch_code,mch_goods_code,predict_sales_num,name,batch_id,uc_shopid,goods_role,is_structure,is_qiuck_seller,is_relation,ranking,handle_goods_role) values ({},%s,%s,%s,%s,2,%s,%s,%s,'{}','{}',{},%s,%s,%s,%s,{})"
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
        # print(insert_sql_02)
        print(tuple_data[:5])
        cursor.executemany(insert_sql_02.format(self.shop_id,self.batch_id, self.uc_shopid,goods_role,goods_role).replace('None', 'NULL'), tuple_data[:])
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
    f = DailyChangeGoods(pos_shopid, "88,3156,3238",batch_id,uc_shop_id)
    # f = DailyChangeGoods(pos_shopid, "1284,3955,3779,1925,4076,1924,3598",batch_id,uc_shop_id)
    f.recommend_03()

if __name__ == '__main__':

    f = DailyChangeGoods(1284, "1284,3955,3779,1925,4076,1924,3598",'lishu_test_003',806)
    f.recommend_03()
    # start_choose_goods('lishu_test_01',806,88)






