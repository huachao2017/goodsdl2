import time
import urllib.request
import json
import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
django.setup()
from django.db import connections

from goods.models import ai_sales_order

def order_commit(shopid, erp_shop_type, shop_upc_ordersales):

    try:
        cursor_dmstore = connections['dmstore'].cursor()
        cursor_dmstore.execute('select erp_shop_id from erp_shop_related where shop_id={} and erp_shop_type = {}'.format(shopid,erp_shop_type))
        (erp_shopid,) = cursor_dmstore.fetchone()
        cursor_dmstore.close()

        create_date = str(time.strftime('%Y-%m-%d', time.localtime()))
        # urltest = "http://erp.aicvs.cn/automaticOrdering/addShopBuy?erpShopId={}"
        url = "http://erp.aicvs.cn/automaticOrdering/addShopBuy?erpShopId={}"
        headers = {
            "Accept":"application/json",
            "Content-Type":"application/json"
        }

        order_data = []
        for one_order in shop_upc_ordersales:
            order_data.append({
                "upc":one_order.upc,
                "number":one_order.order_sale
            })
        index = 0
        while True:
            try:
                json_info = json.dumps(order_data)
                print(json_info)
                data = bytes(json_info, 'utf8')
                request = urllib.request.Request(url=url.format(erp_shopid), data=data, headers=headers)

                response = urllib.request.urlopen(request)
                print(response.read().decode())
                break
            except Exception as e:
                index += 1
                if index > 5:
                    raise e
                print('order_commit error:{}'.format(e))
                time.sleep(1)
                continue
        # 提交正确加入数据库
        for one_order in shop_upc_ordersales:
            ai_sales_order.objects.create(
                shopid=shopid,
                upc = one_order.upc,
                order_sale = one_order.order_sale,
                predict_sale = one_order.predict_sale,
                min_stock = one_order.min_stock,
                max_stock = one_order.max_stock,
                stock = one_order.stock,
                create_date = create_date,
                multiple = one_order.multiple,
                start_max = one_order.start_max,
                start_min = one_order.start_min,
                start_sum = one_order.start_sum,
                erp_shop_type = one_order.erp_shop_type,
            )
    except Exception as e:
        print('order_commit error:{}'.format(e))

if __name__ == "__main__":
    order_commit(1284,0,[])