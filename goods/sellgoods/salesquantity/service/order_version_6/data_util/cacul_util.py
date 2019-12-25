from goods.sellgoods.commonbean.goods_ai_sales_order import SalesOrder
from goods.sellgoods.salesquantity.service.order_version_6.data_util.goods_info import get_shop_order_goods
from goods.sellgoods.salesquantity.bean import taskflow
from goods.sellgoods.salesquantity.proxy import order_rule
import math
import demjson
import time
import traceback
def get_saleorder_ins(drg_ins, shop_id,shop_type):
    sales_order_ins = SalesOrder()
    sales_order_ins.shopid = shop_id
    if drg_ins.package_type in taskflow.package_type_name_dict.keys():
        sales_order_ins.package_type = taskflow.package_type_name_dict[drg_ins.package_type]
    else:
        sales_order_ins.package_type = taskflow.package_type_name_dict[0]
    sales_order_ins.shop_name = drg_ins.shop_name
    sales_order_ins.start_max = drg_ins.max_disnums
    sales_order_ins.start_min = drg_ins.min_disnums
    sales_order_ins.upc = drg_ins.upc
    sales_order_ins.erp_shop_type = shop_type
    sales_order_ins.order_sale = 0
    sales_order_ins.max_stock = drg_ins.max_disnums
    sales_order_ins.min_stock = drg_ins.min_disnums
    sales_order_ins.min_disnums = drg_ins.min_disnums
    sales_order_ins.max_disnums = drg_ins.max_disnums
    sales_order_ins.stock = drg_ins.stock
    sales_order_ins.start_sum = drg_ins.start_sum
    sales_order_ins.multiple = drg_ins.multiple
    sales_order_ins.goods_name = drg_ins.goods_name
    sales_order_ins.supply_stock = drg_ins.supply_stock
    sales_order_ins.delivery_type = drg_ins.delivery_type
    sales_order_ins.storage_day = drg_ins.storage_day
    sales_order_ins.mch_goods_code = drg_ins.mch_code
    sales_order_ins.category_id = drg_ins.category_id
    sales_order_ins.category1_id = drg_ins.category1_id
    sales_order_ins.category2_id = drg_ins.category2_id
    sales_order_ins.psd_nums_4 = drg_ins.psd_nums_4
    sales_order_ins.psd_amount_4 = drg_ins.psd_amount_4
    sales_order_ins.face_num = 0
    sales_order_ins.sub_count = drg_ins.sub_count
    sales_order_ins.upc_price = drg_ins.upc_price
    sales_order_ins.upc_psd_amount_avg_4 = drg_ins.upc_psd_amount_avg_4
    sales_order_ins.upc_psd_amount_avg_1 = drg_ins.upc_psd_amount_avg_1
    sales_order_ins.purchase_price = drg_ins.purchase_price
    sales_order_ins.max_scale = drg_ins.max_scale
    sales_order_ins.oneday_max_psd = drg_ins.oneday_max_psd
    sales_order_ins.shelf_inss = drg_ins.shelf_inss
    sales_order_ins.height = drg_ins.height
    sales_order_ins.width = drg_ins.width
    sales_order_ins.depth = drg_ins.depth
    shelf_data = []
    for shelf_ins in drg_ins.shelf_inss:
        sales_order_ins.face_num += shelf_ins.face_num
        shelf_data.append({"tz_id":shelf_ins.taizhang_id,"shelf_id":shelf_ins.shelf_id,"shelf_order":0,"face_num":shelf_ins.face_num})
    sales_order_ins.shelf_order_info = shelf_data
    return sales_order_ins


def get_goods_batch_order_data_warhouse(batch_id,goods_order_all):
    """
    获取仓库单位的  订单数据
    :param batch_id:
    :param goods_order_all:
    :return:
    """
    order_data,order_data_dict = get_order_data_warhouse(goods_order_all)
    # 加入冰淇淋的 空间限制规则：
    try:
        print ("冰淇淋空间限制前 订货品个数 = "+str(len(list(demjson.decode(order_data)))))
        order_data_dict = order_rule.rule_bingql(drg_inss=goods_order_all,order_data_dict=order_data_dict)
        order_data = update_order_data(order_data_dict,order_data)
        print("冰淇淋空间限制后 订货品个数 = " + str(len(list(demjson.decode(order_data)))))
    except:
        print ("冰淇淋空间限制 规则 error , check ....")
        traceback.print_exc()
    order_data_all = get_order_data_all_warhouse(goods_order_all,order_data_dict)
    create_time = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    update_time = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    return [(batch_id, order_data, create_time, update_time, order_data_all)]




def get_order_data_all_warhouse(goods_order_all,order_data_dict):
    jsondata = []
    print("店内目标库存,仓库总订货数,门店id,门店名称,商品id,upc,商品名称,"
          "一级分类,二级分类,三级分类,face数,陈列规格,"
          "模板店4周预估psd,模板店4周预估psd金额,配送单位,最小陈列数,"
          "最大陈列数,门店库存,仓库库存,配送类型,保质期,"
          "起订量,在途订货数,进货价,商品单价,开店以来单天最大psd数量,"
          "最大陈列比例,4周实际销售psd数量,1周实际销售psd数量,品的生命周期:0首次1新品2旧品,"
          "7天平均废弃率,7天平均废弃后毛利率,7天平均废弃量,周1-5平均psd数量,周6-7平均psd数量,2周的psd数量,2周小类的psd数量,单face配置最小陈列量,补货单在途订单数")
    for drg_ins in goods_order_all:
        mch_goods_dict = {}
        warhouse_order_sale = 0
        key = str(drg_ins.mch_code)+","+str(drg_ins.upc)
        if key in order_data_dict.keys():
            warhouse_order_sale = order_data_dict[key]
        mch_goods_dict['order_sale'] = drg_ins.order_sale
        mch_goods_dict['warhouse_order_sale']=warhouse_order_sale
        mch_goods_dict['ucshop_id'] = drg_ins.ucshop_id
        mch_goods_dict['shop_name'] = drg_ins.shop_name
        mch_goods_dict['mch_code'] = drg_ins.mch_code
        mch_goods_dict['upc'] = drg_ins.upc
        mch_goods_dict['goods_name'] = drg_ins.goods_name
        mch_goods_dict['category1_id'] = drg_ins.category1_id
        mch_goods_dict['category2_id'] = drg_ins.category2_id
        mch_goods_dict['category_id'] = drg_ins.category_id
        mch_goods_dict['face_num'] = drg_ins.face_num
        mch_goods_dict['package_type'] = drg_ins.package_type
        mch_goods_dict['psd_nums_4'] = drg_ins.psd_nums_4
        mch_goods_dict['psd_amount_4'] = drg_ins.psd_amount_4
        mch_goods_dict['psd_nums_2'] = drg_ins.psd_nums_2
        mch_goods_dict['psd_nums_2_cls'] = drg_ins.psd_nums_2_cls
        mch_goods_dict['start_sum'] = drg_ins.start_sum
        mch_goods_dict['min_disnums'] = drg_ins.min_disnums
        mch_goods_dict['max_disnums'] = drg_ins.max_disnums
        mch_goods_dict['stock'] = drg_ins.stock
        mch_goods_dict['supply_stock'] = drg_ins.supply_stock
        mch_goods_dict['delivery_type'] = drg_ins.delivery_type
        mch_goods_dict['storage_day'] = drg_ins.storage_day
        mch_goods_dict['sub_count'] = drg_ins.sub_count
        mch_goods_dict['purchase_price'] = drg_ins.purchase_price
        mch_goods_dict['upc_price'] = drg_ins.upc_price
        mch_goods_dict['oneday_max_psd'] = math.ceil(drg_ins.oneday_max_psd / drg_ins.upc_price)
        mch_goods_dict['upc_psd_amount_avg_4'] = float(drg_ins.upc_psd_amount_avg_4 / drg_ins.upc_price)
        mch_goods_dict['upc_psd_amount_avg_1'] = float(drg_ins.upc_psd_amount_avg_1 / drg_ins.upc_price)
        mch_goods_dict['upc_status_type'] = drg_ins.upc_status_type
        mch_goods_dict['loss_avg'] = drg_ins.loss_avg
        mch_goods_dict['loss_avg_profit_amount'] = drg_ins.loss_avg_profit_amount
        mch_goods_dict['loss_avg_nums'] = drg_ins.loss_avg_nums
        mch_goods_dict['week_1_5_avg_psdnums'] = float(drg_ins.upc_psd_amount_avg_1_5 / drg_ins.upc_price)
        mch_goods_dict['week_6_7_avg_psdnums'] = float(drg_ins.upc_psd_amount_avg_6_7 / drg_ins.upc_price)
        mch_goods_dict['single_face_min_disnums'] = drg_ins.single_face_min_disnums
        mch_goods_dict['add_sub_count'] = drg_ins.add_sub_count
        shelf_data = []
        for shelf_ins in drg_ins.shelf_inss:
            shelf_data.append({"tz_id": shelf_ins.taizhang_id, "shelf_id": shelf_ins.shelf_id,
                               "face_num": shelf_ins.face_num,"level_depth":shelf_ins.level_depth})
        mch_goods_dict['shelf_data'] = shelf_data
        mch_goods_dict['depth'] = drg_ins.depth
        mch_goods_dict['height'] = drg_ins.height
        mch_goods_dict['width'] = drg_ins.width
        print("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"
              "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"
              "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"
              "%s,%s,%s,%s,%s,%s,%s,%s,%s"
              % (str(drg_ins.order_sale),str(warhouse_order_sale),
                 str(drg_ins.ucshop_id), str(drg_ins.shop_name), str(drg_ins.mch_code),
                 str(drg_ins.upc), str(drg_ins.goods_name),
                 str(drg_ins.category1_id), str(drg_ins.category2_id), str(drg_ins.category_id), str(drg_ins.face_num),
                 str(drg_ins.package_type),
                 str(drg_ins.psd_nums_4), str(drg_ins.psd_amount_4), str(drg_ins.start_sum), str(drg_ins.min_disnums),
                 str(drg_ins.max_disnums), str(drg_ins.stock), str(drg_ins.supply_stock), str(drg_ins.delivery_type),
                 str(drg_ins.storage_day),
                 str(drg_ins.start_sum), str(drg_ins.sub_count), str(drg_ins.purchase_price), str(drg_ins.upc_price),
                 str(math.ceil(drg_ins.oneday_max_psd / drg_ins.upc_price)),
                 str(drg_ins.max_scale), str(float(drg_ins.upc_psd_amount_avg_4 / drg_ins.upc_price)),
                 str(float(drg_ins.upc_psd_amount_avg_1 / drg_ins.upc_price)), str(drg_ins.upc_status_type),
                 str(drg_ins.loss_avg), str(drg_ins.loss_avg_profit_amount), str(drg_ins.loss_avg_nums),
                 str(float(drg_ins.upc_psd_amount_avg_1_5 / drg_ins.upc_price)),
                 str(float(drg_ins.upc_psd_amount_avg_6_7 / drg_ins.upc_price)),
                 str(float(drg_ins.psd_nums_2)), str(float(drg_ins.psd_nums_2_cls)),str(drg_ins.single_face_min_disnums),str(drg_ins.add_sub_count)))
        jsondata.append(mch_goods_dict)
    order_all_data = demjson.encode(jsondata)
    return order_all_data


class  Cls_Order_Data:
    mch_goods_code = None
    upc = None
    delivery_type = 1
    order_sale =  0
    min_disnums = 0
    max_disnums = 0
    shop_stock  = 0
    supply_stock = 0
    start_sum = 0
    shelf_inss = None
    height = 0
    width = 0
    depth = 0


def get_order_data_warhouse(goods_order_all):
    jsondata = []
    data_dict = {}
    for drg_ins in goods_order_all:
        key = str(drg_ins.mch_code)+","+str(drg_ins.upc)
        if key not in data_dict:
            order_data_ins = Cls_Order_Data()
            order_data_ins.mch_goods_code = drg_ins.mch_code
            order_data_ins.upc = drg_ins.upc
            order_data_ins.delivery_type = drg_ins.delivery_type
            order_data_ins.start_sum = drg_ins.start_sum
            order_data_ins.height = drg_ins.height
            order_data_ins.depth = drg_ins.depth
            order_data_ins.width = drg_ins.width
            order_data_ins.order_sale = drg_ins.order_sale
            order_data_ins.min_disnums = drg_ins.min_disnums
            order_data_ins.max_disnums = drg_ins.max_disnums
            order_data_ins.shop_stock = drg_ins.stock
            order_data_ins.supply_stock = drg_ins.supply_stock
            order_data_ins.sub_count = drg_ins.sub_count
            shelf_inss = []
            for shelf_ins in drg_ins.shelf_inss:
                shelf_inss.append(shelf_ins)
            order_data_ins.shelf_inss = shelf_inss
            data_dict[key] = order_data_ins
        else:
            order_data_ins = data_dict[key]
            order_data_ins.order_sale =  drg_ins.order_sale+order_data_ins.order_sale
            order_data_ins.min_disnums = order_data_ins.min_disnums + drg_ins.min_disnums
            order_data_ins.max_disnums =  order_data_ins.max_disnums + drg_ins.max_disnums
            order_data_ins.shop_stock = drg_ins.stock + order_data_ins.shop_stock
            shelf_order_info = []
            for shelf_ins1 in order_data_ins.shelf_inss:
                shelf_order_info.append(shelf_ins1)
            for shelf_ins2 in drg_ins.shelf_inss:
                shelf_order_info.append(shelf_ins2)
            order_data_ins.shelf_inss = shelf_order_info

    order_data_inss = []
    for key in data_dict:
        order_data_ins = data_dict[key]
        order_sale = order_data_ins.order_sale - order_data_ins.sub_count - order_data_ins.shop_stock - order_data_ins.supply_stock
        if order_sale > 0 :
            # 起订量规则
            order_sale = order_rule.rule_start_num2(order_sale, order_data_ins.start_sum)
            order_data_ins.order_sale = order_sale
        else:
            order_data_ins.order_sale = 0
        if order_data_ins.order_sale > 0 :
            order_data_inss.append(order_data_ins)
    # 日配品 空间限制规则
    print ("日配品 空间限制前：len(order_data_inss) = "+str(len(order_data_inss)))
    order_data_inss = order_rule.rule_daydelivery_type(order_data_inss)
    print("日配品 空间限制后：len(order_data_inss) = " + str(len(order_data_inss)))
    new_data_dict = {}
    for order_data_ins in order_data_inss:
        if order_data_ins.order_sale > 0 :
            order_data_dict = {}
            key = str(order_data_ins.mch_goods_code)+","+ order_data_ins.upc
            new_data_dict[key] = order_data_ins.order_sale
            order_data_dict["mch_goods_code"] =order_data_ins.mch_goods_code
            order_data_dict["upc"] = order_data_ins.upc
            order_data_dict["order_sale"] = order_data_ins.order_sale
            order_data_dict["min_disnums"] = order_data_ins.min_disnums
            order_data_dict["max_disnums"] = order_data_ins.max_disnums
            order_data_dict["shop_stock"] = order_data_ins.shop_stock
            order_data_dict["supply_stock"] = order_data_ins.supply_stock
            shelf_data = []
            face_num = 0
            for shelf_ins in order_data_ins.shelf_inss:
                face_num += shelf_ins.face_num
                shelf_data.append({"tz_id": shelf_ins.taizhang_id, "shelf_id": shelf_ins.shelf_id, "shelf_order": 0,
                                   "face_num": shelf_ins.face_num})
            order_data_dict["shelf_order_info"] = shelf_data
            jsondata.append(order_data_dict)
    order_data = demjson.encode(jsondata)
    return order_data,new_data_dict


def update_order_data(new_data_dict,order_data):
    order_data_dict = list(demjson.decode(order_data))
    order_data_new = []
    for key in new_data_dict:
        mch_goods_code = str(key).split("_")[0]
        upc = str(key).split("_")[1]
        order_sale = new_data_dict[key]
        for v_dict in order_data_dict:
            if order_sale>0 and int(v_dict['mch_goods_code']) == int(mch_goods_code) and str(v_dict['upc']) == str(upc):
                v_dict['order_sale'] = order_sale
                order_data_new.append(v_dict)
    order_data_new = demjson.encode(order_data_new)
    return order_data_new










def get_goods_batch_order_data(batch_id,sales_order_inss,result):
    jsondata = []
    for sales_order_ins in sales_order_inss:
        data_dict = {}
        data_dict['order_sale'] = sales_order_ins.order_sale
        data_dict['mch_goods_code'] = sales_order_ins.mch_goods_code
        data_dict['upc'] = sales_order_ins.upc
        data_dict['min_disnums'] = sales_order_ins.min_disnums
        data_dict['max_disnums'] = sales_order_ins.max_disnums
        data_dict['shop_stock'] = sales_order_ins.stock
        data_dict['supply_stock'] = sales_order_ins.supply_stock
        data_dict['shelf_order_info'] = sales_order_ins.shelf_order_info
        jsondata.append(data_dict)
    order_data = demjson.encode(jsondata)
    order_all_data = get_order_all_data(result,sales_order_inss)
    create_time = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    update_time = str(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()))
    return [(batch_id,order_data,create_time,update_time,order_all_data)]

def get_order_all_data(result,sales_order_inss):
    jsondata=[]
    print("订货数,门店id,门店名称,商品id,upc,商品名称,"
          "一级分类,二级分类,三级分类,face数,陈列规格,"
          "模板店4周预估psd,模板店4周预估psd金额,配送单位,最小陈列数,"
          "最大陈列数,门店库存,仓库库存,配送类型,保质期,"
          "起订量,在途订货数,进货价,商品单价,开店以来单天最大psd数量,"
          "最大陈列比例,4周实际销售psd数量,1周实际销售psd数量,品的生命周期:0首次1新品2旧品,"
          "7天平均废弃率,7天平均废弃后毛利率,7天平均废弃量,周1-5平均psd数量,周6-7平均psd数量,2周的psd数量,2周小类的psd数量,单face配置最小陈列量,补货单在途订单数")
    for mch_code in result:
        mch_goods_dict = {}
        drg_ins = result[mch_code]
        order_sale = 0
        for sales_order_ins in sales_order_inss:
            if drg_ins.upc == sales_order_ins.upc:
                order_sale = sales_order_ins.order_sale
        mch_goods_dict['order_sale'] = order_sale
        mch_goods_dict['ucshop_id'] = drg_ins.ucshop_id
        mch_goods_dict['shop_name'] = drg_ins.shop_name
        mch_goods_dict['mch_code'] = drg_ins.mch_code
        mch_goods_dict['upc'] = drg_ins.upc
        mch_goods_dict['goods_name'] = drg_ins.goods_name
        mch_goods_dict['category1_id'] = drg_ins.category1_id
        mch_goods_dict['category2_id'] = drg_ins.category2_id
        mch_goods_dict['category_id'] = drg_ins.category_id
        mch_goods_dict['face_num'] = drg_ins.face_num
        mch_goods_dict['package_type'] = drg_ins.package_type
        mch_goods_dict['psd_nums_4'] = drg_ins.psd_nums_4
        mch_goods_dict['psd_amount_4'] = drg_ins.psd_amount_4
        mch_goods_dict['psd_nums_2'] = drg_ins.psd_nums_2
        mch_goods_dict['psd_nums_2_cls'] = drg_ins.psd_nums_2_cls
        mch_goods_dict['start_sum'] = drg_ins.start_sum
        mch_goods_dict['min_disnums'] = drg_ins.min_disnums
        mch_goods_dict['max_disnums'] = drg_ins.max_disnums
        mch_goods_dict['stock'] = drg_ins.stock
        mch_goods_dict['supply_stock'] = drg_ins.supply_stock
        mch_goods_dict['delivery_type'] = drg_ins.delivery_type
        mch_goods_dict['storage_day'] = drg_ins.storage_day
        mch_goods_dict['sub_count'] = drg_ins.sub_count
        mch_goods_dict['purchase_price'] = drg_ins.purchase_price
        mch_goods_dict['upc_price'] = drg_ins.upc_price
        mch_goods_dict['oneday_max_psd'] = math.ceil(drg_ins.oneday_max_psd / drg_ins.upc_price)
        mch_goods_dict['upc_psd_amount_avg_4'] = float(drg_ins.upc_psd_amount_avg_4 / drg_ins.upc_price)
        mch_goods_dict['upc_psd_amount_avg_1'] = float(drg_ins.upc_psd_amount_avg_1 / drg_ins.upc_price)
        mch_goods_dict['upc_status_type'] = drg_ins.upc_status_type
        mch_goods_dict['loss_avg'] = drg_ins.loss_avg
        mch_goods_dict['loss_avg_profit_amount'] = drg_ins.loss_avg_profit_amount
        mch_goods_dict['loss_avg_nums'] = drg_ins.loss_avg_nums
        mch_goods_dict['week_1_5_avg_psdnums'] = float(drg_ins.upc_psd_amount_avg_1_5 / drg_ins.upc_price)
        mch_goods_dict['week_6_7_avg_psdnums'] = float(drg_ins.upc_psd_amount_avg_6_7 / drg_ins.upc_price)
        mch_goods_dict['single_face_min_disnums'] = drg_ins.single_face_min_disnums
        mch_goods_dict['add_sub_count'] = drg_ins.add_sub_count
        shelf_data = []
        for shelf_ins in drg_ins.shelf_inss:
            shelf_data.append({"tz_id": shelf_ins.taizhang_id, "shelf_id": shelf_ins.shelf_id,
                               "face_num": shelf_ins.face_num, "level_depth": shelf_ins.level_depth})
        mch_goods_dict['shelf_data'] = shelf_data
        mch_goods_dict['depth'] = drg_ins.depth
        mch_goods_dict['height'] = drg_ins.height
        mch_goods_dict['width'] = drg_ins.width
        print("%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"
              "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"
              "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,"
              "%s,%s,%s,%s,%s,%s,%s,%s"
              % (str(order_sale),
                 str(drg_ins.ucshop_id), str(drg_ins.shop_name), str(drg_ins.mch_code),
                 str(drg_ins.upc), str(drg_ins.goods_name),
                 str(drg_ins.category1_id), str(drg_ins.category2_id), str(drg_ins.category_id), str(drg_ins.face_num),
                 str(drg_ins.package_type),
                 str(drg_ins.psd_nums_4), str(drg_ins.psd_amount_4), str(drg_ins.start_sum), str(drg_ins.min_disnums),
                 str(drg_ins.max_disnums), str(drg_ins.stock), str(drg_ins.supply_stock), str(drg_ins.delivery_type),
                 str(drg_ins.storage_day),
                 str(drg_ins.start_sum), str(drg_ins.sub_count), str(drg_ins.purchase_price), str(drg_ins.upc_price),
                 str(math.ceil(drg_ins.oneday_max_psd / drg_ins.upc_price)),
                 str(drg_ins.max_scale), str(float(drg_ins.upc_psd_amount_avg_4 / drg_ins.upc_price)),
                 str(float(drg_ins.upc_psd_amount_avg_1 / drg_ins.upc_price)), str(drg_ins.upc_status_type),
                 str(drg_ins.loss_avg),str(drg_ins.loss_avg_profit_amount),str(drg_ins.loss_avg_nums),
                 str(float(drg_ins.upc_psd_amount_avg_1_5 / drg_ins.upc_price)),str(float(drg_ins.upc_psd_amount_avg_6_7 / drg_ins.upc_price)),
                 str(float(drg_ins.psd_nums_2)),str(float(drg_ins.psd_nums_2_cls)),str(drg_ins.single_face_min_disnums),str(drg_ins.add_sub_count)))
        jsondata.append(mch_goods_dict)
    order_all_data = demjson.encode(jsondata)
    return order_all_data


def data_process(shop_id,add_type=False):
    try:
        result = get_shop_order_goods(shop_id, add_type=add_type)
    except:
        traceback.print_exc()
        print("shop_id day generate order failed ,get_data error   " + str(shop_id))
        result = None
    return result