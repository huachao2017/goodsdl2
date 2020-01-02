
"""
首次换品
"""
import decimal
from  decimal import Decimal
import datetime,pymysql
import os,django

# import main.import_django_settings
# from django.db import connections

class FirstChooseGoods:
    """
    目前只是非日配的首次选品逻辑
    """

    def __init__(self,shop_id,template_shop_ids,topn_ratio=0.6,days=28):
        self.category_goods_list = []    # 结构品
        self.template_shop_ids = template_shop_ids.split(',')
        self.shop_id = shop_id
        self.topn_ratio = Decimal(topn_ratio)  # 取累计psd金额的百分之多少作为畅销品
        self.days = days     # 取数周期
        self.third_category_list = []      # 三级分类的列表
        self.first_category_goods_count_dict = {}     # 一级分类选品预估的数量

        conn = pymysql.connect('123.103.16.19', 'readonly', password='fxiSHEhui2018@)@)', database='dmstore',charset="utf8", port=3300, use_unicode=True)
        self.cursor = conn.cursor()
        # self.cursor = connections['dmstore'].cursor()

    def get_data(self,third_category,shop_ids):
        """

        :param third_category:
        :param shop_ids:
        :return:
        """
        # print(shop_ids)

        now = datetime.datetime.now()
        now_date = now.strftime('%Y-%m-%d %H:%M:%S')
        week_ago = (now - datetime.timedelta(days=self.days)).strftime('%Y-%m-%d %H:%M:%S')
        if type(shop_ids) is list:
            print('list,third_category',shop_ids,third_category)
            shop_ids = tuple(shop_ids)
            sql = "select sum(p.amount),g.upc,g.corp_classify_code,g.neighbor_goods_id,g.price,p.name from dmstore.payment_detail as p left join dmstore.goods as g on p.goods_id=g.id where p.create_time > '{}' and p.create_time < '{}' and p.shop_id in {} and g.corp_classify_code={} group by g.upc order by sum(p.amount) desc;"
        elif type(shop_ids) is str:
            # print('str',shop_ids,type(shop_ids))
            sql = "select sum(p.amount),g.upc,g.corp_classify_code,g.neighbor_goods_id,g.price,p.name from dmstore.payment_detail as p left join dmstore.goods as g on p.goods_id=g.id where p.create_time > '{}' and p.create_time < '{}' and p.shop_id = {} and g.corp_classify_code={} group by g.upc order by sum(p.amount) desc;"
        else:
            print('none', shop_ids,type(shop_ids))
            return None
        self.cursor.execute(sql.format(week_ago, now_date, shop_ids,third_category))
        results = self.cursor.fetchall()
        # cursor.close()
        print(results)
        return results

    def get_third_category_list(self):
        """
        获取一段取数周期内，有销量的品的所有三级分类列表
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
        同组门店中每个三级分类下： 4周的psd金额或psd /（门店数*在售天数）的前60-70%
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
            all_shop_data = self.get_data(third_category,self.template_shop_ids)
            # 以下13行代码主要是统计upc取数周期内在各店出现的次数
            all_one_shop_data_list = []
            for template_shop_id in self.template_shop_ids:

                one_shop_data = self.get_data(third_category,template_shop_id)
                all_one_shop_data_list.append(one_shop_data)
            all_upc = [i[1] for i in all_shop_data]   #FIXME
            upc_time = {}           # upc在各店出现的次数，k为upc，v为次数
            for upc in all_upc:
                temp_num = 0
                for one_shop_data in all_one_shop_data_list:
                    for data in one_shop_data:
                        if upc == data[1]: #FIXME
                            temp_num += 1
                if temp_num > 2:    # 出现大于0次的都加进去
                    upc_time[upc] = temp_num

            print('upc_time',upc_time)
            third_category_quick_seller_list = []
            for data in all_shop_data:     # psd金额除以商店数
                try:
                    third_category_quick_seller_list.append([data[1],data[0]/upc_time[data[1]]])
                except:
                    pass
            category_dict[third_category] = third_category_quick_seller_list

        quick_seller_list = []
        for category, goods_list in category_dict.items():
            goods_list.sort(key=lambda x: x[1], reverse=True)  # 基于psd金额排序
            print('goods_list',goods_list)
            amount = 0  # 分类下psd金额的总额
            for goods in goods_list:
                amount += goods[1]

            temp_amount = 0
            for goods in goods_list:  # 将累计前占比60%psd金额的商品选出来，遇到边界少选策略

                temp_amount += goods[1]
                if temp_amount > amount * self.topn_ratio:
                    break
                quick_seller_list.append(goods[0])
        return quick_seller_list

    def calculate_category_goods(self):
        """
        计算结构品的数据
        :return:
        """

        all_data = None
        # for data in all_data:
        #     pass
        return []


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

def start_choose_goods(batch_id,uc_shop_id):
    pass

if __name__ == '__main__':

    first_choose_goods = FirstChooseGoods(1284, "3955,3779,1925,4076,1924")
    data = first_choose_goods.recommend()
    # data = add_goods.get_third_category_list()
    print('最终增品',data)
    print('最终增品长度',len(data))





