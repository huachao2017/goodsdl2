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


