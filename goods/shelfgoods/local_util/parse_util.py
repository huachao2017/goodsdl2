# coding=utf8
import demjson

#对台账商品陈列 做转换
def parse_tz_display_goods(result):
    shelfs = list(demjson.decode(result))
    shelf_floor_upc = {}
    for shelf in shelfs:
        shelf = dict(shelf)
        shelfId = shelf['shelfId']
        layerArray = list(shelf["layerArray"])
        floor_num =  len(layerArray)
        floor = range(floor_num)
        floor_goods = {}
        for fl,fl_goods in zip(floor,layerArray):
            fl_num = int(floor_num-1-fl)
            fl_goods = list(fl_goods)
            upcs = []
            for good in fl_goods:
                good = dict(good)
                if "goods_upc" not in list(good.keys()) or "is_fitting" not in list(good.keys()) or "top" not in list(good.keys()) or "left" not in  list(good.keys()) or "width" not in list(good.keys()) or "height" not in list(good.keys()):
                    continue
                upc = good['goods_upc']
                is_fitting = 0
                if 'is_fitting' in list(good.keys()):
                    is_fitting = good['is_fitting'] #1 陈列盒  0 商品
                bottom, left, width, height = good['top'],good['left'],good['width'],good['height']
                upcs.append((upc,int(is_fitting),float(bottom), float(left), float(width), float(height)))
            if len(upcs) > 0 :
                floor_goods[fl_num] = upcs
        shelf_floor_upc[str(shelfId)] = floor_goods
    return shelf_floor_upc

# 对ai数据框做排序转换
def parse_ai_data(box_id,shelf_img_id,xmin,ymin,xmax,ymax,level):
    level_goods = {}
    for leveli in level:
        level_goods[leveli] = []
    for box_idi,shelf_img_idi,xmini,ymini,xmaxi,ymaxi,leveli in zip(box_id,shelf_img_id,xmin,ymin,xmax,ymax,level):
        level_goods[leveli].extend((xmini,ymini,xmaxi,ymaxi,box_idi,shelf_img_idi))
    return level_goods







if __name__=='__main__':
    result = '[{"shelfId":"FMG-004-001","layerArray":[[{"bottom":0,"left":507.679180887372,"width":74,"height":210,"goodsId":"27661","goods_upc":"6902538005141","name":"Z脉动蜜桃味600ml*","icon":"21581664"},{"bottom":17.406143344709896,"left":588.9078498293516,"width":65,"height":125,"goodsId":"20610","goods_upc":"6953392501010","name":"可口可乐330ml","icon":"21580303"}],[],[{"bottom":0,"left":58.020477815699664,"width":65,"height":230,"goodsId":"1667","goods_upc":"6921168509256","name":"Z农夫山泉水550ml*","icon":"21581293"},{"bottom":0,"left":826.7918088737201,"width":66,"height":210,"goodsId":"1576","goods_upc":"6924743915763","name":"Z乐事原味104g*","icon":"21580358"}],[{"bottom":0,"left":443.8566552901024,"width":204.99999999999997,"height":72,"goodsId":"2069","goods_upc":"84501446314","name":"康元椰子奶油饼干200g","icon":"21581377"},{"bottom":0,"left":229.18088737201367,"width":204.99999999999997,"height":72,"goodsId":"2069","goods_upc":"84501446314","name":"康元椰子奶油饼干200g","icon":"21581377"},{"bottom":0,"left":11.604095563139932,"width":204.99999999999997,"height":72,"goodsId":"2069","goods_upc":"84501446314","name":"康元椰子奶油饼干200g","icon":"21581377"},{"bottom":81.22866894197952,"left":11.604095563139932,"width":204.99999999999997,"height":72,"goodsId":"2069","goods_upc":"84501446314","name":"康元椰子奶油饼干200g","icon":"21581377"}]]},{"shelfId":"FMG-004-002","layerArray":[[],[],[],[{"bottom":0,"left":556.9965870307167,"width":74,"height":210,"goodsId":"1634","goods_upc":"6902538004045","name":"脉动青柠味600ml","icon":"21580925"}]]},{"shelfId":"FMG-004-003","layerArray":[[{"bottom":0,"left":359.7269624573379,"width":62,"height":243,"goodsId":"18322","goods_upc":"6909612113112","name":"可口可乐500ml","icon":"21579755"},{"bottom":0,"left":455.46075085324236,"width":150,"height":132,"goodsId":"20665","goods_upc":"6903252000979","name":"康师傅香辣牛肉桶面108g","icon":"21580662"},{"bottom":0,"left":644.0273037542662,"width":65,"height":125,"goodsId":"24154","goods_upc":"6954767441481","name":"芬达330ml","icon":"21580350"},{"bottom":0,"left":739.7610921501707,"width":65,"height":125,"goodsId":"24154","goods_upc":"6954767441481","name":"芬达330ml","icon":"21580350"},{"bottom":0,"left":37.71331058020478,"width":65,"height":210,"goodsId":"1618","goods_upc":"4891028705949","name":"Z维他柠檬茶500ml*","icon":"21581731"}],[{"bottom":0,"left":136.34812286689422,"width":63.99999999999999,"height":215,"goodsId":"17925","goods_upc":"6925303721398","name":"统一冰红茶","icon":"21580290"},{"bottom":0,"left":406.14334470989763,"width":66,"height":127.99999999999999,"goodsId":"1660","goods_upc":"6920180209601","name":"Z屈臣氏苏打水330ml*","icon":"21580777"},{"bottom":0,"left":574.4027303754266,"width":63.99999999999999,"height":215,"goodsId":"17925","goods_upc":"6925303721398","name":"统一冰红茶","icon":"21580290"}],[{"bottom":0,"left":110.23890784982936,"width":74,"height":210,"goodsId":"1634","goods_upc":"6902538004045","name":"脉动青柠味600ml","icon":"21580925"},{"bottom":0,"left":258.1911262798635,"width":150,"height":132,"goodsId":"18757","goods_upc":"6925303773106","name":"来一桶辣味老坛酸菜面125g","icon":"21580889"},{"bottom":0,"left":400.34129692832767,"width":150,"height":132,"goodsId":"18757","goods_upc":"6925303773106","name":"来一桶辣味老坛酸菜面125g","icon":"21580889"}],[{"bottom":0,"left":107.33788395904438,"width":74,"height":210,"goodsId":"1634","goods_upc":"6902538004045","name":"脉动青柠味600ml","icon":"21580925"},{"bottom":0,"left":200.17064846416383,"width":74,"height":210,"goodsId":"1634","goods_upc":"6902538004045","name":"脉动青柠味600ml","icon":"21580925"},{"bottom":0,"left":316.21160409556313,"width":120.00000000000001,"height":132,"goodsId":"113910649","goods_upc":"6917536014088","name":"合味道","icon":"120"},{"bottom":0,"left":519.283276450512,"width":200,"height":100,"goodsId":"113910663","goods_upc":"6917536014089","name":"果粒源","icon":"1"},{"bottom":0,"left":762.9692832764505,"width":65,"height":99,"goodsId":"113910674","goods_upc":"6917536014090","name":"黄桃","icon":"12"}]]}]'
    shelf_floor_upc = parse_tz_display_goods(result)
    print (shelf_floor_upc)