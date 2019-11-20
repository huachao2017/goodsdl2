

import datetime,pymysql
import os,django
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
# django.setup()
# from django.db import connections

class AddGoods:

    def __init__(self,shop_id,template_shop_ids,topn_ratio=0.4,days=13):
        self.category_goods_list = []    # 结构品
        self.template_shop_ids = template_shop_ids
        self.shop_id = shop_id
        self.topn_ratio = topn_ratio    # 取前百分之多少作为畅销品
        self.days = days     #取数周期

        conn = pymysql.connect('123.103.16.19', 'readonly', password='fxiSHEhui2018@)@)', database='dmstore',charset="utf8", port=3300, use_unicode=True)
        self.cursor = conn.cursor()
        # self.cursor = connections['dmstore'].cursor()

    def get_data(self,shop_id):
        """
        :param shop_id: 目标店的id
        :param days: 多少天的范围内进行销量排序选择
        :return:
        """
        now = datetime.datetime.now()
        now_date = now.strftime('%Y-%m-%d %H:%M:%S')
        week_ago = (now - datetime.timedelta(days=self.days)).strftime('%Y-%m-%d %H:%M:%S')
        sql = "select sum(p.amount),g.upc,g.corp_classify_code,g.neighbor_goods_id,g.price,p.name from dmstore.payment_detail as p left join dmstore.goods as g on p.goods_id=g.id where p.create_time > '{}' and p.create_time < '{}' and p.shop_id={} group by g.upc order by sum(p.amount) desc;"
        self.cursor.execute(sql.format(week_ago, now_date, shop_id))
        results = self.cursor.fetchall()
        # cursor.close()
        print(results)
        return results

    def get_sale_goods(self):
        """
        获取该店在售的商品
        :return:
        """
        sql = "SELECT * FROM shop_goods WHERE shop_id = {} AND STATUS=10;"   # TODO 要哪些字段
        self.cursor.execute(sql.format(self.shop_id))
        results = self.cursor.fetchall()
        return results

    def calculate_quick_seller(self):
        """
        计算畅销品，根据商品在每个店的畅销品的出现次数
        比如：
        一共3个模板店，
        如果次数设为1，则相当于把3个店看成一个店
        如果设为2，即每个商品在2个店里是畅销品就是最终畅销品
        如果设为3，即三个店的交集是最终畅销品
        :param topn:
        :return:
        """
        template_shop_ids_list = self.template_shop_ids.split(',')

        all_goods = []  # 每个店的畅销品的去重汇总
        quick_seller_list_all = []  # 每个店的畅销品列表是其值
        for template_shop_id in template_shop_ids_list:
            data = self.get_data(template_shop_id)
            quick_seller_list = data[:int(len(data) * self.topn_ratio)]
            quick_seller_list_all.append(quick_seller_list)
            for d in quick_seller_list:
                if not d in all_goods:
                    all_goods.append(d)
        goods_time_dict = {}  # 商品出现在各模板店畅销品列表的次数，k为goods，v为次数
        for goods in all_goods:
            temp_num = 0
            for quick_seller_list in quick_seller_list_all:
                if goods in quick_seller_list:
                    temp_num += 1
            goods_time_dict[goods] = temp_num
        print(goods_time_dict)
        return goods_time_dict

    def calculate_category_goods(self):
        """
        计算结构品的数据
        :return:
        """

        all_data = None
        # for data in all_data:
        #     pass


    def recommend(self):

        quick_seller = self.calculate_quick_seller()    #带次数的畅销品字典
        print(quick_seller)
        for k,v in quick_seller.items():
            if v >= 2:
                print(k,v)
        quick_seller_list = []
        # TODO 畅销品列表计算

        self.calculate_category_goods()   #计算结构品的数据

        sale_goods = self.get_sale_goods()  # 在售的商品
        recommend_list = []
        for goods in self.category_goods_list:
            if goods not in sale_goods:        #FIXME goods是一回事吗
                recommend_list.append(goods)

        for goods in quick_seller_list:
            if goods not in sale_goods and goods not in recommend_list:
                recommend_list.append(goods)

        return recommend_list

if __name__ == '__main__':

    add_goods = AddGoods(1284,"3955,3779,1925,4076,1924")
    data = add_goods.recommend()
    print(data)

