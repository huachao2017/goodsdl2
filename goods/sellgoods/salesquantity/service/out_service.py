from goods.sellgoods.salesquantity.local_util import out_service_util
# day = "2019-10-17"  这种格式 day 是当前日期   day_sqles 统计的当天日期的销量
# days 是需要预测当前天 之后多少天的销量 ， 不传依据配置 默认7天
def get_nextday_sales(shop_ids,upcs,day,days_sales,days=None):
    predicts_info = out_service_util.get_nextday_sales(shop_ids, upcs, day, days_sales, days=days)
    return predicts_info
