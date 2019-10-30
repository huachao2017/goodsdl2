from set_config import config
from goods.sellgoods.salesquantity.utils.mysql_util import MysqlUtil
from goods.sellgoods.sql.sales_quantity import sql_params
ucenter = config.ucenter
# 根据shop_id 获取门店下的货架信息
def displayall_info():
    mysql_ins = MysqlUtil(ucenter)
    # 获取所有陈列
    get_all_display = sql_params['get_all_display']
    results = mysql_ins.selectAll(get_all_display)
    for result in results:
        print ("do ....")
