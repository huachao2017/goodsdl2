class Taizhang:
    tz_id=None
    shelfs = []
    associated_catids = None
    calculate_goods_array = [] # 每次计算完更新，李树

    twidth_to_goods = {}
    last_twidth = 0 # 每次计算完更新，李树

    def get_all_display_goods(self):
        """
        最后
        :return: goods列表
        """

        all_good_array = []
        for shelf in self.shelfs:
            for level in shelf.levels:
                for good in level.goods:
                    all_good_array.append(good)

        return all_good_array

    def __str__(self):
        """
        :return:
        shelf_id:xx
        [
            level_id:xx
            height:xx
            goods:[
            mch_goods_code:
            top:
            left:
            row:
            col:
            dep:
            ]
        ]
        """
        ret = ''
        for shelf in self.shelfs:
            ret += str(shelf.shelf_id)
            ret += '\n[\n'
            for level in shelf.levels:
                if level.isTrue:
                    ret += '\tlevel_id:{}\n'.format(level.level_id)
                    ret += '\theight:{}\n'.format(level.level_height)
                    ret += '\tgoods:[\n'
                    for good in level.goods:
                        ret += '\t\t{}-{},{},{}:[\n'.format(good.mch_good_code,good.width,good.height,good.depth)
                        for gooddisplay in good.gooddisplay_inss:
                            ret += '\t\ttop:{}\n'.format(gooddisplay.top)
                            ret += '\t\tleft:{}\n'.format(gooddisplay.left)
                            ret += '\t\trow:{}\n'.format(gooddisplay.row)
                            ret += '\t\tcol:{}\n'.format(gooddisplay.col)
                            ret += '\t\tdep:{}\n'.format(gooddisplay.dep)
                        ret += '\t\t]\n'
                ret += '\t]\n'
            ret += '\n]'

        return ret

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
                            "mch_good_code": good.mch_good_code,
                            "upc": good.upc,
                            "width":good.width,
                            "height":good.height,
                            "depth":good.depth,
                            "displays": []
                        }
                        json_level["goods"].append(json_goods)
                        for gooddisplay in good.gooddisplay_inss:
                            if gooddisplay.dep == 0:
                                json_display = {
                                    "top": gooddisplay.top,
                                    "left": gooddisplay.left,
                                    "row": gooddisplay.row,
                                    "col": gooddisplay.col,
                                }
                                json_goods["displays"].append(json_display)

        return json_ret
