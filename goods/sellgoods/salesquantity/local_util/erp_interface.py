import time
import urllib.request
import json
import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "main.settings")
django.setup()
from django.db import connections

from goods.models import ai_sales_order

def order_commit(shop_upc_ordersales):
    cursor = connections['dmstore'].cursor()
    cursor.execute('select shop_id, erp_shop_id from erp_shop_related where erp_shop_type = 0')
    relate_list = cursor.fetchall()
    cursor.close()
    print(relate_list)

    create_date = str(time.strftime('%Y-%m-%d', time.localtime()))
    # urltest = "http://erp.aicvs.cn/automaticOrdering/addShopBuy?erpShopId={}"
    url = "http://erp.aicvs.cn/automaticOrdering/addShopBuy?erpShopId={}"
    headers = {
        "Accept":"application/json",
        "Content-Type":"application/json"
    }

    for relate in relate_list:
        shopid = int(relate[0])
        erp_shopid = int(relate[1])
        orders = ai_sales_order.objects.filter(shopid=shopid).filter(create_date=create_date)

        order_data = []
        for one_order in orders:
            order_data.append({
                "upc":one_order.upc,
                "number":one_order.order_sale
            })
        json_info = json.dumps(order_data)
        print(json_info)
        data = bytes(json_info, 'utf8')
        request = urllib.request.Request(url=url.format(erp_shopid), data=data, headers=headers)

        response = urllib.request.urlopen(request)
        print(response.read().decode())

if __name__ == "__main__":
    order_commit([])