from django.db import connections

def init_data(tz_id, goods_data_list):
    taizhang = Taizhang()
    # TODO 获取数据
    return taizhang


class Taizhang:
    tz_id=None
    shelfs = []
    associated_catids = None

    candidate_goods_data_list = []

    def to_json(self):
        """
        :return:
        {
        taizhang_id:xx
        shelfs:[{
            shelf_id:xx
            levels:[{
                level_id:xx   #0是底层,1,2,3,4...
                height:xx
                hole_num:xx
                goods:[{
                    mch_goods_code:
                    upc:
                    width:
                    height:
                    depth:
                    displays:[{
                        top:
                        left:
                        row:
                        col:
                        },
                        {
                        ...
                        }]
                    },
                    {
                    ...
                    }]
                },
                {
                ...
                }]
            },
            {
            ...
            }]
        }
        """
        json_ret = {
            "taizhang_id":self.tz_id,
            "shelfs":[]
        }
        for shelf in self.shelfs:
            json_shelf={
                "shelf":shelf.shelf_id,
                "levels":[]
            }
            json_ret["shelfs"].append(json_shelf)
            for level in shelf.levels:
                if level.isTrue:
                    json_level = {
                        "level_id":level.level_id,
                        "height":level.level_height,
                        "goods":[]
                    }
                    json_shelf["levels"].append(json_level)
                    for good in level.goods:
                        json_goods = {
                            "mch_good_code": good.goods_data.mch_code,
                            "upc": good.goods_data.upc,
                            "width":good.goods_data.width,
                            "height":good.goods_data.height,
                            "depth":good.goods_data.depth,
                            "displays": []
                        }
                        json_level["goods"].append(json_goods)
                        # TODO
                        # for gooddisplay in good.gooddisplay_inss:
                        #     if gooddisplay.dep == 0:
                        #         json_display = {
                        #             "top": gooddisplay.top,
                        #             "left": gooddisplay.left,
                        #             "row": gooddisplay.row,
                        #             "col": gooddisplay.col,
                        #         }
                        #         json_goods["displays"].append(json_display)

        return json_ret

class Shelf:
    shelf_id = None
    width = None
    height = None
    depth = None
    levels = []
    badcase_value = 0

    def copy(self):
        shelf = Shelf()
        shelf.shelf_id = self.shelf_id
        shelf.width = self.width
        shelf.height = self.height
        shelf.depth = self.depth
        return shelf

    def assign(self, shelf):
        self.levels = shelf.levels
        self.badcase_value = shelf.badcase_value

class Level:
    level_id = None # 层id
    goods_list = []  # 商品集合
    level_none_good_width = None  # 层空余的宽度
    level_start_height = None  # 层相对货架的起始高度
    level_width = None  # 层宽度
    level_height = None  # 层高度
    level_depth = None  # 层深度

class DisplayGoods:
    #初始化数据
    goods_data = None

    #计算信息
    face_num = 1 # faces 数
    superimpose_rows = 1 # 叠放几行
